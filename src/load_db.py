import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import time
from src.constant import CSV_SELECTED_NUTRIMENT_COLUMNS, CSV_SELECTED_COLUMNS, TEXT_TYPE, NUMERIC_TYPE

load_dotenv()

CSV_SOURCE = os.getenv('CSV_FILE_FILTERED')
DATABASE_URL = os.getenv("DATABASE_URL_USER")
NUMERIC = NUMERIC_TYPE + CSV_SELECTED_NUTRIMENT_COLUMNS

def load(table_name: str, df: pd.DataFrame) -> None:
    print(f'Insertion table {table_name}: {df.shape[0]} lignes, {df.shape[1]} colonnes')

    df = df.replace({np.nan: None})

    engine = create_engine(DATABASE_URL)

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False,
        chunksize=20000
    )

    engine.dispose()

def load_csv(csv_source: str) -> None:
    print(f'Chargement du CSV: {csv_source}')

    df = pd.read_csv(
        csv_source,
        dtype={c: "string" for c in TEXT_TYPE},
        converters={col: lambda val: pd.to_numeric(val, errors="coerce") for col in NUMERIC} # Force la conversion de type à cause d'erreur d'insertion en BDD
    )

    return df

def execute(df: pd.DataFrame) -> None:
    print('Début du chargement en BDD')
    start_time = time.time()

    df.insert(0, 'product_id', range(1, len(df) + 1))
    df_products = df[CSV_SELECTED_COLUMNS + ['product_id']].copy()

    """
    Marques
    """
    df_brands = df[['brands']].dropna(subset=['brands']).drop_duplicates(subset=['brands']).copy()
    df_brands.insert(0, 'brand_id', range(1, len(df_brands) + 1))

    """
    Catégories
    """
    df_categories = df[['main_category', 'categories_tags']].dropna(subset=['main_category']).drop_duplicates(subset=['main_category']).copy()
    df_categories.insert(0, 'category_id', range(1, len(df_categories) + 1))

    """
    Tags catégorie
    """
    df_categories_tags = df_categories[['category_id', 'categories_tags']].dropna(subset=['categories_tags']).copy()

    df_categories_tags['tags'] = df_categories_tags['categories_tags'].str.split(',')
    df_categories_tags = df_categories_tags.explode('tags').reset_index(drop=True)
    df_categories_tags = df_categories_tags.dropna(subset=['tags'])

    df_category_tag = df_categories_tags[['tags']].drop_duplicates().rename(columns={'tags': 'name'}).copy()
    df_category_tag.insert(0, 'id', range(1, len(df_category_tag) + 1))

    tag_map = dict(zip(df_category_tag['name'], df_category_tag['id']))

    df_categories_tags = pd.DataFrame({
        'category_id': df_categories_tags['category_id'],
        'category_tag_id': df_categories_tags['tags'].map(tag_map)
    }).copy()
    df_categories_tags.drop_duplicates(inplace=True)

    """
    Produits
    """
    df_merge_products_brands = pd.merge(
        df_products,
        df_brands[['brand_id', 'brands']],
        on='brands', 
        how='left'
    )

    df_categories.drop(columns='categories_tags')
    df_merge_products_categories = pd.merge(
        df_merge_products_brands, 
        df_categories[['category_id', 'main_category']],
        on='main_category', 
        how='left'
    )

    df_brands = df_brands.rename(columns={'brand_id': 'id', 'brands': 'name'}).copy()
    df_categories = df_categories[['category_id', 'main_category']].rename(columns={'category_id': 'id', 'main_category': 'name'}).copy()

    df_products = df_merge_products_categories[CSV_SELECTED_COLUMNS + ['product_id', 'brand_id', 'category_id']].rename(
        columns={
            'product_name': 'name',
            'product_id': 'id'
        }
    ).copy()

    """
    Nutriments
    """
    df_nutriments = df[['product_id'] + CSV_SELECTED_NUTRIMENT_COLUMNS].rename(
        columns={
            'energy-kcal_100g': 'energy_kcal_100g',
            'saturated-fat_100g': 'saturated_fat_100g',
            'fruits-vegetables-legumes_100g': 'fruits_vegetables_legumes_100g'
        }
    ).copy()


    load('category_tag', df_category_tag)

    load('category', df_categories)

    load('categories_tags', df_categories_tags)

    load('brand', df_brands)

    load('product', df_products)

    load('nutriment', df_nutriments)

    execution_time = time.time() - start_time
    minutes = int(execution_time // 60)
    seconds = int(execution_time % 60)
    print(f"Temps d'exécution total : {minutes} min {seconds} s (soit {execution_time:.2f} secondes).")

def main():
    df = load_csv(CSV_SOURCE)
    execute(df)

if __name__ == "__main__":
    main()