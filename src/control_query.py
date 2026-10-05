import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import CursorResult 
from dotenv import load_dotenv

load_dotenv()

TABLES_COUNT = ['product', 'nutriment', 'brand', 'category', 'category_tag', 'categories_tags']
DATABASE_URL = os.getenv("DATABASE_URL_USER")

def execute_query(query: str) -> CursorResult:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        query = text(query)
        
        return connection.execute(query)

    engine.dispose()

def execute() -> None:
    print('\n---- VOLUMETRIE ----')
    for table in TABLES_COUNT:
        result = execute_query(f"SELECT COUNT(*) FROM {table}")
        count = result.scalar()
        print(f"Total table \"{table}\" : {count}")

    print('\n---- PRODUITS SANS CATEGORIES ----')
    result = execute_query("SELECT COUNT(*) FROM product WHERE category_id IS NULL")
    count = result.scalar()
    print(f"Total : {count}")

    print('\n---- TOP 10 MARQUES ----')
    result = execute_query("""
        SELECT
            b.id AS brand_id,
            b.name,
            COUNT(p.id) AS total_products
        FROM
            brand b
        INNER JOIN
            product p ON b.id = p.brand_id
        WHERE
            b.name IS NOT NULL
            AND TRIM(b.name) != ''
        GROUP BY
            b.id
        ORDER BY
            total_products DESC
        LIMIT 10
    """).fetchall()
    for row in result:
        print(f"{row[1]}: {row[2]}")

    print('\n ---- COMPLÉTUDE NUTRISCORE PAR RAYON ----')
    result = execute_query("""
        SELECT
            COALESCE(pnns_groups_1, 'Rayon inconnu') AS rayon,
            COUNT(id) AS total_products,
            COUNT(nutriscore_grade) AS products_with_nutriscore,
            COALESCE(
                ROUND(
                    (COUNT(nutriscore_grade) * 100.0) / NULLIF(COUNT(id), 0),
                    4
                ),
                0.0000
            ) AS completeness_percentage
        FROM
            product
        GROUP BY
            pnns_groups_1
        ORDER BY
            completeness_percentage DESC, total_products DESC
    """).fetchall()

    for row in result:
        print(
            f"# Rayon: {row[0]}\n",
            f"\tNbre de produits: {row[1]}\n",
            f"\tProduit avec NS: {row[2]}\n",
            f"\tComplétude: {row[3]}%"
        )


    print('\n ---- DOUBLONS CODE RESTANTS ----')
    result = execute_query("""
        SELECT 
            code, 
            COUNT(*) AS nombre_de_doublons
        FROM 
            product
        GROUP BY 
            code
        HAVING 
            COUNT(*) > 1
        ORDER BY 
            nombre_de_doublons DESC
    """).fetchall()
    if result:
        for row in result:
            print(f"{row[0]} : {row[1]}")
    else:
        print("Aucun doublon trouvé : 0")

if __name__ == "__main__":
    execute()