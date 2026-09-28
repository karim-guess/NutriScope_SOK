import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import time
from src.constant import CSV_SELECTED_NUTRIMENT_COLUMNS, CSV_SELECTED_COLUMNS, CSV_SELECTED_CATEGORIES

load_dotenv()

CSV_SOURCE = os.getenv('CSV_FILE_ORIGIN')
CSV_FILTERED = os.getenv('CSV_FILE_FILTERED')
USECOLS = CSV_SELECTED_COLUMNS + CSV_SELECTED_NUTRIMENT_COLUMNS

"""
Lecture du CSV OFF original
"""
print(f'Début du chargement du CSV brut: {CSV_SOURCE}')
start_time = time.time()

chunk_iterator_csv = pd.read_csv(
    CSV_SOURCE,
    memory_map=True,
    skipinitialspace=True,
    sep="\t",
    chunksize=10000,
    low_memory = False,
    on_bad_lines="skip",
    usecols=USECOLS
)

full_data_csv = []

for chunk in chunk_iterator_csv:
    full_data_csv.append(chunk)

df_full_csv = pd.concat(full_data_csv, ignore_index=True)

print(f'CSV complet: {df_full_csv.shape[0]} lignes, {df_full_csv.shape[1]} colonnes')

"""
Filtrer sur produits vendus en France
"""
df_new_csv_fr = df_full_csv[df_full_csv["countries_tags"].str.contains("en:france")].copy()

print(f'CSV fltré FR : {df_new_csv_fr.shape[0]} lignes, {df_new_csv_fr.shape[1]} colonnes')

"""
Filtrer sur les rayon représentatifs
"""
# df_new_csv_categories = df_new_csv_fr[df_new_csv_fr["pnns_groups_1"].isin(CSV_SELECTED_CATEGORIES)].copy()
# print(f'CSV filtré catégories {CSV_SELECTED_CATEGORIES} : {df_new_csv_categories.shape[0]} lignes, {df_new_csv_categories.shape[1]} colonnes')
# df_new_csv = df_new_csv_categories.copy()
df_new_csv = df_new_csv_fr.copy()

"""
Création du nouveau CSV filtré
"""
print(f'Création du CSV filtré: {CSV_FILTERED}')
df_new_csv.to_csv(CSV_FILTERED, index=False)

execution_time = time.time() - start_time
minutes = int(execution_time // 60)
seconds = int(execution_time % 60)
print(f"Temps d'exécution total : {minutes} min {seconds} s (soit {execution_time:.2f} secondes).")