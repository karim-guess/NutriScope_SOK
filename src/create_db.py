import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_ADMIN")
SQL_FILE_PATH = os.getenv("SQL_FILE_BDD")

def execute(sql_file_path: str) -> None:
    if not DATABASE_URL:
        print("La variable 'DATABASE_URL_ADMIN' est introuvable dans le fichier .env.")
        sys.exit(1)
        
    if not sql_file_path:
        print("La variable 'SQL_FILE_BDD_OFF' est introuvable dans le fichier .env.")
        sys.exit(1)

    if not os.path.exists(sql_file_path):
        print(f"Le fichier SQL est introuvable : '{sql_file_path}'")
        sys.exit(1)

    print(f"Fichier cible détecté : {sql_file_path}")

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        print("Fichier SQL lu avec succès.")
    except Exception as e:
        print(f"Impossible de lire le fichier SQL : {e}")
        sys.exit(1)

    print("Initialisation du moteur de base de données (SQLAlchemy)...")
    try:
        engine = create_engine(DATABASE_URL)
    except Exception as e:
        print(f"Configuration de l'engine incorrecte : {e}")
        sys.exit(1)

    print("Ouverture de la connexion et exécution du script...")

    try:
        with engine.begin() as connection:
            connection.execute(text(sql_script))
            
        print("Toutes les requêtes ont été appliquées avec succès (Commit effectué).")

    except Exception as e:
        print("L'exécution a échoué. Les modifications ont été annulées (Rollback).")
        print(f"Détails de l'erreur SQL : {e}")
        sys.exit(1)
        
    finally:
        engine.dispose()
        print("Ressources de la base de données libérées.")


def main():
    execute(SQL_FILE_PATH)

if __name__ == "__main__":
    main()