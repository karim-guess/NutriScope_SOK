import pandas as pd
import numpy as np
import pytest

@pytest.fixture
def tordu() -> pd.DataFrame:
    """Cinq lignes construites à la main, un cas par situation à couvrir."""
    # ligne 5 : sugars_100g > carbohydrates_100g + 0.5
    # ligne 5 : saturated-fat_100g > fat_100g + 0.5
    return pd.DataFrame({
        "code": ["001", "001", "002", "003", None, "004"],            # nominal, doublon, ok, ok, sans code
        "completeness": [0.9, 0.4, 0.7, 0.6, 0.5, 0.9],
        "fat_100g": [10.0, 10.0, 2000.0, 5.0, 3.0, 10.0],             # ligne 2 : 2 000 g -> impossible
        "carbohydrates_100g": [20.0, 20.0, 0.0, -1.0, 10.0, 20.0],    # ligne 3 : négatif -> impossible
        "sugars_100g": [5.0, 5.0, 0.0, 0.0, 74000.0, 20.6],           # ligne 4 : 74 000 g -> impossible
        "proteins_100g": [3.0, 3.0, 0.0, 2.0, 1.0, 3.0],
        "salt_100g": [1.0, 1.0, 0.0, 0.5, 0.5, 1.0],
        "saturated-fat_100g": [1.0, 1.0, 1.0, 1.0, 1.0, 10.6],
        "fruits-vegetables-legumes_100g": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    })

@pytest.fixture
def kcal_salt_sodium_tordu() -> pd.DataFrame:
    """
        Ligne 0 : energy-kcal_100g est absent mais energy_100g est présent -> dérivation
        Ligne 1 : Le rapport energy_100g/energy-kcal_100g sort de [3.9, 4.5] -> recalcul des energy_100g
        Ligne 2 : Dérivation du salt_100g si absent
        Ligne 3 : Dérivation du sodium_100g si absent
        Ligne 4 : Recalcul du sodium_100g depuis le salt_100g si incohérent (écart > 0.01g)
    """
    return pd.DataFrame({
        'energy-kcal_100g': [None, 50.0, 0.0, 0.0, 0.0],
        'energy_100g': [50.0, 10.0, 0.0, 0.0, 0.0],
        'salt_100g': [0.0, 0.0, None, 2.5, 10.0],
        'sodium_100g': [0.0, 0.0, 1.0, None, 20.0]
    })

@pytest.fixture
def energies_tordu() -> pd.DataFrame:
    """
        Ligne 0 : kcal = 0 avec des macros (10g prot = 40, 10g lip = 90 -> calcul = 130) -> recalcul
        Ligne 1 : kcal > 900 (950) mais macros valides (10g prot, calcul = 40 <= 900) -> recalcul
        Ligne 2 : kcal > 900 (999) et calcul > 900 (110g lipides -> calcul = 990) -> NA
        Ligne 3 : kcal à plus de 50% du calcul théorique (150 kcal pour un calcul à 50) -> recalcul
        Ligne 4 : exception Alcool (kcal=0 avec macros mais rayon Alcoholic beverages) -> inchangé
    """
    return pd.DataFrame(
        {
            "energy-kcal_100g": [0.0, 950.0, 999.0, 150.0, 0.0],
            "energy_100g": [0.0, 0.0, 0.0, 0.0, 0.0],
            "proteins_100g": [10.0, 10.0, 0.0, 0.0, 10.0],
            "carbohydrates_100g": [0.0, 0.0, 0.0, 12.5, 0.0],
            "fat_100g": [10.0, 0.0, 110.0, 0.0, 10.0],
            "pnns_groups_1": [
                "Fruits",
                "Vegetables",
                "Fats",
                "Sugars",
                "Alcoholic beverages",
            ],
        }
    )

@pytest.fixture
def categories_tordu() -> pd.DataFrame:
    """
        Ligne 0 : Rayon absent, possède une catégorie -> rayon devient 'unknown', main_category reste intacte.
        Ligne 1 : Main_category absente -> dérivée du dernier tag de 'categories' ('en:biscuits') -> drapeau categorie_vide=True.
        Ligne 2 : Categories vide -> drapeau categorie_vide=True.
        Ligne 3 : INCLASSABLE -> sans catégorie ET rayon absent (devient unknown) -> Supprimé.
    """
    return pd.DataFrame({
        "pnns_groups_1": [np.nan, "Sugary snacks", "Beverages", np.nan],
        "categories_tags": ["en:beverages,en:juices", "en:snacks,en:biscuits", np.nan, np.nan],
        "main_category": ["en:juices", np.nan, np.nan, np.nan]
    })

import numpy as np
import pandas as pd
import pytest

@pytest.fixture
def texte_tordu():
    """
    Génère un DataFrame pour tester les cas limites de normaliser_textes :
    - Ligne 0 : Cas nominal propre (Nestlé sert de référence majoritaire)
    - Ligne 1 : Nom vide (none), marque à harmoniser (nestlé), nova inconnu (unknown_group)
    - Ligne 2 : Nutriscore inconnu (unknown)
    - Ligne 3 : Nova inconnu avec espaces ('  nan  '), Nestlé répété pour être le mode
    """
    return pd.DataFrame({
        "product_name": [
            "chocolat au lait",  # Ligne 0 -> Devient "CHOCOLAT AU LAIT"
            "none",              # Ligne 1 -> Devient NaN (compte pour noms_vides_nettoyes)
            "Biscuit",           # Ligne 2
            "Jus d'orange"       # Ligne 3
        ],
        "brands": [
            "Nestlé",            # Ligne 0 -> Forme de référence 1
            "nestlé",            # Ligne 1 -> Modifiée en "Nestlé" (compte pour marques_harmonisees)
            "Danone",            # Ligne 2
            "Nestlé"             # Ligne 3 -> Forme de référence 2 (fait de 'Nestlé' la graphie majoritaire)
        ],
        "nutriscore_grade": [
            "a",                 # Ligne 0
            "b",                 # Ligne 1
            "unknown",           # Ligne 2 -> Devient NaN (compte pour grades_unknown_nettoyes)
            "c"                  # Ligne 3
        ],
        "nova_group": [
            "4",                 # Ligne 0
            "unknown_group",     # Ligne 1 -> Devient NaN (compte pour grades_unknown_nettoyes)
            "3",                 # Ligne 2
            "  nan  "            # Ligne 3 -> Devient NaN (compte pour grades_unknown_nettoyes)
        ]
    })
