# NutriScope_SOK

**Bibliothèques:**  
global:
- pip install pandas
- pip install numpy
- pip install datetime
- pip install pyarrow
- pip install duckdb
- pip install python-dotenv
- pip install psycopg2-binary
- pip install dotenv
- pip install sqlalchemy

notebook:
- pip install humanize
- pip install matplotlib
- pip install pathlib
- pip install seaborn

**Installation:**  
Créer un fichier **.env** à la racine du projet.  
Copier le contenu de **.env.dist** dans **.env**  
Modifier les valeurs des variables d'environnement selon sa configuration locale

**Chargement du schema de la database**  
python -m src.command execute_sql

**Extraction des données / colonnes utiles depuis OFF**  
python -m src.command extract_off_data

**Extraction des nutriments**  
python -m src.command extract_nutriment_data

**Préparation des données**  
python -m src.command prepare_data

**Chargement des données en BDD**
python -m src.command load_data