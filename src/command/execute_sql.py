import os
import sys
from sqlalchemy import create_engine, text

# Codes couleur ANSI pour la console
class Style:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log_info(message):
    print(f"{Style.BLUE}▶️  {message}{Style.END}")

def log_success(message):
    print(f"{Style.GREEN}✅ {message}{Style.END}")

def log_warn(message):
    print(f"{Style.YELLOW}⚠️  {message}{Style.END}")

def log_error(message):
    print(f"{Style.RED}{Style.BOLD}🚨 ERREUR : {message}{Style.END}", file=sys.stderr)

def run():
    database_url = os.getenv("DATABASE_URL_ADMIN")
    sql_file_path = os.getenv("SQL_FILE_BDD_OFF")
    
    if not database_url:
        log_error("La variable 'DATABASE_URL_ADMIN' est introuvable dans le fichier .env.")
        sys.exit(1)
        
    if not sql_file_path:
        log_error("La variable 'SQL_FILE_BDD_OFF' est introuvable dans le fichier .env.")
        sys.exit(1)

    # Vérification et lecture du fichier SQL
    if not os.path.exists(sql_file_path):
        log_error(f"Le fichier SQL est introuvable : '{sql_file_path}'")
        sys.exit(1)

    log_info(f"Fichier cible détecté : {sql_file_path}")

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        log_success("Fichier SQL lu avec succès.")
    except Exception as e:
        log_error(f"Impossible de lire le fichier SQL : {e}")
        sys.exit(1)

    # Initialisation du moteur SQLAlchemy
    log_info("Initialisation du moteur de base de données (SQLAlchemy)...")
    try:
        engine = create_engine(database_url)
    except Exception as e:
        log_error(f"Configuration de l'engine incorrecte : {e}")
        sys.exit(1)

    # Connexion et exécution de la transaction
    log_info("Ouverture de la connexion et exécution du script...")
    
    try:
        # Si une erreur survient, le Rollback est automatique à la sortie du bloc 'with'.
        # Si tout se passe bien, le Commit est automatique.
        with engine.begin() as connection:
            # SQLAlchemy requiert d'envelopper les chaînes SQL brutes dans la fonction text()
            connection.execute(text(sql_script))
            
        log_success("Toutes les requêtes ont été appliquées avec succès (Commit effectué).")

    except Exception as e:
        log_warn("L'exécution a échoué. Les modifications ont été annulées (Rollback).")
        log_error(f"Détails de l'erreur SQL : {e}")
        sys.exit(1)
        
    finally:
        # On ferme le pool de connexions proprement
        engine.dispose()
        log_info("Ressources de la base de données libérées.")
