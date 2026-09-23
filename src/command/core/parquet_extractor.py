import os
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from src.command.core.execution_timer import ExecutionTimer

class ParquetExtractor:
    def __init__(self):
        self.batch_size = int(os.getenv("EXTRACT_BATCH_SIZE", "10000"))
        self.source_parquet = os.getenv("EXTRACT_SOURCE_PARQUET_FILE")
        self.output_parquet = os.getenv("EXTRACT_OUTPUT_PARQUET_FILE")

        columns = os.getenv("EXTRACT_SELECTED_COLUMNS")
        self.selected_columns = columns.split(",") if columns else None

        self.timer = ExecutionTimer()

    def extract(self) -> None:
        if not self.source_parquet or not self.output_parquet:
            print("Erreur : Les chemins source ou destination ne sont pas définis.")
            return

        source_file = Path(self.source_parquet)
        if not source_file.exists():
            print(f"Erreur : Le fichier source spécifié n'existe pas : '{source_file.resolve()}'")
            return

        self.timer.log_step(f"Début du traitement. Source : '{self.source_parquet}'")
        writer = None

        try:
            parquet_file = pq.ParquetFile(self.source_parquet)
            total_rows = parquet_file.metadata.num_rows
            self.timer.log_step(f"Fichier source analysé. Total de lignes à traiter : {total_rows:,}")
            self.timer.log_step(f"Lancement du streaming par blocs de {self.batch_size} lignes...")

            block_count = 0
            rows_processed = 0

            for batch in parquet_file.iter_batches(columns=self.selected_columns, batch_size=self.batch_size):
                table_chunk = pa.Table.from_batches([batch])

                if writer is None:
                    self.timer.log_step(f"Initialisation du fichier de sortie : '{self.output_parquet}'")
                    writer = pq.ParquetWriter(self.output_parquet, table_chunk.schema, compression='snappy')

                writer.write_table(table_chunk)

                block_count += 1
                rows_processed += batch.num_rows

                if block_count % 5 == 0 or rows_processed == total_rows:
                    self.timer.log_step(f"En cours : {rows_processed:,} / {total_rows:,} lignes traitées ({block_count} blocs).")

            self.timer.log_step("Fin de l'écriture. Finalisation du fichier...")

        except pa.ArrowInvalid as e:
            print(f"Erreur Arrow (Données corrompues ou colonnes introuvables) : {e}")
        except PermissionError:
            print(f"Erreur de permission : Impossible de lire '{self.source_parquet}' ou d'écrire '{self.output_parquet}'.")
        except Exception as e:
            print(f"Une erreur inattendue est survenue : {e}")
            
        finally:
            if writer:
                writer.close()

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
        
        self.timer.log_step("Extraction des colonnes choisies")
        self.extract()

        self.show_informations()
        
        self.timer.log_end(message="Extraction terminée avec succès")