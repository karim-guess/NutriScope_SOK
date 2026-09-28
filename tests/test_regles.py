import pandas as pd
import pytest
from src.cleaning import (
    # REGLE_CATEGORIES_VIDE,
    REGLE_CORRIGER_ENERGIE,
    REGLE_NORMALISER_TEXTE,
    REGLE_NORMALISER_UNITE,
    TOUTES_LES_REGLES,
    KJ_PAR_KCAL,
    CompteRendu,
    borner_nutriments,
    corriger_energie,
    dedupliquer_codes,
    normaliser_textes,
    normaliser_unites,
    traiter_categories_vides
)

def test_borner_nutriments_negatif_et_sup_100(tordu):
    df, cr = borner_nutriments(tordu)
    assert pd.isna(df.loc[2, "fat_100g"])             # 2 000 g -> NA
    assert pd.isna(df.loc[3, "carbohydrates_100g"])   # -1 g -> NA
    assert pd.isna(df.loc[4, "sugars_100g"])          # 74 000 g -> NA
    assert df.loc[0, "fat_100g"] == 10.0              # cas nominal, inchangé
    assert isinstance(cr, CompteRendu) and cr.regle == "borner_nutriments"
    assert cr.details["fat_100g_hors_bornes"] == 1

def test_sugars_incoherent_glucides(tordu):
    df, cr = borner_nutriments(tordu)
    assert pd.isna(df.loc[5, "sugars_100g"])          # sugars_100g > carbohydrates_100g + 0.5
    assert cr.details["sugars_incoherent_glucides"] == 1

def test_saturated_incoherent_fat(tordu):
    df, cr = borner_nutriments(tordu)
    assert pd.isna(df.loc[5, "saturated-fat_100g"])   # saturated-fat_100g > fat_100g + 0.5
    assert cr.details["saturated_incoherent_fat"] == 1

def test_dedupliquer_codes_garde_le_plus_complet(tordu):
    df, cr = dedupliquer_codes(tordu)
    assert df["code"].is_unique
    assert 1 not in df.index # doublon "001" moins complet (0,4 < 0,9) écarté
    assert 4 not in df.index # ligne sans code écartée
    assert cr.details == {"sans_code": 1, "doublons_supprimes": 1}
    assert cr.lignes_supprimees == 2

def test_normaliser_unites_incoherent_ou_incomplette(kcal_salt_sodium_tordu):
    df, cr = normaliser_unites(kcal_salt_sodium_tordu)
    assert df.loc[0, "energy-kcal_100g"] == 11.9503
    assert cr.details["energy_kcal_100g_manquant_calcul_derivees"] == 1
    assert df.loc[1, "energy-kcal_100g"] == 2.3901
    assert cr.details["energy_kcal_100g_hors_borne_recalculees"] == 1
    assert df.loc[2, "salt_100g"] == 2.5
    assert cr.details["salt_100g_manquant_calcul_derivees"] == 1
    assert df.loc[3, "sodium_100g"] == 1
    assert cr.details["sodium_100g_manquant_calcul_derivees"] == 1
    assert df.loc[4, "sodium_100g"] == 4
    assert cr.details["sodium_100g_incoherent_recalculees"] == 1

def test_corriger_energie(energies_tordu):
    df, cr = corriger_energie(energies_tordu)
    assert df.loc[0, "energy-kcal_100g"] == 130.0 # Ligne 0 : kcal nulle recalculée (10*4 + 10*9 = 130)
    assert df.loc[1, "energy-kcal_100g"] == 40.0  # Ligne 1 : kcal > 900 recalculée car le calcul 449 fait 40.0 (<= 900)
    assert pd.isna(df.loc[2, "energy-kcal_100g"]) # Ligne 2 : kcal > 900 invalidée (NaN) car le calcul 449 fait 990 (> 900)
    assert df.loc[3, "energy-kcal_100g"] == 50.0  # Ligne 3 : kcal incohérente recalculée (calcul = 12.5 * 4 = 50. 150 est à plus de 50% d'écart)
    assert df.loc[4, "energy-kcal_100g"] == 0.0   # Ligne 4 : Pas de modification (Reste à 0) grâce à l'exception Alcoholic beverages

    # Vérification du réalignement systématique des kJ
    for i in range(len(df)):
        if pd.isna(df.loc[i, "energy-kcal_100g"]):
            assert pd.isna(df.loc[i, "energy_100g"])
        else:
            assert df.loc[i, "energy_100g"] == (
                df.loc[i, "energy-kcal_100g"] * KJ_PAR_KCAL
            )

    assert cr.details["energy_kcal_100g_nulles_recalculees"] == 1
    assert cr.details["energy_kcal_100g_plus_900_recalculees"] == 1
    assert cr.details["energy_kcal_100g_plus_900_invalidees"] == 1
    assert cr.details["incoherentes_energy-kcal_100g_recalculees"] == 1

def test_corriger_categories(categories_tordu):
    df, cr = traiter_categories_vides(categories_tordu)

    # Ligne 0 : Rayon complété à 'unknown'
    assert df.loc[0, "pnns_groups_1"] == "unknown"
    assert df.loc[0, "categorie_vide"] == False

    # Ligne 1 : Dérivation de la catégorie principale depuis le dernier tag
    assert df.loc[1, "main_category"] == "en:biscuits"
    assert df.loc[1, "categorie_vide"] == True

    # Ligne 2 : Drapeau catégorie vide activé
    assert df.loc[2, "categorie_vide"] == True
    assert df.loc[2, "pnns_groups_1"] == "Beverages" # Conservé car le rayon est connu

    # Ligne 3 : Supprimée car pas de catégorie et rayon inconnu (inclassable)
    assert 3 not in df.index
    assert len(df) == 3

    # Vérification des métriques du compte rendu
    assert cr.details["rayon_manquant_unknown"] == 2        # Ligne 0, Ligne 3
    assert cr.details["main_category_derivee"] == 1         # Ligne 1
    assert cr.details["drapeau_categorie_vide_ajoute"] == 3 # Ligne 1 (derivée tags), Ligne 2, Ligne 3
    assert cr.details["inclassables_supprimes"] == 1        # Ligne 3

def test_normaliser_textes(texte_tordu):
    df, cr = normaliser_textes(texte_tordu)

    # Ligne 0 : Passage en majuscules
    assert df.loc[0, "product_name"] == "CHOCOLAT AU LAIT"
    assert df.loc[0, "brands"] == "Nestlé"

    # Ligne 1 : Nom vide devient NA, marque harmonisée sur la forme fréquente 'Nestlé'
    assert pd.isna(df.loc[1, "product_name"])
    assert df.loc[1, "brands"] == "Nestlé"

    # Ligne 2 & 3 : Nettoyage des grades inconnus (unknown et unknown_group deviennent NA)
    assert pd.isna(df.loc[2, "nutriscore_grade"])
    assert pd.isna(df.loc[1, "nova_group"])
    assert pd.isna(df.loc[3, "nova_group"])

    # Vérification des métriques du compte rendu
    assert cr.details["noms_vides_nettoyes"] == 1
    assert cr.details["marques_harmonisees"] == 1     # La ligne 1 "nestlé" a été modifiée en "Nestlé"
    assert cr.details["grades_unknown_nettoyes"] == 3 # Ligne 2 (nutriscore), Ligne 1 (nova), Ligne 3 (nova)

import pandas as pd
import pytest

# RÈGLES GÉNÉRALES (typer_colonnes, borner_nutriments, dedupliquer_codes)
@pytest.mark.parametrize("regle", TOUTES_LES_REGLES)
def test_idempotence_regles_generales(regle, tordu):
    une_fois, _ = regle(tordu)
    deux_fois, cr = regle(une_fois)
    pd.testing.assert_frame_equal(une_fois, deux_fois)
    assert cr.lignes_touchees == 0

# RÈGLE : normaliser_unites
@pytest.mark.parametrize("regle", REGLE_NORMALISER_UNITE)
def test_idempotence_normaliser_unites(regle, kcal_salt_sodium_tordu):
    une_fois, _ = regle(kcal_salt_sodium_tordu)
    deux_fois, cr = regle(une_fois)
    pd.testing.assert_frame_equal(une_fois, deux_fois)
    assert cr.lignes_touchees == 0

# RÈGLE : corriger_energie (utilise la bonne fixture energies_tordu)
@pytest.mark.parametrize("regle", REGLE_CORRIGER_ENERGIE)
def test_idempotence_corriger_energie(regle, energies_tordu):
    une_fois, _ = regle(energies_tordu)
    deux_fois, cr = regle(une_fois)
    pd.testing.assert_frame_equal(une_fois, deux_fois)
    assert cr.lignes_touchees == 0

# RÈGLE : traiter_categories_vides
# /!\ Drapeau categorie_vide
# @pytest.mark.parametrize("regle", REGLE_CATEGORIES_VIDE)
# def test_idempotence_categories(regle, categories_tordu):
#     une_fois, _ = regle(categories_tordu)
#     deux_fois, cr = regle(une_fois)
#     pd.testing.assert_frame_equal(une_fois, deux_fois)
#     assert cr.lignes_touchees == 0

# RÈGLE : normaliser_textes (si stockée dans REGLE_NORMALISER_TEXTE)
@pytest.mark.parametrize("regle", REGLE_NORMALISER_TEXTE)
def test_idempotence_textes(regle, texte_tordu):
    une_fois, _ = regle(texte_tordu)
    deux_fois, cr = regle(une_fois)
    pd.testing.assert_frame_equal(une_fois, deux_fois)
    assert cr.lignes_touchees == 0
