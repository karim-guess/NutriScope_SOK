from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import warnings
from src.constant import TEXT_TYPE, NUMERIC_TYPE, CSV_SELECTED_NUTRIMENT_COLUMNS, STRATEGIE_PAR_DEFAUT, FLAG_COLUMNS

KCAL_MAX = 900.0
SEL_PAR_SODIUM = 2.5
KJ_PAR_KCAL = 4.184
CATEGORY_ALCHOL = 'Alcoholic beverages'
NUTRIMENTS_G = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "sugars_100g", "proteins_100g", "salt_100g", "fruits-vegetables-legumes_100g"]
BORNES_MAX = {col: 100.0 for col in NUTRIMENTS_G}
BORNES_MAX["sodium_100g"] = 40.0

ROUND = 4
NUMERIC = NUMERIC_TYPE + CSV_SELECTED_NUTRIMENT_COLUMNS

@dataclass
class CompteRendu:
    """Ce qu'une règle a fait : lignes avant / après, lignes touchées, détail par sous-règle."""

    regle: str
    lignes_avant: int
    lignes_apres: int
    lignes_touchees: int
    details: dict = field(default_factory=dict)

    @property
    def lignes_supprimees(self) -> int:
        return self.lignes_avant - self.lignes_apres

    def __str__(self) -> str:
        detail = ", ".join(f"{k}={v}" for k, v in self.details.items()) or "-"
        return f"{self.regle}: {self.lignes_avant} -> {self.lignes_apres} lignes, {self.lignes_touchees} touchée(s) [{detail}]"


def _lignes_modifiees(avant: pd.DataFrame, apres: pd.DataFrame, colonnes: list[str]) -> int:
    """Nombre de lignes dont au moins une des colonnes a changé (deux NA comparés comme égaux)."""
    a, b = avant[colonnes], apres[colonnes]
    differe = ~((a == b) | (a.isna() & b.isna()))
    return int(differe.any(axis=1).sum())

def typer_colonnes(df: pd.DataFrame) -> tuple[pd.DataFrame, CompteRendu]:
    """
        Conversion des type des colonnes.
        code: string
        compteurs: Int64
        nutriments: float64
    """
    resultat = df.copy()

    for col in TEXT_TYPE:
        resultat[col] = resultat[col].astype("string")
    for col in NUMERIC:
        resultat[col] = resultat[col].astype("float64")

    colonnes_controlees = TEXT_TYPE + NUMERIC
    touchees = _lignes_modifiees(df, resultat, colonnes_controlees)
    
    details = {"colonnes_typees": len(colonnes_controlees)}

    try:
        pd.testing.assert_frame_equal(df, resultat)
    except AssertionError as e:
        details = {"statut": "le DataFrame à été modifié"}

    return resultat, CompteRendu("typer_colonnes", len(df), len(resultat), touchees, details)

def borner_nutriments(df: pd.DataFrame) -> tuple[pd.DataFrame, CompteRendu]:
    """
    Invalide (NA) les nutriments négatifs ou > 100 g/100 g.
    """
    resultat = df.copy()
    details: dict[str, int] = {}
    for col in NUTRIMENTS_G:
        hors = (resultat[col] < 0) | (resultat[col] > BORNES_MAX[col])
        details[f"{col}_hors_bornes"] = int(hors.sum())
        resultat[col] = resultat[col].mask(hors, np.nan)

    """
    Invalide (NA) Sucres > Glucides + 0.5
    """
    coherence_sucre = resultat["sugars_100g"] > (resultat["carbohydrates_100g"] + 0.5)
    details["sugars_incoherent_glucides"] = int(coherence_sucre.sum())
    resultat["sugars_100g"] = resultat["sugars_100g"].mask(coherence_sucre, np.nan)

    """
    Invalide (NA) Acides Gras Saturés > Lipides + 0.5
    """
    coherence_sat = resultat["saturated-fat_100g"] > (resultat["fat_100g"] + 0.5)
    details["saturated_incoherent_fat"] = int(coherence_sat.sum())
    resultat["saturated-fat_100g"] = resultat["saturated-fat_100g"].mask(coherence_sat, np.nan)

    touchees = _lignes_modifiees(df, resultat, NUTRIMENTS_G)
    return resultat, CompteRendu("borner_nutriments", len(df), len(resultat), touchees, details)

def dedupliquer_codes(df: pd.DataFrame) -> tuple[pd.DataFrame, CompteRendu]:
    """
    Garde une seule fiche par code-barres : la plus complète.
    """
    resultat = df.copy()
    details: dict[str, int] = {}
    resultat["code"] = resultat["code"].astype("string").str.strip()
    sans_code = resultat["code"].isna() | (resultat["code"] == "")
    details["sans_code"] = int(sans_code.sum())
    resultat = resultat[~sans_code]
    if "completeness" in resultat.columns:
        resultat = resultat.sort_values("completeness", ascending=False, na_position="last", kind="stable")
    doublons = resultat["code"].duplicated(keep="first")
    details["doublons_supprimes"] = int(doublons.sum())
    resultat = resultat[~doublons].sort_index()
    touchees = len(df) - len(resultat)
    return resultat, CompteRendu("dedupliquer_codes", len(df), len(resultat), touchees, details)

def normaliser_textes(df: pd.DataFrame) -> tuple[pd.DataFrame, CompteRendu]:
    """
    Normalise les colonnes textuelles :
    - Noms vides ('product_name') -> NA
    - Noms convertis en MAJUSCULES (standardisation)
    - Marques ('brands') ramenées à leur graphie la plus fréquente (la casse la plus courante)
    - Nutri-score grade / Nova group ayant pour valeur 'unknown' ou 'unknown_group' -> NA
    """
    resultat = df.copy()
    details: dict[str, int] = {"grades_unknown_nettoyes": 0}

    # Gestion des noms de produits (product_name)
    if "product_name" in resultat.columns:
        resultat["product_name"] = resultat["product_name"].astype(str).str.strip()
        nom_minuscules = resultat["product_name"].str.lower()
        mask_nom_vide = (resultat["product_name"] == "") | (nom_minuscules == "nan") | (nom_minuscules == "none")
        details["noms_vides_nettoyes"] = int(mask_nom_vide.sum())
        
        resultat["product_name"] = resultat["product_name"].str.upper()
        resultat.loc[mask_nom_vide, "product_name"] = np.nan

    # Harmonisation des marques (brands) selon la graphie la plus fréquente
    if "brands" in resultat.columns:
        # On garde une copie propre des valeurs initiales pour la comparaison de fin
        marques_initiales = resultat["brands"].copy()
        
        marques_brutes = resultat["brands"].astype(str).str.strip()
        marques_minuscules = marques_brutes.str.lower()
        mask_marque_valide = (resultat["brands"].notna()) & (marques_brutes != "") & (marques_minuscules != "nan") & (marques_minuscules != "none")
        
        if mask_marque_valide.any():
            resultat["_brands_lower"] = marques_minuscules
            df_valide = resultat[mask_marque_valide]
            
            mode_par_marque = (
                df_valide.groupby("_brands_lower")["brands"]
                .agg(lambda x: x.mode().iloc[0] if not x.empty else np.nan)
            )
            
            marques_harmonisees = resultat["_brands_lower"].map(mode_par_marque)
            
            mask_changement = mask_marque_valide & (marques_initiales != marques_harmonisees)
            details["marques_harmonisees"] = int(mask_changement.sum())
            
            resultat["brands"] = marques_harmonisees
            resultat.loc[~mask_marque_valide, "brands"] = np.nan
            resultat.drop(columns=["_brands_lower"], inplace=True)
        else:
            resultat.loc[~mask_marque_valide, "brands"] = np.nan

    # Nettoyage des grades
    resultat['nutriscore_grade'] = resultat['nutriscore_grade'].str.lower()

    # Calcul des lignes touchées
    colonnes_controlees = [c for c in ["product_name", "brands", "nutriscore_grade"] if c in df.columns]
    touchees = _lignes_modifiees(df, resultat, colonnes_controlees)

    return resultat, CompteRendu("normaliser_textes", len(df), len(resultat), touchees, details)

def normaliser_unites(df: pd.DataFrame) -> tuple[pd.DataFrame, CompteRendu]:
    """
    Normalise les énergies (kJ/kcal) et la relation sel/sodium.
    - kcal: energy_100g / 4.184 si kcal absente ou si le rapport energy_100g/energy_kcal_100g hors de [3.9, 4.5]
    - sel <-> sodium x 2.5 dans les deux sens si l'un manque
    - sodium recalculé depuis le sel si incohérent (!= sel / 2.5)
    """
    resultat = df.copy()
    details: dict[str, int] = {}

    # Gestion des énergies (energy_100g / energy-kcal_100g)
    energy_100g = resultat["energy_100g"]
    energy_kcal_100g = resultat["energy-kcal_100g"]
    ratio_energy_energy_kcal = energy_100g / energy_kcal_100g

    # Cas A : energy_kcal_100g est absent mais energy_100g est présent -> dérivation
    mask_kcal_manquant = energy_kcal_100g.isna() & energy_100g.notna() & (energy_100g > 0)
    resultat.loc[mask_kcal_manquant, "energy-kcal_100g"] = (energy_100g / KJ_PAR_KCAL).round(ROUND)
    details["energy_kcal_100g_manquant_calcul_derivees"] = int(mask_kcal_manquant.sum())

    # Cas B : Le rapport energy_100g/energy_kcal_100g sort de [3.9, 4.5] -> recalcul des kcal
    mask_rapport_incoherent = (
        energy_kcal_100g.notna()
        & energy_100g.notna()
        & ((ratio_energy_energy_kcal < 3.9) | (ratio_energy_energy_kcal > 4.5))
    )
    resultat.loc[mask_rapport_incoherent, "energy-kcal_100g"] = (energy_100g / KJ_PAR_KCAL).round(ROUND)
    details["energy_kcal_100g_hors_borne_recalculees"] = int(mask_rapport_incoherent.sum())

    # Gestion salt_100g <-> sodium_100g
    salt_100g = resultat["salt_100g"]
    sodium_100g = resultat["sodium_100g"]

    # Dérivation du salt_100g si absent
    mask_salt_100g_manquant = salt_100g.isna() & sodium_100g.notna()
    resultat.loc[mask_salt_100g_manquant, "salt_100g"] = (sodium_100g * SEL_PAR_SODIUM).round(ROUND)
    details["salt_100g_manquant_calcul_derivees"] = int(mask_salt_100g_manquant.sum())

    # Dérivation du sodium_100g si absent
    mask_sodium_100g_manquant = sodium_100g.isna() & salt_100g.notna()
    resultat.loc[mask_sodium_100g_manquant, "sodium_100g"] = (salt_100g / SEL_PAR_SODIUM).round(ROUND)
    details["sodium_100g_manquant_calcul_derivees"] = int(mask_sodium_100g_manquant.sum())

    # Recalcul du sodium_100g depuis le salt_100g si incohérent (écart > 0.01g)
    salt_100g = resultat["salt_100g"]
    sodium_100g = resultat["sodium_100g"]

    mask_sodium_100g_incoherent = (
        salt_100g.notna()
        & sodium_100g.notna()
        & ((sodium_100g - (salt_100g / SEL_PAR_SODIUM)).abs() > 0.01)
    )
    resultat.loc[mask_sodium_100g_incoherent, "sodium_100g"] = (salt_100g / SEL_PAR_SODIUM).round(ROUND)
    details["sodium_100g_incoherent_recalculees"] = int(mask_sodium_100g_incoherent.sum())

    touchees = _lignes_modifiees(df, resultat, [
        "energy-kcal_100g",
        "energy_100g",
        "salt_100g",
        "sodium_100g",
    ])

    return resultat, CompteRendu("normaliser_unites", len(df), len(resultat), touchees, details)

def corriger_energie(df: pd.DataFrame) -> tuple[pd.DataFrame, CompteRendu]:
    """
    Corrige les anomalies sur les calories (kcal) et réaligne les kJ :
    - kcal nulles (0) alors qu'il y a des macronutriments -> recalcul
    - kcal > 900 -> recalcul si possible, sinon NA
    - kcal à plus de 50 % du calcul théorique 4/4/9 (si calcul >= 50 kcal) -> recalcul, sinon NA
    - Exception : Ne pas appliquer les recalculs/invalidation de cohérence sur le rayon 'Alcoholic beverages'
    - À la fin : Réalignement des kJ (energy_100g) depuis les kcal finales
    """
    resultat = df.copy()
    details: dict[str, int] = {}

    # Préparation des variables et du calcul théorique 4/4/9
    energy_kcal_100g = resultat["energy-kcal_100g"]
    
    # Remplissage temporaire des NaN par 0 pour le calcul théorique des macros
    fat_100g = resultat["fat_100g"].fillna(0)
    carbohydrates_100g = resultat["carbohydrates_100g"].fillna(0)
    proteins_100g = resultat["proteins_100g"].fillna(0)
    
    calcul_449 = (proteins_100g * 4.0) + (carbohydrates_100g * 4.0) + (fat_100g * 9.0)
    a_des_macros = calcul_449 > 0

    # Masque d'exclusion pour le rayon alcool
    is_alcool = resultat.get("pnns_groups_1", pd.Series(False, index=resultat.index)) == CATEGORY_ALCHOL

    # energy_kcal_100g nulles avec macronutriments
    mask_nulle_avec_macro = (energy_kcal_100g == 0) & a_des_macros & (~is_alcool)
    resultat.loc[mask_nulle_avec_macro, "energy-kcal_100g"] = calcul_449
    details["energy_kcal_100g_nulles_recalculees"] = int(mask_nulle_avec_macro.sum())

    energy_kcal_100g = resultat["energy-kcal_100g"]

    # energy_kcal_100g > 900
    mask_trop_haute = energy_kcal_100g > KCAL_MAX
    
    # On peut recalculer si le produit a des macros valides et n'est pas de l'alcool, et que ce calcul est <= 900
    mask_trop_haute_recalcul = mask_trop_haute & a_des_macros & (calcul_449 <= KCAL_MAX) & (~is_alcool)
    mask_trop_haute_invalide = mask_trop_haute & (~mask_trop_haute_recalcul)

    resultat.loc[mask_trop_haute_recalcul, "energy-kcal_100g"] = calcul_449
    resultat.loc[mask_trop_haute_invalide, "energy-kcal_100g"] = np.nan
    
    details["energy_kcal_100g_plus_900_recalculees"] = int(mask_trop_haute_recalcul.sum())
    details["energy_kcal_100g_plus_900_invalidees"] = int(mask_trop_haute_invalide.sum())

    # energy_kcal_100g à plus de 50% du calcul théorique (si calcul >= 50 kcal)
    energy_kcal_100g = resultat["energy-kcal_100g"]

    # Écart relatif de plus de 50% : |energy_kcal_100g - calcul_449| / calcul_449 > 0.50
    écart_coherence = ((energy_kcal_100g - calcul_449).abs() / calcul_449) > 0.50
    mask_incoherent = energy_kcal_100g.notna() & (calcul_449 >= 50) & écart_coherence & (~is_alcool)

    # Si incohérent -> recalcul via 449
    resultat.loc[mask_incoherent, "energy-kcal_100g"] = calcul_449
    details["incoherentes_energy-kcal_100g_recalculees"] = int(mask_incoherent.sum())

    # Réalignement des energy_100g
    kcal_finales = resultat["energy-kcal_100g"]
    resultat["energy_100g"] = kcal_finales * KJ_PAR_KCAL

    # Calcul des lignes touchées
    touchees = _lignes_modifiees(df, resultat, ["energy-kcal_100g", "energy_100g"])

    return resultat, CompteRendu("corriger_energie", len(df), len(resultat), touchees, details)

def traiter_categories_vides(df: pd.DataFrame) -> tuple[pd.DataFrame, CompteRendu]:
    """
    Traite les catégories et rayons manquants ou vides :
    - 'pnns_groups_1' (rayon) manquant -> remplacé par 'unknown'
    - 'main_category' dérivée du dernier élément de 'categories' si absente
    - Crée un drapeau 'categorie_vide' (booléen) si 'categories' était vide ou absent
    - Supprime du périmètre les produits qui n'ont AUCUNE catégorie ET dont le rayon est 'unknown'
    """
    resultat = df.copy()
    details: dict[str, int] = {}

    # VERIFICATION ET CONVERSION DES CHAINES VIDES EN NA
    colonnes_texte = resultat.select_dtypes(include=['string', 'object']).columns
    if not colonnes_texte.empty:
        resultat[colonnes_texte] = resultat[colonnes_texte].replace(r'^\s*$', np.nan, regex=True)

    # Gestion du rayon (pnns_groups_1) manquant -> 'unknown'
    mask_rayon_manquant = resultat["pnns_groups_1"].isna() | (resultat["pnns_groups_1"].astype(str).str.strip() == "")
    resultat.loc[mask_rayon_manquant, "pnns_groups_1"] = "unknown"
    details["rayon_manquant_unknown"] = int(mask_rayon_manquant.sum())

    # Gestion du drapeau 'categorie_manquant'
    mask_main_manquant = resultat["main_category"].isna() | (resultat["main_category"].astype(str).str.strip() == "")
    resultat.loc[mask_main_manquant, "main_category"] = np.nan
    resultat["main_categorie_manquant"] = mask_main_manquant
    details["drapeau_categorie_vide_ajoute"] = int(mask_main_manquant.sum())
    
    # Extraction du dernier tag
    def extraire_dernier_tag(text):
        if pd.isna(text):
            return pd.NA

        tags = [t.strip() for t in text.split(",") if t.strip()]
        return tags[-1] if tags else np.nan

    # vérifier s'il y a au moins une ligne qui a besoin d'être traitée
    if mask_main_manquant.any():
        resultat.loc[mask_main_manquant, "main_category"] = resultat.loc[mask_main_manquant, "categories_tags"].apply(extraire_dernier_tag)
        details["main_category_derivee"] = int(resultat.loc[mask_main_manquant, "main_category"].notna().sum())


    # Suppression des produits hors périmètre (inclassables)
    # Définition : Pas de catégories (vide) ET rayon == 'unknown'
    mask_hors_perimetre = resultat["main_category"].isna() & (resultat["pnns_groups_1"] == "unknown")
    details["inclassables_supprimes"] = int(mask_hors_perimetre.sum())
    resultat = resultat[~mask_hors_perimetre]

    # Calcul des lignes modifiées ou supprimées
    touchees = len(df) - len(resultat)
    # On ajoute au calcul les modifications internes sur les lignes conservées
    touchees += _lignes_modifiees(df.loc[df.index.isin(resultat.index)], resultat, ["pnns_groups_1", "main_category"])

    return resultat, CompteRendu("traiter_categories_vides", len(df), len(resultat), touchees, details)

def strategie_manquants(df: pd.DataFrame, strategie: dict[str, str]) -> tuple[pd.DataFrame, CompteRendu]:
    """
    Applique la stratégie de traitement des valeurs manquantes par colonne.
    
    Vocabulaire fermé autorisé : 
    - 'garder' : Laisse les NaN inchangés.
    - 'drapeau' : Crée une colonne booléenne <colonne>_manquant et garde le NaN.
    - 'constante:<v>' : Remplace les NaN par la valeur <v>.
    - 'supprimer_colonne' / 'supprimer la colonne' : Retire la colonne.
    - 'mediane_rayon' / 'mode' : Interdit ici (bloqué post-split).
    """
    resultat = df.copy()
    details: dict[str, int] = {}
    
    colonnes_traitees = 0
    colonnes_supprimees = 0
    drapeaux_crees = 0
    lignes_nutriments_supprimees = 0
    
    decisions_valides = {'garder', 'drapeau', 'supprimer_colonne', 'mediane_rayon', 'mode'}

    # Initialisation des colonnes drapeaux
    resultat[FLAG_COLUMNS] = False

    # Application de la stratégie colonne par colonne
    for col, decision in strategie.items():
        if col not in resultat.columns:
            continue
            
        is_constante = decision.startswith("constante:")
        if not is_constante and decision not in decisions_valides:
            raise ValueError(f"Décision inconnue '{decision}' pour la colonne '{col}'.")
        
        if decision == 'garder':
            continue
            
        elif decision == 'drapeau':
            resultat[f"{col}_manquant"] = resultat[col].isna()
            drapeaux_crees += 1
            colonnes_traitees += 1
            
        elif is_constante:
            valeur_str = decision.split(":", 1)[1]
            try:
                valeur = float(valeur_str) if '.' in valeur_str else int(valeur_str)
            except ValueError:
                valeur = valeur_str
            resultat[col] = resultat[col].fillna(valeur)
            colonnes_traitees += 1
            
        elif decision == 'supprimer_colonne':
            resultat = resultat.drop(columns=[col])
            colonnes_supprimees += 1
            
        # elif decision in ['mediane_rayon', 'mode']:
        #     warnings.warn(
        #         f"L'imputation statistique ({decision}) pour '{col}' a été ignorée avant le split Train/Test.",
        #         UserWarning
        #     )

    # Suppression des lignes sans aucun nutriment clé
    taille_avant = len(resultat)
    resultat = resultat.dropna(subset=CSV_SELECTED_NUTRIMENT_COLUMNS, how='all')
    lignes_nutriments_supprimees = taille_avant - len(resultat)

    # Suppression des lignes completeness < 0.25
    taille_avant_filtre = len(resultat)
    resultat = resultat[resultat["completeness"] >= 0.25]
    lignes_completeness_inf_025_supprimees = taille_avant_filtre - len(resultat)

    # On identifie les colonnes et les INDEX (lignes) présents dans les deux DataFrames
    colonnes_communes = [c for c in df.columns if c in resultat.columns]
    index_communs = df.index.intersection(resultat.index)
    
    # On extrait des sous-ensembles strictement identiques en termes de labels (lignes et colonnes)
    df_aligne = df.loc[index_communs, colonnes_communes]
    resultat_aligne = resultat.loc[index_communs, colonnes_communes]

    # L'appel à _lignes_modifiees se fait désormais sans risque de désalignement
    touchees = _lignes_modifiees(df_aligne, resultat_aligne, colonnes_communes)
    
    # Si des lignes entières ont été supprimées, elles comptent comme touchées
    if lignes_nutriments_supprimees > 0:
        touchees += lignes_nutriments_supprimees

    details = {
        "colonnes_analysees": len(strategie),
        "colonnes_traitees": colonnes_traitees,
        "colonnes_supprimees": colonnes_supprimees,
        "drapeaux_crees": drapeaux_crees,
        "lignes_nutriments_cles_supprimees": lignes_nutriments_supprimees,
        "lignes_completeness_inf_025_supprimees": lignes_completeness_inf_025_supprimees

    }

    return resultat, CompteRendu("strategie_manquants", len(df), len(resultat), touchees, details)

def nettoyer(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    cr_list = []

    # 1 ligne pnns_groups_1 = 'italie' ???
    masque_italie = df["pnns_groups_1"] == "italie"
    df = df.loc[~masque_italie]

    df, cr = normaliser_unites(df)
    cr_list.append(cr)

    df, cr = borner_nutriments(df)
    cr_list.append(cr)

    df, cr = corriger_energie(df)
    cr_list.append(cr)

    df, cr = dedupliquer_codes(df)
    cr_list.append(cr)

    df, cr = traiter_categories_vides(df)
    cr_list.append(cr)

    df, cr = normaliser_textes(df)
    cr_list.append(cr)

    df, cr = typer_colonnes(df)
    cr_list.append(cr)

    df, cr = strategie_manquants(df, STRATEGIE_PAR_DEFAUT)
    cr_list.append(cr)

    return df, cr_list

"""
écrit docs/data/rapport_nettoyage.md avec : volumétrie avant / après (lignes, colonnes, codes distincts),
lignes touchées par règle (tableau, une ligne par compte rendu,
détail des sous-règles),
anomalies métier avant / après (mêmes définitions que le diagnostic du matin),
manquants avant / après sur les colonnes clés, produits par rayon après nettoyage,
colonnes ajoutées et retirées. En tête : la date, la source, le crédit Open Food Facts.
"""
def generer_rapport(avant: pd.DataFrame, apres: pd.DataFrame, journal: list[CompteRendu], chemin: str) -> None:
    """
    Génère un fichier Markdown de manière idempotente.
    Le fichier est recréé à chaque appel avec le contenu exact fourni.
    """
    chemin = Path(chemin)

    lignes = ["""
---
### Crédits
Données issues de la base de données ouverte [Open Food Facts][https://openfoodfacts.org](https://openfoodfacts.org).  
Ces données sont publiées sous la licence [Open Database License (ODbL)][https://opendatacommons.org](https://opendatacommons.org).
    """]

    date = datetime.now().strftime("%d/%m/%Y à %H:%M")
    lignes.append(f"**Généré le :** {date}")

    lignes.append(f"""
### Volumetrie
- **Avant:** {avant.shape[0]} lignes, {avant.shape[1]} colonnes
- **Après:** {apres.shape[0]} lignes, {apres.shape[1]} colonnes
    """)

    lignes.append("### Compte rendu du nettoyage")
    for cr in journal:
        lignes.append(f"""
**Règle:** {cr.regle}  
**Avant:** {cr.lignes_avant} lignes  
**Après:** {cr.lignes_apres} lignes  
**Modifiée(s):** {cr.lignes_touchees} lignes(s)  
**Détails:**  
{'  \n'.join(f'{k}: {v}' for k, v in cr.details.items())}
        """)
        
    texte_final = "\n".join(lignes)
    chemin.write_text(texte_final, encoding="utf-8")


TOUTES_LES_REGLES = [dedupliquer_codes, borner_nutriments] # typer_colonnes
REGLE_NORMALISER_UNITE = [normaliser_unites]
REGLE_CORRIGER_ENERGIE = [corriger_energie]
REGLE_CATEGORIES_VIDE = [traiter_categories_vides]
REGLE_NORMALISER_TEXTE = [normaliser_textes]
