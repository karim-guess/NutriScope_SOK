import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats as scipy_stats 
from unittest.mock import patch  
from src.eda import figure, resume_univarie, profil_par_rayon

def test_figure_cree_le_fichier_png(monkeypatch):
    """Vérifie que la fonction sauvegarde bien le fichier dans 'figures/' et ferme la figure."""
    nom_test = "graphique_test"

    dossier_cible = Path("tests/figures")
    os.makedirs(dossier_cible, exist_ok=True)
    fichier_attendu = dossier_cible / f"{nom_test}.png"
    
    # On déplace temporairement le répertoire de travail dans './tests'
    monkeypatch.chdir("tests")
    
    plt.switch_backend("Agg")
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    fignum = fig.number

    # Exécution avec mock de l'affichage pour éviter l'erreur hors-notebook
    with patch("src.eda.display") as mock_display:
        figure(fig, nom_test)
        
        monkeypatch.undo()

        assert fichier_attendu.exists(), "Le fichier PNG n'a pas été généré."
        assert fichier_attendu.stat().st_size > 0, "Le fichier PNG généré est vide."
        assert not plt.fignum_exists(fignum), "La figure Matplotlib n'a pas été fermée."
        mock_display.assert_called_once()
        
    # Nettoyage
    if fichier_attendu.exists():
        os.remove(fichier_attendu)

def test_resume_univarie_calculs_exacts():
    """Vérifie l'exactitude des calculs de la fonction resume_univarie."""
    # Création d'un échantillon avec une valeur manquante (NaN)
    donnees_test = pd.Series([10, 20, 20, 30, 40, np.nan])
    
    stats_resultat = resume_univarie(donnees_test)
    
    # Assertions sur les effectifs
    assert stats_resultat["n"] == 5
    assert stats_resultat["manquants"] == 1
    
    # Assertions sur la tendance centrale et dispersion
    assert stats_resultat["moyenne"] == 24.0
    assert stats_resultat["mediane"] == 20.0
    assert stats_resultat["IQR"] == 10.0  # Q75 (30) - Q25 (20)
    
    # Vérification du MAD (Scipy calcule par défaut avec scale=1.4826, 
    assert stats_resultat["MAD"] == scipy_stats.median_abs_deviation(donnees_test.dropna())

def test_resume_univarie_valeurs_connues():
    """Vérifie le comportement de resume_univarie sur un échantillon simple sans manquants."""
    donnees_simples = pd.Series([10, 20, 30])

    stats_resultat = resume_univarie(donnees_simples)

    assert stats_resultat["n"] == 3
    assert stats_resultat["manquants"] == 0
    assert stats_resultat["moyenne"] == 20.0
    assert stats_resultat["mediane"] == 20.0
    assert stats_resultat["min"] == 10
    assert stats_resultat["max"] == 30

def test_profil_par_rayon_valeurs_connues(mock_food_data):
    """
    Vérifie les calculs statistiques (Moyenne, Médiane, Q1, Q3)
    sur des valeurs mathématiques connues à l'avance.
    """
    # On fixe min_n=3 pour que Rayon_A (4 lignes) soit conservé
    resultat = profil_par_rayon(
        mock_food_data, ["sugars_100g", "salt_100g"], min_n=3
    )

    # Valeurs de Rayon_A : [10.0, 20.0, 30.0, 40.0]
    stats_sucre = resultat.loc[("sugars_100g", "Rayon_A")]

    assert stats_sucre["effectif"] == 4
    assert stats_sucre["moyenne"] == 25.0  # (10+20+30+40) / 4
    assert stats_sucre["mediane"] == 25.0  # Milieu entre 20 et 30
    assert stats_sucre["q1"] == 17.5       # Quantile 25%
    assert stats_sucre["q3"] == 32.5       # Quantile 75%

    # Valeurs de Rayon_A : [1.0, 2.0, 3.0, 4.0]
    stats_sel = resultat.loc[("salt_100g", "Rayon_A")]

    assert stats_sel["effectif"] == 4
    assert stats_sel["moyenne"] == 2.5
    assert stats_sel["mediane"] == 2.5

def test_profil_par_rayon_filtrage_petit_groupe(mock_food_data):
    """
    Vérifie qu'un groupe possédant moins de lignes que 'min_n'
    est correctement exclu du tableau final.
    """
    # Rayon_B possède 2 lignes. Avec min_n=3, il doit disparaître.
    resultat = profil_par_rayon(
        mock_food_data, ["sugars_100g", "salt_100g"], min_n=3
    )

    # Vérifier que 'Rayon_A' est présent dans l'index au niveau 'rayon'
    assert "Rayon_A" in resultat.index.get_level_values("rayon")

    # Vérifier que 'Rayon_B' a bien été écarté
    assert "Rayon_B" not in resultat.index.get_level_values("rayon")
