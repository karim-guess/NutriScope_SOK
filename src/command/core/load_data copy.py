import os
import io
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import sys
from sqlalchemy import create_engine
from src.command.core.execution_timer import ExecutionTimer

class LoadData:
    NUTRIMENT_COLUMNS = ['energy', 'sugars', 'saturated_fat', 'salt', 'sodium', 'fiber', 'proteins', 'fruits_vegetables_legumes', 'fat']

    def __init__(self):
        self.source_parquet = os.getenv("PREPARE_OUTPUT_PARQUET_FILE")
        self.database_url = os.getenv("DATABASE_URL_USER")
        self.timer = ExecutionTimer()

    def get_dataframe(self) -> pd.DataFrame:
        self.timer.log_step("Lecture du fichier Parquet (PyArrow)")
        table = pq.read_table(self.source_parquet)
        df_final = table.to_pandas()
        print(f"-> Extraction terminée ! Total : {len(df_final)} lignes.")

        return df_final

    def _sanitize_text_column(self, df: pd.DataFrame, col_name: str) -> pd.DataFrame:
        """Nettoie une colonne de texte de manière vectorisée pour éviter les crashs de COPY."""
        if col_name in df.columns:
            df[col_name] = (df[col_name].astype(str)
                            .str.replace('\x00', '', regex=False)
                            .str.replace('\t', ' ', regex=False)
                            #.str.slice(0, 255)
                            )
            df[col_name] = df[col_name].replace({'None': None, 'nan': None, '': None})
        return df

    def load(self):
        df = self.get_dataframe()

        try:
            engine = create_engine(self.database_url)

            # 1. Nettoyage vectorisé des chaînes de texte critiques
            self.timer.log_step("Nettoyage et sanitisation des colonnes texte")
            df = self._sanitize_text_column(df, 'product_name')
            df = self._sanitize_text_column(df, 'categories_tags')
            df = self._sanitize_text_column(df, 'category_name')
            df = self._sanitize_text_column(df, 'brand_name')
            df = self._sanitize_text_column(df, 'brands_tags')
            for column in self.NUTRIMENT_COLUMNS:
                df = self._sanitize_text_column(df, column + '_unit')

            # 2. Isolation des dimensions uniques
            self.timer.log_step("Isolation des catégories et marques uniques")
            df_categories = df[['category_name']].dropna().drop_duplicates().rename(columns={'category_name': 'name'})
            df_brands = df[['brand_name', 'brands_tags']].dropna(subset=['brand_name']).drop_duplicates(subset=['brand_name']).rename(
                columns={'brand_name': 'name', 'brands_tags': 'tag'}
            )

            # 3. Traitement en BDD des dimensions (Insert + Récupération IDs)
            self.timer.log_step("Insertion et récupération des IDs de la table 'category'")
            map_category_ids = self.inserer_dimension_recuperer_ids(df_categories, 'category', ['name'], engine)
            
            self.timer.log_step("Insertion et récupération des IDs de la table 'brand'")
            map_brand_ids = self.inserer_dimension_recuperer_ids(df_brands, 'brand', ['name', 'tag'], engine)

            # 4. Association des clés étrangères sur les Produits
            self.timer.log_step("Mappage des IDs de catégories et de marques sur le DataFrame produit")
            df['category_id'] = df['category_name'].map(map_category_ids).astype('Int64')
            df['brand_id'] = df['brand_name'].map(map_brand_ids).astype('Int64')

            # 5. Sélection et renommage pour les produits
            df_produits_pret = df[[
                'code',
                'product_name',
                'nutriscore_score',
                'nutriscore_grade',
                'category_id',
                'brand_id'
            ]].rename(
                columns={'product_name': 'name'}
            )

            # 6. Bulk Copy des Produits ET récupération des nouveaux IDs de produits générés
            self.timer.log_step(f"Bulk Copy PostgreSQL de {len(df_produits_pret)} produits")
            map_product_ids = self.bulk_copy_produits_recuperer_ids(df_produits_pret, engine)

            # 7. Préparation du DataFrame Nutriment
            self.timer.log_step("Préparation du DataFrame 'nutriment'")
            df['product_id'] = df['code'].map(map_product_ids).astype('Int64')
            
            # On isole les nutriments en forçant le format numérique (REAL en BDD)
            nutriment_columns = ['product_id']
            for column in self.NUTRIMENT_COLUMNS:
                df[column] = pd.to_numeric(df[column], errors='coerce')
                nutriment_columns.append(column)
                nutriment_columns.append(column + '_unit')

            df_nutriments_pret = df[nutriment_columns].dropna(subset=['product_id'])

            # 8. Bulk Copy final des Nutriments
            self.timer.log_step(f"Bulk Copy PostgreSQL de {len(df_nutriments_pret)} nutriments")
            self.bulk_copy_nutriments(df_nutriments_pret, engine)

            engine.dispose()
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            sys.exit(1)

    def inserer_dimension_recuperer_ids(self, df_dim, table_name, columns, engine):
        """Insère les dimensions de manière dynamique en s'adaptant au nombre de colonnes (ex: avec ou sans tag)."""
        if df_dim.empty:
            return {}
        raw_conn = engine.raw_connection()
        try:
            with raw_conn.cursor() as cur:
                # 1. Génération dynamique des types pour la table temporaire
                temp_cols_definition = ", ".join([f"{col} TEXT" for col in columns])
                cur.execute(f"CREATE TEMP TABLE temp_{table_name} ({temp_cols_definition}) ON COMMIT DROP;")
                
                # Bulk COPY vers la table temporaire
                output = io.StringIO()
                df_dim[columns].to_csv(output, sep='\t', header=False, index=False, na_rep='')
                output.seek(0)
                
                cols_str = ", ".join(columns)
                cur.copy_expert(f"COPY temp_{table_name} ({cols_str}) FROM STDIN WITH CSV DELIMITER '\t' NULL ''", output)
                
                # 2. Insertion sélective dans la vraie table (basée uniquement sur le champ 'name' unique)
                query = f"""
                    INSERT INTO {table_name} ({cols_str})
                    SELECT DISTINCT {", ".join([f"t.{c}" for c in columns])} FROM temp_{table_name} t
                    LEFT JOIN {table_name} d ON d.name = t.name
                    WHERE d.name IS NULL
                    RETURNING id, name;
                """
                cur.execute(query)
                mapping_ids = {row[1]: row[0] for row in cur.fetchall()}
                
                # 3. Récupération des IDs qui existaient déjà en BDD
                liste_noms = [n for n in df_dim['name'] if n is not None]
                if liste_noms:
                    cur.execute(f"SELECT id, name FROM {table_name} WHERE name IN %s;", (tuple(liste_noms),))
                    for row in cur.fetchall():
                        mapping_ids[row[1]] = row[0]
                    
                raw_conn.commit()
                return mapping_ids
        finally:
            raw_conn.close()

    def bulk_copy_produits_recuperer_ids(self, df, engine):
        """Insère les produits à haute vitesse et retourne un dictionnaire {code: id_produit}."""
        raw_conn = engine.raw_connection()
        try:
            with raw_conn.cursor() as cur:
                # Table de transit temporaire pour capter les insertions sur gros volumes
                cur.execute("""CREATE TEMP TABLE temp_product (
                    code TEXT,
                    name TEXT,
                    nutriscore_score REAL,
                    nutriscore_grade VARCHAR(1),
                    category_id INT,
                    brand_id INT
                ) ON COMMIT DROP;""")
                
                output = io.StringIO()
                df.to_csv(output, sep='\t', header=False, index=False, na_rep='')
                output.seek(0)
                cur.copy_expert("COPY temp_product (code, name, nutriscore_score, nutriscore_grade, category_id, brand_id) FROM STDIN WITH CSV DELIMITER '\t' NULL ''", output)
                
                # Insertion finale + RETURNING pour mapper la relation enfant
                query = """
                    INSERT INTO product (code, name, nutriscore_score, nutriscore_grade, category_id, brand_id)
                    SELECT code, name, nutriscore_score, nutriscore_grade, category_id, brand_id FROM temp_product
                    RETURNING id, code;
                """
                cur.execute(query)
                map_product_ids = {row[1]: row[0] for row in cur.fetchall()}
                raw_conn.commit()
                return map_product_ids
        finally:
            raw_conn.close()

    def bulk_copy_nutriments(self, df, engine):
        """Envoi en bloc des nutriments associés aux produits."""
        output = io.StringIO()
        df.to_csv(output, sep='\t', header=False, index=False, na_rep='')
        output.seek(0)

        columns_to_string = ['product_id']
        for column in self.NUTRIMENT_COLUMNS:
            columns_to_string.append(column)
            columns_to_string.append(column + '_unit')

        raw_conn = engine.raw_connection()
        try:
            with raw_conn.cursor() as cur:
                sql_query = """COPY nutriment (
                    """ + ', '.join(columns_to_string) + """
                ) FROM STDIN WITH CSV DELIMITER \'\t\' NULL \'\'"""
                cur.copy_expert(sql=sql_query, file=output)
                raw_conn.commit()
                print(f"-> Insertion réussie de {len(df)} lignes de nutriments !")
        finally:
            raw_conn.close()

    def run(self) -> None:
        self.timer.log_start()
        self.load()
        self.timer.log_end(message="Chargement complet (avec nutriments) terminé avec succès")
