# NutriScope_SOK

**Installation:**  
Créer un fichier **.env** à la racine du projet.  
Copier le contenu de **.env.dist** dans **.env**  
Modifier les valeurs des variables d'environnement selon sa configuration locale

**Chargement du schema de la database**  
```bash
python -m src.create_db
```

**Création du fichier CSV filtré**  
```bash
python -m src.filter_csv
```

**Import en BDD**  
```bash
python -m src.load_db
```

**Requêtes SQL de contôle**  
```bash
python -m src.control_query
```

**Lancement pipeline**
```bash
python -m src.pipeline
```

**Tests**
```bash
python -m pytest -q
python -m pytest -v tests/test_regles.py
python -m pytest -v -s tests/test_regles.py::test_typer_colonnes
```

**Génération notebooks/eda_reference.ipynb**
```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/eda_reference.ipynb
```