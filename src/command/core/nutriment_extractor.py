import os
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import json
from src.command.core.execution_timer import ExecutionTimer

class NutrimentExtractor:
    def __init__(self):
        self.batch_size = int(os.getenv("EXTRACT_BATCH_SIZE", "10000"))
        self.source_parquet = os.getenv("EXTRACT_OUTPUT_PARQUET_FILE")
        self.output_parquet = os.getenv("EXTRACT_OUTPUT_NUTRIMENT_PARQUET_FILE")

        columns = os.getenv("EXTRACT_SELECTED_COLUMNS")
        self.selected_columns = columns.split(",") if columns else None

        nutriments_columns = os.getenv("NUTRIMENT_COLUMNS")
        self.nutriments_columns = nutriments_columns.split(",") if columns else None

        self.timer = ExecutionTimer()

    # TODO: convertir les valeurs dans les bonnes unités
    def process_nutriment_batch(self, batch: pa.RecordBatch, target_nutriments: list) -> pd.DataFrame:
        raw_cells = batch.column('nutriments').to_pylist()

        extracted_rows = []
        for cell in raw_cells:
            row_dict = {n: None for n in target_nutriments}
            
            if cell is None:
                extracted_rows.append(row_dict)
                continue
                
            items = json.loads(cell) if isinstance(cell, (str, bytes)) else cell
            
            if isinstance(items, list):
                for item in items:
                    name = item.get('name')
                    if name in target_nutriments:
                        row_dict[name] = item.get('100g')
                        row_dict[name + '_unit'] = item.get('unit')#TODO: lower case
                        
            extracted_rows.append(row_dict)

        return pd.DataFrame(extracted_rows)

    def extract(self) -> None:
        if not self.source_parquet or not self.output_parquet:
            print("Erreur : Les chemins source ou destination ne sont pas définis.")
            return
        
        base_columns = self.selected_columns.copy()
        base_columns.remove('nutriments')
        columns_to_load = self.selected_columns.copy()

        source_file = Path(self.source_parquet)
        if not source_file.exists():
            print(f"Erreur : Le fichier source spécifié n'existe pas : '{source_file.resolve()}'")
            return

        self.timer.log_step(f"Début du traitement. Source : '{self.source_parquet}'")

        try:
            parquet_file = pq.ParquetFile(self.source_parquet)
            total_rows = parquet_file.metadata.num_rows
            self.timer.log_step(f"Fichier source analysé. Total de lignes à traiter : {total_rows:,}")
            self.timer.log_step(f"Lancement du streaming par blocs de {self.batch_size} lignes...")

            block_count = 0
            rows_processed = 0

            all_chunks = []
            for batch in parquet_file.iter_batches(columns=columns_to_load, batch_size=self.batch_size):
                block_count += 1
                rows_processed += batch.num_rows
                
                if block_count % 5 == 0 or rows_processed == total_rows:
                    self.timer.log_step(f"En cours : {rows_processed:,} / {total_rows:,} lignes traitées ({block_count} blocs).")

                df_base_chunk = batch.select(base_columns).to_pandas()

                df_nutrients_chunk = self.process_nutriment_batch(batch, self.nutriments_columns)

                df_combined_chunk = pd.concat([df_base_chunk, df_nutrients_chunk], axis=1)
                all_chunks.append(df_combined_chunk)

            self.timer.log_step("Fin de l'écriture. Finalisation du fichier...")

        except pa.ArrowInvalid as e:
            print(f"Erreur Arrow (Données corrompues ou colonnes introuvables) : {e}")
        except PermissionError:
            print(f"Erreur de permission : Impossible de lire '{self.source_parquet}' ou d'écrire '{self.output_parquet}'.")
        except Exception as e:
            print(f"Une erreur inattendue est survenue : {e}")


        self.timer.log_step(f"Fin de l'écriture. Finalisation du fichier...")
        df_clean = pd.concat(all_chunks, ignore_index=True)
        self.timer.log_step(f"Préparation terminée ! Nombre total de lignes : {len(df_clean)}")

        self.timer.log_step(f"Écriture du nouveau DataFrame dans {self.output_parquet}...")
        try:
            table_to_save = pa.Table.from_pandas(df_clean)
            pq.write_table(table_to_save, self.output_parquet, compression='snappy')
        except Exception as e:
            print(f"Erreur lors de l'écriture du fichier de sortie '{self.output_parquet}' : {e}")
            raise

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
        
        self.timer.log_step("Extraction des nutriments")
        self.extract()

        self.show_informations()
        
        self.timer.log_end(message="Extraction terminée avec succès")