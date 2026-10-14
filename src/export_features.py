#!/usr/bin/env python3
"""
Étape 5 — L'export d'entraînement figé
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


def main():
    parser = argparse.ArgumentParser(description="Export des features pour le Nutri-Score via DuckDB.")
    parser.add_argument("--input-dir", type=str, required=True, help="Répertoire racine du Parquet partitionné par rayon")
    parser.add_argument("--output-dir", type=str, default=".", help="Répertoire de sortie de l'export figé")
    parser.add_argument("--force", action="store_true", help="Forcer l'écrasement si le fichier existe déjà")
    args = parser.parse_args()

    # Configuration des noms de fichiers de sortie
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    parquet_filename = f"features_nutriscore_{today_str}.parquet"
    json_filename = "schema.json"
    
    parquet_path = os.path.join(args.output_dir, parquet_filename)
    json_path = os.path.join(args.output_dir, json_filename)

    # 1. Gestion du blocage sans option --force
    if os.path.exists(parquet_path) and not args.force:
        print(f"Erreur : Le fichier '{parquet_path}' existe déjà. Utilisez --force pour l'écrasement.", file=sys.stderr)
        sys.exit(1)

    # Définition du chemin de lecture avec le glob pattern pour les partitions de DuckDB
    # Comme DuckDB a partitionné par 'rayon', la colonne virtuelle 'rayon' est déduite du dossier
    input_pattern = os.path.join(args.input_dir, "**", "*.parquet")

    print(f"Traitement et filtrage des données depuis : {args.input_dir}")
    
    # 2. Requête DuckDB : Filtres de cohérence, création du rayon et calcul des ratios
    # Note : Le ratio d'énergie venant des lipides est basé sur : (fat_100g * 9) / energy-kcal_100g
    query = f"""
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
            nutriscore_grade
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
    """

    # Exécution et sauvegarde directe en Parquet via DuckDB (sans index)
    duckdb.execute(f"COPY ({query}) TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    # 3. Récupération des statistiques pour le schema.json via DuckDB
    print("Calcul des métadonnées et statistiques...")
    
    # Nombre de lignes total
    row_count = duckdb.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')").fetchone()[0]
    
    # Répartition de la cible
    target_res = duckdb.execute(f"""
        SELECT nutriscore_grade, ROUND(COUNT(*) * 1.0 / {row_count}, 4) 
        FROM read_parquet('{parquet_path}') 
        GROUP BY nutriscore_grade
    """).fetchall()
    target_distribution = {row[0]: row[1] for row in target_res}

    # Analyse des colonnes et des manquants (% de valeurs NULL)
    df_sample = duckdb.execute(f"SELECT * FROM read_parquet('{parquet_path}') LIMIT 1").df()
    columns_metadata = []

    for col in df_sample.columns:
        # Pourcentage de manquants
        missing_count = duckdb.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path}') WHERE \"{col}\" IS NULL").fetchone()[0]
        missing_pct = round((missing_count / row_count) * 100, 2)
        
        # Type natif DuckDB
        col_type = duckdb.execute(f"SELECT column_type FROM (DESCRIBE SELECT \"{col}\" FROM read_parquet('{parquet_path}'))").fetchone()[0]

        # Politique de manquants prévue pour le TP 14
        imputation_policy = "Aucune (Obligatoire)"
        if col in ['additives_n', 'nova_group']:
            imputation_policy = "Imputation par le mode (valeur la plus fréquente) ou la médiane"
            
        columns_metadata.append({
            "name": col,
            "type": str(col_type),
            "pct_missing": missing_pct,
            "imputation_policy_tp14": imputation_policy,
            "description": f"Variable représentant la colonne {col}"
        })

    # 4. Calcul de l'empreinte SHA-256
    sha256_val = compute_sha256(parquet_path)

    # 5. Création de schema.json
    schema_data = {
        "metadata": {
            "dataset_name": f"features_nutriscore_{today_str}",
            "freeze_date": datetime.datetime.now().isoformat(),
            "source": args.input_dir,
            "git_commit": get_git_commit(),
            "row_count": row_count,
            "sha256": sha256_val,
            "target": "nutriscore_grade",
            "identifier": "code",
            "licence": "ODbL",
            "intended_usage": "Entraînement et évaluation des modèles prédictifs Nutri-Score (TP 13 & 14)"
        },
        "applied_filters": [
            "nutriscore_grade valide (a à e)",
            "Présence des 7 nutriments obligatoires",
            "Cohérence physique : sucres <= glucides",
            "Cohérence physique : saturés <= lipides",
            "Cohérence physique : énergie > 0"
        ],
        "target_distribution": target_distribution,
        "columns": columns_metadata
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(schema_data, f, indent=4, ensure_ascii=False)

    print(f"Export terminé avec succès.\nFichier généré : {parquet_path}\nSHA-256 : {sha256_val}")


if __name__ == "__main__":
    main()
