import os
from pathlib import Path
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import numpy as np
from src.command.core.execution_timer import ExecutionTimer

class PrepareData:
    def __init__(self):
        self.batch_size = int(os.getenv("EXTRACT_BATCH_SIZE", "10000"))
        self.source_parquet = os.getenv("EXTRACT_OUTPUT_NUTRIMENT_PARQUET_FILE")
        self.output_parquet = os.getenv("PREPARE_OUTPUT_PARQUET_FILE")

        self.timer = ExecutionTimer()

    # TODO: prendre la meilleure ligne, supprimer les lignes code vide au cas où
    def prepare_code(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remplacer les chaînes vides ou espaces par des vrais NaN
        df['code'] = df['code'].replace(r'^\s*$', np.nan, regex=True)
        df = df.dropna(subset=['code'])

        df = df.drop_duplicates(subset=['code'])

        return df
    
    def prepare_product_name(self, df: pd.DataFrame) -> pd.DataFrame:
        df['bdd_product_name'] = [
            next((el.get('text') for el in liste if el.get('lang') == lang), None)
            or next((el.get('text') for el in liste if el.get('lang') == 'main'), None)
            for liste, lang in zip(df['product_name'], df['lang'])
        ]

        return df

    def prepare_nutriscore_grade(self, df: pd.DataFrame) -> pd.DataFrame:
        #NA, unknown, not-applicable
        to_delete = r'^\s*$|^na$|^unknown$|^not-applicable$'
        df['nutriscore_grade'] = (df['nutriscore_grade']
                                .astype(str)
                                .str.strip()
                                .replace(to_delete, np.nan, regex=True))

        df['nutriscore_grade'] = df['nutriscore_grade'].str.upper()

        return df

    # retirer les prefix en:... fr:..., supprimer les null
    def prepare_categories_tags(self, df: pd.DataFrame) -> pd.DataFrame:
        df['categories_tags'] = df['categories_tags'].apply(
            lambda x: ";".join([t.split(":")[-1] for t in x if t != "en:null"]) 
                if isinstance(x, (list, np.ndarray)) and len([t for t in x if t != "en:null"]) > 0 
                else np.nan
        )

        return df

    # retirer les prefix, applatir les listes tag séparés par ;
    def prepare_brands_tags(self, df: pd.DataFrame) -> pd.DataFrame:
        df['brands_tags'] = df['brands_tags'].apply(
            lambda x: np.nan if not isinstance(x, (list, np.ndarray)) or len([t for t in x if t and str(t).split(':')[-1] not in ['null', 'None', '']]) == 0 
            else ";".join([str(t).split(':')[-1] for t in x if t and str(t).split(':')[-1] not in ['null', 'None', '']])
        )

        return df

    # applatir la liste séparé par ;
    def prepare_countries_tags(self, df: pd.DataFrame) -> pd.DataFrame:
        df['countries_tags'] = df['countries_tags'].apply(
            lambda x: ";".join([str(i) for i in x.tolist()]) if isinstance(x, np.ndarray) or (pd.notna(x) if not isinstance(x, (list, np.ndarray)) else True) else None
        )

        return df

    def prepare(self) -> None:
        if not self.source_parquet or not self.output_parquet:
            print("Erreur : Les chemins source ou destination ne sont pas définis.")
            return
        
        source_file = Path(self.source_parquet)
        if not source_file.exists():
            print(f"Erreur : Le fichier source spécifié n'existe pas : '{source_file.resolve()}'")
            return
        
        df = self.get_dataframe(self.source_parquet, self.batch_size)

        self.timer.log_step("Préparation de product.code")
        df = self.prepare_code(df)

        self.timer.log_step("Préparation de product.countries")
        df = self.prepare_countries_tags(df)

        self.timer.log_step("Préparation de product.name")
        df = self.prepare_product_name(df)

        self.timer.log_step("Préparation de product.nutriscore_grade")
        df = self.prepare_nutriscore_grade(df)

        self.timer.log_step("Préparation de categories_tags")
        df = self.prepare_categories_tags(df)

        self.timer.log_step("Préparation de brands_tags")
        df = self.prepare_brands_tags(df)

        df_new = df[[
            'code',
            'bdd_product_name',
            'countries_tags',
            'nutriscore_score',
            'nutriscore_grade',
            'categories',
            'categories_tags',
            'brands',
            'brands_tags',
            'energy',
            'energy_unit',
            'sugars',
            'sugars_unit',
            'saturated-fat',
            'saturated-fat_unit',
            'salt',
            'salt_unit', 
            'sodium',
            'sodium_unit',
            'fiber',
            'fiber_unit',
            'proteins',
            'proteins_unit',
            'fruits-vegetables-legumes',
            'fruits-vegetables-legumes_unit',
            'fat',
            'fat_unit'
        ]].rename(
            columns={
                'bdd_product_name': 'product_name',
                'categories': 'category_name',
                'brands': 'brand_name',
                'saturated-fat': 'saturated_fat',
                'saturated-fat_unit': 'saturated_fat_unit',
                'fruits-vegetables-legumes': 'fruits_vegetables_legumes',
                'fruits-vegetables-legumes_unit': 'fruits_vegetables_legumes_unit'
            }
        ).copy()



        # Identifier les colonnes de type texte (object/string) dans votre DataFrame
        colonnes_texte = df_new.select_dtypes(include=['object', 'string']).columns

        # Remplacer le caractère nul (\x00) par du vide pour chaque colonne de texte
        for col in colonnes_texte:
            df_new[col] = df_new[col].astype(str).str.replace('\x00', '', regex=False)
            df_new[col] = df_new[col].astype(str).str.replace('\t', ' ', regex=False)



        self.timer.log_step(f"Écriture du nouveau DataFrame dans {self.output_parquet}...")
        try:
            df_new.to_parquet(self.output_parquet, index=False)
            # table_to_save = pa.Table.from_pandas(df)
            # pq.write_table(table_to_save, self.output_parquet, compression='snappy')
        except Exception as e:
            print(f"Erreur lors de l'écriture du fichier de sortie '{self.output_parquet}' : {e}")
            raise

    def get_dataframe(self, parquet_file_to_read: str, batch_size: int) -> pd.DataFrame:
        parquet_file = pq.ParquetFile(parquet_file_to_read)
        all_chunks = []

        print(f"Chargement du fichier par blocs de {batch_size} lignes...")

        for batch in parquet_file.iter_batches(batch_size=batch_size):
            df_chunk = batch.to_pandas()
            all_chunks.append(df_chunk)

        df_final = pd.concat(all_chunks, ignore_index=True)
        print(f"Extraction terminée ! Total : {len(df_final)} lignes.")

        return df_final

    def show_informations(self) -> None:
        if not self.output_parquet or not Path(self.output_parquet).exists():
            print("Impossible d'afficher les infos : le fichier de sortie n'existe pas.")
            return

        print("\n--- TYPES DES COLONNES ---")
        schema = pq.read_schema(self.output_parquet)
        for name, type_ in zip(schema.names, schema.types):
            print(f"{name:30} {type_}")

        print("\n--- DIMENSIONS ---")
        metadata = pq.read_metadata(self.output_parquet)
        print(f"Nombre de lignes   : {metadata.num_rows:,}")
        print(f"Nombre de colonnes : {len(schema)}")

        print("\n--- VALEURS MANQUANTES PAR COLONNE ---")
        for col in schema.names:
            col_table = pq.read_table(self.output_parquet, columns=[col])
            null_count = col_table.column(col).null_count
            print(f"{col:30} {null_count:,} valeurs manquantes")

    def run(self) -> None:
        self.timer.log_start()
        
        self.timer.log_step("Préparation des données")
        self.prepare()

        self.show_informations()

        self.timer.log_end(message="Préparation terminée avec succès")