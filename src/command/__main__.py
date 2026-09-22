import sys
import importlib

def main():
    # Si l'utilisateur n'écrit rien après la commande
    if len(sys.argv) < 2:
        print("\033[1m Erreur : Vous devez spécifier une commande.\033[0m")
        print("\nCommandes disponibles :")
        print("  - execute_sql")
        print("  - extract_off_data")
        print("  - extract_nutriment_data")
        print("  - prepare_data")
        print("  - load_data")
        print("\nUsage : python -m src.command <nom_de_la_commande>")
        sys.exit(1)

    commande_nom = sys.argv[1]

    try:
        module = importlib.import_module(f"src.command.{commande_nom}")
        
        if hasattr(module, 'run'):
            module.run()
        else:
            print(f"\033[91m Erreur : La commande '{commande_nom}' n'a pas de fonction 'run()'.\033[0m")
            sys.exit(1)
            
    except ModuleNotFoundError as e:
        if f"src.command.{commande_nom}" in str(e):
            print(f"\033[91m Erreur : La commande '{commande_nom}' n'existe pas dans le dossier src/command.\033[0m")
        else:
            # Si le script existe mais qu'il lui manque une dépendance interne (ex: sqlalchemy)
            print(f"\033[91m Erreur d'importation dans la commande '{commande_nom}' : {e}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
