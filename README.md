# NutriScope_SOK

**Installation:**  
Créer un fichier **.env** à la racine du projet.  
Copier le contenu de **.env.dist** dans **.env**  
Modifier les valeurs des variables d'environnement selon sa configuration locale

```bash
pip install -r requirements.txt
```

**Création du fichier CSV filtré**  
```bash
python -m src.filter_csv
```

**Chargement du schema de la database**  
```bash
python -m src.create_db
```

**Import en BDD**  
```bash
python -m src.load_db
```

**Requêtes de contôle PGSQL**  
```bash
python -m src.run_queries --con pgsql
```

**Lancement pipeline**
```bash
python -m src.pipeline
```

**Génération notebooks/eda_reference.ipynb**
```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/eda_reference.ipynb
```

**Conversion parquet**
```bash
python -m src.convert_parquet
```

**Requêtes de contrôle .parquet**
```bash
python -m src.run_queries --con parquet
```

**Export features**
```bash
python -m src.export_features --input-dir ./data/parquet/produits --output-dir ./data/exports --force
```

**Création du modèle**
```bash
python -m src.train_model --input-file ./data/exports/features_nutriscore_20261014.parquet --model-dir ./models
```


**Tests**
```bash
python -m pytest -q
python -m pytest -v tests/test_regles.py
python -m pytest -v -s tests/test_regles.py::test_typer_colonnes
```


pipreqs ./src --force