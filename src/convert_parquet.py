import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import duckdb
import shutil
import json

load_dotenv()

CSV_SOURCE = os.getenv('CSV_FILE_FILTERED')
CSV_FILE_CLEAN = os.getenv('CSV_FILE_CLEAN')
CURRENT_PATH = Path(__file__).resolve().parent

def execute() -> None:
    sortie = Path("./data/parquet/produits/")
    if sortie.exists() and sortie.is_dir():
        shutil.rmtree(sortie)
    sortie.mkdir(parents=True, exist_ok=True)

    """
    ajout d'une colonne rayon = slug de pnns_groups_1 (unknown si vide), COPY ... TO ... (FORMAT PARQUET, PARTITION_BY (rayon), COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)
    """
    duckdb.execute(f"""
        COPY (
            SELECT *, 
                lower(regexp_replace(coalesce(pnns_groups_1, 'unknown'), '[^A-Za-z0-9]+', '-', 'g')) AS rayon
            FROM read_csv('{CSV_FILE_CLEAN}', nullstr=['', 'N/A'], header=True, types={{
                'code': 'VARCHAR',
                'energy-kcal_100g': 'FLOAT',
                'energy_100g': 'FLOAT',
                'fat_100g': 'FLOAT',
                'saturated-fat_100g': 'FLOAT',
                'carbohydrates_100g': 'FLOAT',
                'sugars_100g': 'FLOAT',
                'fiber_100g': 'FLOAT',
                'proteins_100g': 'FLOAT',
                'salt_100g': 'FLOAT',
                'sodium_100g': 'FLOAT',
                'fruits-vegetables-legumes_100g': 'FLOAT',
                'additives_n': 'SMALLINT',
                'nutriscore_score': 'SMALLINT',
                'nova_group': 'TINYINT',
                'created_t': 'TIMESTAMP',
                'last_modified_t': 'TIMESTAMP',
            }}, sample_size=-1)
        )
        TO '{sortie}' (FORMAT PARQUET, PARTITION_BY (rayon), COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)
    """)


    con = duckdb.connect()
    res_lignes = con.execute("SELECT count(*) FROM read_parquet('data/parquet/produits/**/*.parquet', hive_partitioning = true)").fetchone()
    print(f"Nombre de lignes : {res_lignes[0]:,}".replace(",", " "))

    chemin_sortie = Path("./data")
    fichier_schema = chemin_sortie / "schema_produits.json"

    schema_data = {
        "licence": "ODbL (Open Database License) - Open Food Facts",
        "nombre_de_lignes": res_lignes[0],
        "cle_de_partition": ["rayon"],
        "compression": "ZSTD",
        "colonnes": {
            "code": {
                "type": "VARCHAR",
                "justification": "Identifiant unique du produit (code-barres), stocké en texte pour conserver les zéros initiaux."
            },
            "created_t": {
                "type": "BIGINT",
                "justification": "Horodatage de création au format Unix Epoch numérique permettant un stockage binaire compact."
            },
            "last_modified_t": {
                "type": "BIGINT",
                "justification": "Horodatage de dernière modification au format Unix Epoch numérique permettant un stockage binaire compact."
            },
            "pnns_groups_1": {
                "type": "VARCHAR",
                "justification": "Groupe nutritionnel brut d'origine servant de base à la catégorisation du catalogue."
            },
            "rayon": {
                "type": "VARCHAR",
                "justification": "Clé de partition nettoyée en minuscules et sans caractères spéciaux générée à partir de pnns_groups_1."
            },
            "additives_n": {
                "type": "SMALLINT",
                "justification": "Nombre entier restreint comptabilisant les additifs détectés dans la recette du produit."
            },
            "nutriscore_score": {
                "type": "SMALLINT",
                "justification": "Score d'évaluation nutritionnelle brut allant de -15 à +40 servant à déterminer la note finale."
            },
            "nova_group": {
                "type": "TINYINT",
                "justification": "Classification du degré d'ultra-transformation des aliments codée de 1 à 4 sur un octet."
            },
            "energy_100g": {
                "type": "FLOAT",
                "justification": "Apport énergétique total exprimé en kilojoules (kJ) pour une portion de 100 grammes."
            },
            "energy-kcal_100g": {
                "type": "FLOAT",
                "justification": "Apport énergétique converti et exprimé en kilocalories (kcal) pour une portion de 100 grammes."
            },
            "fat_100g": {
                "type": "FLOAT",
                "justification": "Matières grasses globales en grammes mesurées pour 100 grammes de produit."
            },
            "saturated-fat_100g": {
                "type": "FLOAT",
                "justification": "Acides gras saturés en grammes pour 100 grammes, indicateur critique pour le profil nutritionnel."
            },
            "carbohydrates_100g": {
                "type": "FLOAT",
                "justification": "Teneur globale en glucides (sucres complexes et simples) en grammes pour 100 grammes."
            },
            "sugars_100g": {
                "type": "FLOAT",
                "justification": "Quantité spécifique de sucres simples en grammes pour 100 grammes, fortement pénalisée dans le calcul."
            },
            "fiber_100g": {
                "type": "FLOAT",
                "justification": "Teneur en fibres alimentaires en grammes pour 100 grammes, composante valorisée par l'algorithme."
            },
            "proteins_100g": {
                "type": "FLOAT",
                "justification": "Masse totale de protéines en grammes pour 100 grammes de produit fini."
            },
            "salt_100g": {
                "type": "FLOAT",
                "justification": "Équivalent en sel de cuisine calculé en grammes pour 100 grammes de produit."
            },
            "sodium_100g": {
                "type": "FLOAT",
                "justification": "Teneur en sodium pur en grammes pour 100 grammes servant de base légale au calcul du sel."
            },
            "fruits-vegetables-legumes_100g": {
                "type": "FLOAT",
                "justification": "Pourcentage de composants végétaux sains inclus pour bonifier le score nutritionnel global."
            }
        }
    }

    with open(fichier_schema, "w", encoding="utf-8") as f:
        json.dump(schema_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    execute()