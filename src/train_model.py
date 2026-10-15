#!/usr/bin/env python3
"""
Étape 6 — Entraînement et évaluation du modèle Nutri-Score
Fichier : train_model.py
"""

import argparse
import os
import sys
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix


def main():
    parser = argparse.ArgumentParser(description="Entraînement du modèle prédictif Nutri-Score.")
    parser.add_argument("--input-file", type=str, required=True, help="Chemin vers le fichier Parquet figé (ex: features_nutriscore_20261014.parquet)")
    parser.add_argument("--model-dir", type=str, default=".", help="Répertoire de sauvegarde du modèle")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Erreur : Le fichier {args.input_file} n'existe pas.", file=sys.stderr)
        sys.exit(1)

    print(f"Chargement des données depuis {args.input_file}...")
    df = pd.read_parquet(args.input_file)

    # Séparation Train / Test basée STRICTEMENT sur la colonne 'split'
    print("Séparation des ensembles Train et Test...")
    df_train = df[df['split'] == 'train']
    df_test = df[df['split'] == 'test']

    # Définition des features (variables explicatives) et de la cible
    features = [
        'energy-kcal_100g', 'fat_100g', 'saturated-fat_100g',
        'carbohydrates_100g', 'sugars_100g', 'proteins_100g', 'salt_100g',
        'additives_n', 'nova_group',
        'ratio_sugar_carbs', 'ratio_sat_fat', 'ratio_energy_fat'
    ]
    target = 'nutriscore_grade'

    X_train, y_train = df_train[features], df_train[target]
    X_test, y_test = df_test[features], df_test[target]

    print(f"Dataset d'entraînement : {X_train.shape[0]} lignes")
    print(f"Dataset de test : {X_test.shape[0]} lignes")

    # Initialisation et entraînement du modèle
    # On fixe le random_state pour garantir la reproductibilité complète
    print("Entraînement du modèle Random Forest (cela peut prendre quelques instants)...")
    model = RandomForestClassifier(
        # n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Évaluation du modèle sur le jeu de test
    print("Évaluation sur le jeu de test...")
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"\n================ HARD METRICS ================")
    print(f"Accuracy Globale : {acc:.4f}")
    print("==============================================")
    
    print("\nRapport de classification par Grade :")
    report = classification_report(y_test, y_pred, target_names=sorted(df[target].unique()))
    print(report)

    # Sauvegarde du modèle et des métadonnées
    os.makedirs(args.model_dir, exist_ok=True)
    model_path = os.path.join(args.model_dir, "model_nutriscore.pkl")
    metrics_path = os.path.join(args.model_dir, "metrics.json")

    print(f"\nSauvegarde du modèle dans : {model_path}")
    joblib.dump(model, model_path)

    # Sauvegarde des métriques au format JSON pour l'historique
    metrics_data = {
        "accuracy": round(acc, 4),
        "features_used": features,
        "train_samples": X_train.shape[0],
        "test_samples": X_test.shape[0],
        "timestamp": pd.Timestamp.now().isoformat()
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4)

    print("Entrainement terminé.")


if __name__ == "__main__":
    main()
