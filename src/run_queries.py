import os
import re
import duckdb

def to_markdown_table(df):
    """Génère un tableau Markdown sans dépendance externe à tabulate."""
    if df.empty:
        return "*Aucun résultat*\n"
    headers = list(df.columns)
    lines = ["| " + " | ".join(map(str, headers)) + " |",
             "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(val) if val is not None else "" for val in row) + " |")
    return "\n".join(lines)

def run_pipeline():
    con = duckdb.connect(database=':memory:')
    path_parquet = "data/parquet/produits/**/*.parquet"
    
    print(f"Création de la vue produits depuis : {path_parquet}")
    con.execute(f"CREATE VIEW produits AS SELECT * FROM read_parquet('{path_parquet}');")

    # Lecture et découpage du fichier SQL
    with open('./src/database/run_queries.sql', 'r', encoding='utf-8') as f:
        sql_text = f.read()
        
    queries = {}
    matches = re.findall(r'--\s*@nom:\s*(\w+)\s*\n([^;]+;)', sql_text)
    for name, query in matches:
        queries[name] = query.strip()
        
    os.makedirs('docs/data', exist_ok=True)
    output_markdown = 'docs/data/controle.md'
    
    with open(output_markdown, 'w', encoding='utf-8') as md:
        md.write('# Rapport de Contrôle Qualité\n\n')
        md.write('Ce rapport valide la cohérence des données issues du stockage Parquet partitionné.\n\n')
        
        for name, sql in queries.items():
            md.write(f'## {name}\n\n')
            try:
                # Exécution directe sous forme de DataFrame pandas
                df = con.execute(sql).df()
                md.write(to_markdown_table(df))
            except Exception as e:
                md.write(f'*Erreur lors de l\'exécution du contrôle {name} : {str(e)}*')
            md.write('\n\n')
            
    print(f"Pipeline terminé. Fichier généré : {output_markdown}")

if __name__ == '__main__':
    run_pipeline()
