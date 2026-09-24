import os
import pandas as pd
from dotenv import load_dotenv
import time

load_dotenv()

csv_source = os.getenv('CSV_FILE_ORIGIN')
csv_filtered = os.getenv('CSV_FILE_FILTERED')
base_cols = os.getenv('CSV_SELECTED_COLUMNS').replace(",", " ").split()
ingredients_columns = os.getenv('CSV_SELECTED_NUTRIMENT_COLUMNS').replace(",", " ").split()
usecols = base_cols + ingredients_columns

"""
Lecture du CSV OFF original
"""
print(f'Début du chargement du CSV brut: {csv_source}')
start_time = time.time()

chunk_iterator_csv = pd.read_csv(
    csv_source,
    memory_map=True,
    skipinitialspace=True,
    sep="\t",
    chunksize=10000,
    low_memory = False,
    on_bad_lines="skip",
    usecols=usecols
)

full_data_csv = []

for chunk in chunk_iterator_csv:
    full_data_csv.append(chunk)

df_full_csv = pd.concat(full_data_csv, ignore_index=True)

print(f'{df_full_csv.shape[0]} lignes, {df_full_csv.shape[1]} colonnes')

"""
Filtrer sur produits vendus en France
"""
df_new_csv = df_full_csv[df_full_csv["countries_tags"].str.contains("en:france")].copy()

print(f'{df_new_csv.shape[0]} lignes, {df_new_csv.shape[1]} colonnes')

"""
Création du nouveau CSV filtré
"""
print(f'Création du CSV filtré: {csv_filtered}')
df_new_csv.to_csv(csv_filtered, index=False)

execution_time = time.time() - start_time
minutes = int(execution_time // 60)
seconds = int(execution_time % 60)
print(f"Temps d'exécution total : {minutes} min {seconds} s (soit {execution_time:.2f} secondes).")