import os
import re
import duckdb
import pandas as pd
import argparse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_USER")

TYPE_PGSL = 'pgsql'
TYPE_PARQUET = 'parquet'

def to_markdown_table(df: pd.DataFrame) -> str:
    """Génère un tableau Markdown."""
    if df.empty:
        return "*Aucun résultat*\n"
    headers = list(df.columns)
    lines = ["| " + " | ".join(map(str, headers)) + " |",
             "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(val) if val is not None else "" for val in row) + " |")

    return "\n".join(lines)

def con_pgsql() -> tuple:
    engine = create_engine(DATABASE_URL)
    con = engine.connect()
    sql_file = './src/database/run_queries_pgsql.sql'
    control_file = 'controle_pgsql.md'

    return con, sql_file, control_file

def con_parquet() -> tuple:
    con = duckdb.connect(database=':memory:')
    sql_file = './src/database/run_queries.sql'
    control_file = 'controle_parquet.md'

    path_parquet = "data/parquet/produits/**/*.parquet"
    
    print(f"Création de la vue produits depuis : {path_parquet}")
    con.execute(f"CREATE VIEW produits AS SELECT * FROM read_parquet('{path_parquet}');")

    return con, sql_file, control_file

def execute_queries(con_type: str = TYPE_PGSL) -> None:
    if con_type == TYPE_PARQUET:
        con, sql_file, control_file = con_parquet()
    if con_type == TYPE_PGSL:
        con, sql_file, control_file = con_pgsql()

    # Lecture et découpage du fichier SQL
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_text = f.read()

    os.makedirs('docs/data', exist_ok=True)
    output_markdown = 'docs/data/' + control_file
        
    queries = {}
    matches = re.findall(r'--\s*@nom:\s*(\w+)\s*\n([^;]+;)', sql_text)
    for name, query in matches:
        queries[name] = query.strip()

    with open(output_markdown, 'w', encoding='utf-8') as md:
        md.write('# Rapport de Contrôle Qualité\n\n')
        
        for name, sql in queries.items():
            md.write(f'## {name}\n\n')
            try:
                if con_type == 'parquet':
                    df = con.execute(sql).df()
                if con_type == 'pgsql':
                    result = con.execute(text(sql))
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())

                md.write(to_markdown_table(df))
            except Exception as e:
                md.write(f'*Erreur lors de l\'exécution du contrôle {name} : {str(e)}*')
            md.write('\n\n')
            
    print(f"Fichier généré : {output_markdown}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Exécution des requêtes de contrôle qualité.")
    parser.add_argument(
        "--con", 
        type=str, 
        default=TYPE_PGSL, 
        choices=[TYPE_PGSL, TYPE_PARQUET],
        help="Type de connexion / source de données (pgsql ou parquet)"
    )
    args = parser.parse_args()

    execute_queries(args.con)
