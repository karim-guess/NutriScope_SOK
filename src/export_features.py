#!/usr/bin/env python3
"""
Phase 4 — L'export d'entraînement figé
Fichier : export_features.py
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import subprocess
import duckdb
from src.constant import STRATEGIE_PAR_DEFAUT


def get_git_commit():
    """Récupère le hash du commit Git actuel."""
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "unknown"

def compute_sha256(filepath):
    """Calcule l'empreinte SHA-256 d'un fichier."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def execute():
    parser = argparse.ArgumentParser(description="Export des features et split stratifié figé pour le Nutri-Score.")
    parser.add_argument("--input-dir", type=str, default="./data/parquet/produits", help="Répertoire racine du Parquet partitionné par rayon")
    parser.add_argument("--output-dir", type=str, default="./data/exports", help="Répertoire de sortie de l'export figé")
    parser.add_argument("--force", action="store_true", help="Forcer l'écrasement si le fichier existe déjà")
    args = parser.parse_args()

    SEED = 42
    TEST_RATIO = 0.20
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    
    parquet_filename = f"features_nutriscore_{today_str}.parquet"
    json_filename = "schema.json"
    
    parquet_path = os.path.join(args.output_dir, parquet_filename)
    json_path = os.path.join(args.output_dir, json_filename)

    # Protection contre l'écrasement silencieux
    if os.path.exists(parquet_path) and not args.force:
        print(f"Erreur : Le fichier '{parquet_path}' existe déjà. Utilisez --force pour forcer.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    # Normalisation des chemins pour DuckDB (Windows/Linux compatibility)
    input_pattern = os.path.join(args.input_dir, "**", "*.parquet").replace("\\", "/")
    parquet_path_clean = parquet_path.replace("\\", "/")

    print(f"Extraction, filtrage et stratification déterministe (seed={SEED})...")
    
    # Requête DuckDB : Tri déterministe par Hash pour assurer la même affectation produit par produit
    query = f"""
        WITH filtered_data AS (
            SELECT 
                code,
                rayon,
                "energy-kcal_100g",
                fat_100g,
                "saturated-fat_100g",
                carbohydrates_100g,
                sugars_100g,
                proteins_100g,
                salt_100g,
                additives_n,
                nova_group,
                COALESCE(sugars_100g / NULLIF(carbohydrates_100g, 0), 0.0) AS ratio_sugar_carbs,
                COALESCE("saturated-fat_100g" / NULLIF(fat_100g, 0), 0.0) AS ratio_sat_fat,
                COALESCE((fat_100g * 9.0) / NULLIF("energy-kcal_100g", 0), 0.0) AS ratio_energy_fat,
                nutriscore_score,
                lower(nutriscore_grade) AS nutriscore_grade,
                -- Stratification déterministe par hachage de la clé unique 'code'
                ROW_NUMBER() OVER (
                    PARTITION BY lower(nutriscore_grade) 
                    ORDER BY hash(code || '{SEED}')
                ) AS row_num,
                COUNT(*) OVER (PARTITION BY lower(nutriscore_grade)) AS group_count
            FROM read_parquet('{input_pattern}', hive_partitioning=True)
            WHERE 
                lower(nutriscore_grade) IN ('a', 'b', 'c', 'd', 'e')
                AND "energy-kcal_100g" IS NOT NULL
                AND fat_100g IS NOT NULL
                AND "saturated-fat_100g" IS NOT NULL
                AND carbohydrates_100g IS NOT NULL
                AND sugars_100g IS NOT NULL
                AND proteins_100g IS NOT NULL
                AND salt_100g IS NOT NULL
                AND sugars_100g <= carbohydrates_100g
                AND "saturated-fat_100g" <= fat_100g
                AND "energy-kcal_100g" > 0
        )
        SELECT 
            code, rayon, "energy-kcal_100g", fat_100g, "saturated-fat_100g",
            carbohydrates_100g, sugars_100g, proteins_100g, salt_100g,
            additives_n, nova_group, ratio_sugar_carbs, ratio_sat_fat, ratio_energy_fat,
            nutriscore_score, nutriscore_grade,
            CASE 
                WHEN row_num <= (group_count * {TEST_RATIO}) THEN 'test'
                ELSE 'train'
            END AS split
        FROM filtered_data
        ORDER BY code ASC  -- Ordre final figé pour l'empreinte SHA-256
    """

    duckdb.execute(f"COPY ({query}) TO '{parquet_path_clean}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    # Récupération des effectifs précis pour le schema.json
    row_count = duckdb.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path_clean}')").fetchone()[0]
    
    counts_res = duckdb.execute(f"""
        SELECT 
            nutriscore_grade,
            COUNT(CASE WHEN split = 'train' THEN 1 END) AS train_count,
            COUNT(CASE WHEN split = 'test' THEN 1 END) AS test_count
        FROM read_parquet('{parquet_path_clean}')
        GROUP BY nutriscore_grade
        ORDER BY nutriscore_grade
    """).fetchall()

    split_distribution = {
        grade: {"train": train_c, "test": test_c, "pct_test": round(test_c / (train_c + test_c), 4)}
        for grade, train_c, test_c in counts_res
    }

    # Analyse des colonnes
    df_sample = duckdb.execute(f"SELECT * FROM read_parquet('{parquet_path_clean}') LIMIT 1").df()
    columns_metadata = []
    for col in df_sample.columns:
        missing_count = duckdb.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path_clean}') WHERE \"{col}\" IS NULL").fetchone()[0]
        missing_pct = round((missing_count / row_count) * 100, 2)
        col_type = duckdb.execute(f"SELECT column_type FROM (DESCRIBE SELECT \"{col}\" FROM read_parquet('{parquet_path_clean}'))").fetchone()[0]
        
        columns_metadata.append({
            "name": col,
            "type": str(col_type),
            "pct_missing": missing_pct,
            "imputation_policy": STRATEGIE_PAR_DEFAUT.get(col, 'aucune')
        })

    sha256_val = compute_sha256(parquet_path)

    # Construction du schema.json avec règles d'usages explicites
    schema_data = {
        "metadata": {
            "dataset_name": f"features_nutriscore_{today_str}",
            "freeze_date": datetime.datetime.now().isoformat(),
            "source": args.input_dir,
            "git_commit": get_git_commit(),
            "row_count": row_count,
            "sha256": sha256_val,
            "target": "nutriscore_grade",
            "identifier": "code"
        },
        "split_method": {
            "type": "Stratified Split par Hachage Déterministe",
            "random_seed": SEED,
            "test_ratio": TEST_RATIO,
            "justification": "Les grades a et b étant minoritaires, la stratification empêche le sous-échantillonnage critique dans le jeu de test. Le hachage garantit la stabilité produit par produit.",
            "strict_rules_of_engagement": "1. FIT (entraînement, imputations, encodages) sur le groupe 'train' UNIQUEMENT. 2. La validation croisée (tuning hyperparamètres) s'effectue exclusivement à l'intérieur du bloc 'train'. 3. Le bloc 'test' ne doit être lu et prédit qu'UNE SEULE FOIS, tout à la fin, pour sortir les métriques finales."
        },
        "applied_filters": [
            "nutriscore_grade IN (a,b,c,d,e)",
            "7 nutriments requis non nuls",
            "Coherences: sucres <= glucides, sat <= lipides, energie > 0"
        ],
        "split_counts_by_grade": split_distribution,
        "columns": columns_metadata
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(schema_data, f, indent=4, ensure_ascii=False)

    print(f"Succès. SHA-256 gravé : {sha256_val}")

def test():
    json_path = "data/exports/schema.json"
    with open(json_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    print("=== ÉTAPE 1 : Vérification de la stratification par Grade ===")
    distributions = schema["split_counts_by_grade"]
    all_around_20 = True
    
    for grade, stats in distributions.items():
        pct = stats["pct_test"] * 100
        print(f"Grade {grade.upper()} : {stats['train']} train | {stats['test']} test -> part de test : {pct:.2f}%")
        # Tolérance infime liée aux arrondis de division entière sur de faibles effectifs
        if not (19.0 <= pct <= 21.0):
            all_around_20 = False
            
    if all_around_20:
        print("-> [OK] Stratification validée : chaque grade possède ~20% de données en test.")
    else:
        print("-> [ÉCHEC] Écart de stratification détecté sur un ou plusieurs grades.")


if __name__ == "__main__":
    execute()
    # test()
