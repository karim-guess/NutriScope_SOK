"""
enchaîne lecture → règles → rapport → base ; le journal indique les volumes par table.
"""
import os
import pandas as pd
from dotenv import load_dotenv
import time
from src.cleaning import CompteRendu, nettoyer, generer_rapport
from src.constant import CSV_SELECTED_NUTRIMENT_COLUMNS, TEXT_TYPE, NUMERIC_TYPE
from src.create_db import execute as execute_create
from src.load_db import execute as execute_load
from src.control_query import execute as execute_control

load_dotenv()

CSV_SOURCE = os.getenv('CSV_FILE_FILTERED')
SQL_FILE_BDD = os.getenv("SQL_FILE_BDD_PIPELINE")
NUMERIC = NUMERIC_TYPE + CSV_SELECTED_NUTRIMENT_COLUMNS


print('Lancement pipeline')
start_time = time.time()

print('Chargement du CSV filtré')
df = pd.read_csv(
    CSV_SOURCE,
    dtype={c: "string" for c in TEXT_TYPE},
    converters={col: lambda val: pd.to_numeric(val, errors="coerce") for col in NUMERIC},
)

print('Application des règles')
df_new, cr_list = nettoyer(df)

print('Génération du rapport')
generer_rapport(df, df_new, cr_list, './docs/data/rapport_nettoyage.md')

print('Création tables BDD')
execute_create(SQL_FILE_BDD)

print('Chargement en BDD')
execute_load(df_new, True)

print('Requêtes de contrôle:')
execute_control()


execution_time = time.time() - start_time
minutes = int(execution_time // 60)
seconds = int(execution_time % 60)
print(f"Temps d'exécution total : {minutes} min {seconds} s (soit {execution_time:.2f} secondes).")
