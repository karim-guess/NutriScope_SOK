import os
import io
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import sys
from sqlalchemy import create_engine
from src.command.core.execution_timer import ExecutionTimer

class LoadData:
    def __init__(self):
        self.source_parquet = os.getenv("PREPARE_OUTPUT_PARQUET_FILE")
        self.database_url = os.getenv("DATABASE_URL_ADMIN")
        columns = os.getenv("NUTRIMENT_COLUMNS")
        self.nutriments_columns = columns.split(",") if columns else None
        self.timer = ExecutionTimer()

    def get_dataframe(self) -> pd.DataFrame:
        self.timer.log_step("Lecture du fichier Parquet")
        table = pq.read_table(self.source_parquet)
        df_final = table.to_pandas()
        self.timer.log_step(f"-> Extraction terminée ! Total : {len(df_final)} lignes.")

        return df_final

    def prepare(self) -> None:
        try:
            df = self.get_dataframe()

            nutriments_columns = [
                sub_col 
                for col in self.nutriments_columns
                for sub_col in (col, col + '_unit')
            ]

            self.timer.log_step(f"Préparation des données...")

            # PRODUCTS
            product_base_cols = ['code', 'product_name', 'countries_tags', 'nutriscore_score', 'nutriscore_grade', 'category_name', 'brand_name']
            df_products = df[product_base_cols + nutriments_columns].copy()

            df_products.insert(0, 'id', range(1, len(df_products) + 1))
            df_products.rename(columns={'product_name': 'name'}, inplace=True)

            # NUTRIMENTS
            df_nutriments_final = df_products[['id'] + nutriments_columns].rename(
                columns={'id': 'product_id'}
            )

            # CATEGORIES
            df_categories = df[['category_name', 'categories_tags']].dropna(subset=['category_name']).drop_duplicates(subset=['category_name']).copy()
            df_categories.insert(0, 'id', range(1, len(df_categories) + 1))

            # CATEGORIES_TAGS
            df_categories_tags = df_categories[['id', 'categories_tags']].dropna(subset=['categories_tags']).copy()

            df_categories_tags['tags'] = df_categories_tags['categories_tags'].str.split(';')
            df_categories_tags = df_categories_tags.explode('tags').reset_index(drop=True)

            df_categories_tags = df_categories_tags.dropna(subset=['tags'])

            df_category_tag_final = df_categories_tags[['tags']].drop_duplicates().rename(columns={'tags': 'name'}).copy()
            df_category_tag_final.insert(0, 'id', range(1, len(df_category_tag_final) + 1))

            tag_map = dict(zip(df_category_tag_final['name'], df_category_tag_final['id']))

            df_categories_tags_final = pd.DataFrame({
                'category_id': df_categories_tags['id'],
                'category_tag_id': df_categories_tags['tags'].map(tag_map)
            })
            df_categories_tags_final.drop_duplicates(inplace=True)

            df_products_clean = df_products.drop(columns=nutriments_columns)

            # BRANDS
            df_brands = df[['brand_name', 'brands_tags']].dropna(subset=['brand_name']).drop_duplicates(subset=['brand_name']).copy()
            df_brands.insert(0, 'id', range(1, len(df_brands) + 1))

            df_brands_final = df_brands.rename(
                columns={
                    'brand_name': 'name',
                    'brands_tags': 'tags'
                }
            )

            # RELATIONS PRODUCT -> CATEGORY, PRODUCT -> BRAND
            df_merge_products_brands = pd.merge(
                df_products_clean.rename(columns={'id': 'product_id'}), 
                df_brands[['id', 'brand_name']].rename(columns={'id': 'brand_id'}),
                on='brand_name', 
                how='left'
            )

            df_merge_products_categories = pd.merge(
                df_merge_products_brands,
                df_categories[['id', 'category_name']].rename(columns={'id': 'category_id'}),
                on='category_name', 
                how='left'
            )

            df_categories_final = df_categories[['id', 'category_name']].rename(
                columns={
                    'category_name': 'name'
                }
            )

            df_products_final = df_merge_products_categories[[
                'product_id', 'code', 'name', 'countries_tags', 'nutriscore_score', 'nutriscore_grade', 'category_id', 'brand_id'
            ]].rename(
                columns={
                    'product_id': 'id',
                    'countries_tags': 'countries'
                }
            )

            self.timer.log_step(f"Insertion des marques ! Total : {len(df_brands_final)} lignes.")
            self.load('brand', df_brands_final)

            self.timer.log_step(f"Insertion des tags categorie ! Total : {len(df_category_tag_final)} lignes.")
            self.load('category_tag', df_category_tag_final)

            self.timer.log_step(f"Insertion des categories ! Total : {len(df_categories_final)} lignes.")
            self.load('category', df_categories_final)

            self.timer.log_step(f"Insertion des relations tags / categories ! Total : {len(df_categories_tags_final)} lignes.")
            self.load('categories_tags', df_categories_tags_final)

            self.timer.log_step(f"Insertion des produits ! Total : {len(df_products_final)} lignes.")
            self.load('product', df_products_final)

            self.timer.log_step(f"Insertion des nutriments ! Total : {len(df_nutriments_final)} lignes.")
            self.load('nutriment', df_nutriments_final)
            
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            sys.exit(1)

    def load(self, table_name: str, df: pd.DataFrame) -> None:
        engine = create_engine(self.database_url)

        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False,
            chunksize=20000
        )

        engine.dispose()

    def run(self) -> None:
        self.timer.log_start()
        self.prepare()
        self.timer.log_end(message="Chargement des données terminé avec succès")
