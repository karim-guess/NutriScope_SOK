## 1. Contexte et objectif du périmètre

NutriScope a pour vocation d'accompagner les consommateurs lors de leurs courses alimentaires en magasin :
1. En analysant la qualité nutritionnelle d'un produit scanné via son code-barres.
2. En proposant des alternatives plus saines et comparables au sein du même rayon.

Face à la volumétrie brute du catalogue Open Food Facts (~7 Go, 111 colonnes, plusieurs millions de lignes), l'objectif de ce document est de formaliser un **périmètre cohérent et exempt de bruit**, aligné sur les contraintes fonctionnelles et techniques du cahier des charges.

---

## 2. Périmètre géographique et volumétrie globale

Le périmètre cible retenu est restreint au **marché français** via le filtre :
`countries_tags => 'en:france'`.

### Résultats du profiling initial (Périmètre France) :
* **Nombre total de fiches produits brutes :** 1 247 336
* **Codes-barres uniques :** 1 247 309
* **Collisions de codes-barres (doublons) :** 27 codes (54 lignes concernées, soit 0,004 % du catalogue).
* **Part des produits avec Nutri-Score officiel (A à E) :** 37,18 % (463 757 références).
* **Part des produits non exploitables pour le score :** 62,82 % (783 579 références réparties entre `UNKNOWN`, `NOT-APPLICABLE` et `NULL`).

---

## 3 Analyse unitaire des colonnes par distributions, cardinalités, taux de manquants 

REJETÉE | CONSERVÉE | À REFORMATER / REJET EN L'ÉTAT:  
→ Périmètre: colonne "code" dédoublonnées, filtre "en:france"   

**additives_n** (numérique)  
REJETÉE. Avec 71.2% de valeurs manquantes

**additives_tags** (liste)  
REJETÉE. Avec 71.2% de valeurs manquantes

**allergens_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 3595 éléments uniques. 

**brands_tags** (liste)  
REJETÉE. Avec 43.5% de valeurs manquantes

**brands** (categoriel)  
REJETÉE. Avec 43.5% de valeurs manquantes

**categories** (liste)  
REJETÉE. Avec 51.5% de valeurs manquantes

**categories_tags** (liste)  
REJETÉE. Avec 47.0% de valeurs manquantes

**categories_properties** (dictionnaire)  
CONSERVÉE. Type [dictionnaire] contenant 3 clés uniques

**checkers_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 33 éléments uniques.

**ciqual_food_name_tags** (liste)  
REJETÉE. Avec 47.2% de valeurs manquantes

**code**  
identifiant unique

**compared_to_category** (categoriel)  
REJETÉE. Avec 51.1% de valeurs manquantes

**complete** (numerique)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**completeness** (numerique)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**correctors_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 394574 éléments uniques.

**countries_tags**  
filtre pays

**created_t** (numerique)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**creator** (categoriel)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**data_quality_errors_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 187 éléments uniques.

**data_quality_info_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 38 éléments uniques.

**data_quality_warnings_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 722 éléments uniques.

**data_sources_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 482 éléments uniques.

**environmental_score_data** (categoriel)  
À REFORMATER / REJET EN L'ÉTAT. La cardinalité est trop élevée (1222164 modalités uniques).

**environmental_score_grade** (categoriel)  
CONSERVÉE. Le taux de complétude (98.0%) et la variance sont optimaux.

**environmental_score_score** (numerique)  
REJETÉE. Avec 64.7% de valeurs manquantes

**environmental_score_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 9 éléments uniques.

**editors** (liste)  
REJETÉE. Avec 96.7% de valeurs manquantes

**emb_codes_tags** (liste)  
REJETÉE. Avec 66.8% de valeurs manquantes

**emb_codes** (categoriel)  
REJETÉE. Avec 70.0% de valeurs manquantes

**entry_dates_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 5425 éléments uniques.

**food_groups_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 56 éléments uniques.

**generic_name** (liste)  
CONSERVÉE. Type [liste] exploitable avec 172363 éléments uniques.

**images** (liste)  
CONSERVÉE. Type [liste] exploitable avec 5403543 éléments uniques.

**informers_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 789473 éléments uniques.

**ingredients_analysis_tags** (liste)  
REJETÉE. Avec 70.0% de valeurs manquantes

**ingredients_from_palm_oil_n** (numerique)  
REJETÉE. Avec 76.0% de valeurs manquantes

**ingredients_n** (numerique)  
REJETÉE. Avec 71.2% de valeurs manquantes

**ingredients_original_tags** (liste)  
REJETÉE. Avec 71.2% de valeurs manquantes

**ingredients_percent_analysis** (numerique)  
REJETÉE. Avec 73.4% de valeurs manquantes

**ingredients_tags** (liste)  
REJETÉE. Avec 71.2% de valeurs manquantes

**ingredients_text** (liste)  
CONSERVÉE. Type [liste] exploitable avec 942763 éléments uniques.

**ingredients_with_specified_percent_n** (numerique)  
REJETÉE. Avec 71.2% de valeurs manquantes

**ingredients_with_unspecified_percent_n** (numerique)  
REJETÉE. Avec 71.2% de valeurs manquantes

**ingredients_without_ciqual_codes_n** (numerique)  
REJETÉE. Avec 71.2% de valeurs manquantes

**ingredients_without_ciqual_codes** (liste)  
REJETÉE. Avec 71.2% de valeurs manquantes

**'ingredients** (categoriel)  
REJETÉE. Avec 71.2% de valeurs manquantes

**known_ingredients_n** (numerique)  
REJETÉE. Avec 71.2% de valeurs manquantes

**labels_tags** (liste)  
REJETÉE. Avec 45.5% de valeurs manquantes

**labels** (categoriel)  
REJETÉE. Avec 50.7% de valeurs manquantes

**lang** (categoriel)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**languages_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 154 éléments uniques.

**last_edit_dates_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 3817 éléments uniques.

**last_editor** (categoriel)  
CONSERVÉE. Le taux de complétude (99.0%) et la variance sont optimaux.

**last_image_t** (numerique)  
CONSERVÉE. Le taux de complétude (95.4%) et la variance sont optimaux.

**last_modified_by** (categoriel)  
CONSERVÉE. Le taux de complétude (98.9%) et la variance sont optimaux.

**last_modified_t** (numerique)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**last_updated_t** (numerique)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**link** (categoriel)  
REJETÉE. Avec 70.3% de valeurs manquantes

**main_countries_tags** (liste)  
REJETÉE. La variance est nulle ou quasi-nulle (cardinalité de 0).

**manufacturing_places_tags** (liste)  
REJETÉE. Avec 69.5% de valeurs manquantes

**manufacturing_places** (categoriel)  
REJETÉE. Avec 72.4% de valeurs manquantes

**max_imgid** (numerique)  
CONSERVÉE. Le taux de complétude (95.4%) et la variance sont optimaux.

**minerals_tags** (liste)  
REJETÉE. Avec 40.1% de valeurs manquantes

**misc_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 1598 éléments uniques.

**new_additives_n** (numerique)  
REJETÉE. Avec 100.0% de valeurs manquantes

**no_nutrition_data** (categoriel)  
REJETÉE. Avec 94.5% de valeurs manquantes

**nova_group** (numerique)  
REJETÉE. Avec 73.3% de valeurs manquantes

**nova_groups_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 6 éléments uniques.

**nova_groups** (categoriel)  
REJETÉE. Avec 73.3% de valeurs manquantes

**nucleotides_tags** (liste)  
REJETÉE. Avec 40.1% de valeurs manquantes

**nutrient_levels_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 12 éléments uniques.

**nutriments** (liste)  
CONSERVÉE. Type [liste] exploitable avec 2275529 éléments uniques.

**nutriscore_grade** (categoriel)  
CONSERVÉE. Le taux de complétude (98.0%) et la variance sont optimaux.

**nutriscore_score** (numerique)  
REJETÉE. Avec 62.8% de valeurs manquantes

**nutrition_data_per** (categoriel)  
REJETÉE. Avec 72.8% de valeurs manquantes

**obsolete** (numerique)  
REJETÉE. La variance est nulle ou quasi-nulle (cardinalité de 1).

**origins_tags** (liste)  
REJETÉE. Avec 69.2% de valeurs manquantes

**origins** (categoriel)  
REJETÉE. Avec 72.2% de valeurs manquantes

**owner_fields** (liste)  
REJETÉE. Avec 93.5% de valeurs manquantes

**owner** (categoriel)  
REJETÉE. Avec 93.5% de valeurs manquantes

**packagings_complete** (categoriel)  
REJETÉE. Avec 85.6% de valeurs manquantes

**packaging_recycling_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 567 éléments uniques.

**packaging_shapes_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 820 éléments uniques.

**packaging_tags** (liste)  
REJETÉE. Avec 74.1% de valeurs manquantes

**packaging_text** (liste)  
CONSERVÉE. Type [liste] exploitable avec 18992 éléments uniques.

**packaging** (categoriel)  
REJETÉE. Avec 74.1% de valeurs manquantes

**packagings** (liste)  
CONSERVÉE. Type [liste] exploitable avec 29275 éléments uniques.

**photographers** (liste)  
REJETÉE. Avec 99.7% de valeurs manquantes

**popularity_key** (numerique)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**popularity_tags** (liste)  
REJETÉE. Avec 55.2% de valeurs manquantes

**product_name** (liste)  
CONSERVÉE. Type [liste] exploitable avec 1575667 éléments uniques.

**product_quantity_unit** (categoriel)  
REJETÉE. Avec 65.3% de valeurs manquantes

**product_quantity** (categoriel)  
REJETÉE. Avec 64.9% de valeurs manquantes

**purchase_places_tags** (liste)  
REJETÉE. Avec 70.2% de valeurs manquantes

**quantity** (categoriel)  
REJETÉE. Avec 54.4% de valeurs manquantes

**rev** (numerique)  
CONSERVÉE. Le taux de complétude (100.0%) et la variance sont optimaux.

**scans_n** (numerique)  
REJETÉE. Avec 54.9% de valeurs manquantes

**serving_quantity** (categoriel)  
REJETÉE. Avec 89.0% de valeurs manquantes

**serving_size** (categoriel)  
REJETÉE. Avec 88.7% de valeurs manquantes

**states_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 40 éléments uniques.

**stores_tags** (liste)  
REJETÉE. Avec 65.8% de valeurs manquantes

**stores** (categoriel)  
REJETÉE. Avec 69.3% de valeurs manquantes

**traces_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 4433 éléments uniques.

**unique_scans_n** (numerique)  
REJETÉE. Avec 54.9% de valeurs manquantes

**unknown_ingredients_n** (numerique)  
REJETÉE. Avec 71.2% de valeurs manquantes

**unknown_nutrients_tags** (liste)  
CONSERVÉE. Type [liste] exploitable avec 704 éléments uniques.

**vitamins_tags** (liste)  
REJETÉE. Avec 40.1% de valeurs manquantes

**with_non_nutritive_sweeteners** (numerique)  
REJETÉE. Avec 99.4% de valeurs manquantes

**with_sweeteners** (numerique)  
REJETÉE. Avec 100.0% de valeurs manquantes

---

## 4. Inventaire des colonnes : retenues vs écartées

Sur les 111 colonnes du schéma Parquet source, nous ne conserverons que les colonnes essentielles aux fonctionnalités cibles :

### Colonnes conservées (14 colonnes)

| Colonne | Type Parquet | Complétude France | Usage fonctionnel NutriScope |
|---|---|---|---|
| `code` | `string` | 100 % | Identifiant unique du produit, recherche par code-barres / scan. |
| `countries_tags` | `list` | 100 % | Le pays où le produit est vendu. |
| `product_name` | `list` / `string` | 100 % | Affichage du nom commercial du produit. |
| `brands` | `string` | 56,47 % | Affichage de la marque. |
| `brands_tags` | `list` | 56,47 % | Version standardisée de la marque. |
| `categories` | `list` | 48,5 % | Catégorie de l'aliment. |
| `categories_tags` | `list` | 53,02 % | Version standardisée de la catégorie, facilite les regroupements. |
| `nutriscore_grade` | `string` | 97,99 % | Affichage du score (A → E). |
| `nutriscore_score` | `int` | 37,2 % | Le score brut calculé (plus il est bas, meilleur est le produit). |
| `nutriments` | `list` | 75,17 % | Extraction des 8 nutriments clés (énergie, sucres, sel, etc.). |
| `images` | `list` | 100 % | Récupération des images pour le front. |
| `ingredients_text` | `list` / `string` | 100 % | La liste des ingrédients. |
| `allergens_tags` | `list` | 98 % | Alertes allergènes pour les produits. |
| `quantity` | `string` | ~60 % | Affichage du conditionnement (ex. « 500 g »). |

### Colonnes explicitement écartées et justifications

| Colonne(s) | Justification de l'exclusion |
|---|---|
| `creator`, `editors`, `last_modified_by` | Pas utile. |
| `environmental_score_*` (Eco-Score) | Hors périmètre nutritionnel. |
| `packaging_*`, `packagings` | Complétude trop faible (trop de manquants). |
| `ciqual_food_code`, `agribalyse_*` | Pas utile. |

---

## 5. Rayons et catégories retenus (5 à 8 catégories cibles)

Pour garantir la pertinence du moteur de recommandation nutritionnelle et éviter les suggestions aberrantes, le catalogue NutriScope est restreint à **6 rayons du quotidien** présentant une complétude nutritionnelle supérieure à 80 % :

| # | Rayon cible | Tag Open Food Facts | Volumétrie France | Complétude Nutri-Score (%) | Justification métier & IA |
|---|---|---|---|---|---|
| 1 | **Biscuits et gâteaux** | `en:biscuits-and-cakes` | 39 849 | **90,2 %** | Forte dispersion de notes, cas idéal pour la substitution sucrée. |
| 2 | **Plats préparés** | `en:meals` | 45 666 | **89,2 %** | Forte disparité en sel et graisses saturées. |
| 3 | **Charcuterie & viandes préparées** | `en:prepared-meats` | 37 946 | **88,3 %** | Le sel et les nitrites. |
| 4 | **Snacks sucrés** | `en:sweet-snacks` | 90 947 | **85,7 %** | Sucre. |
| 5 | **Céréales et dérivés** | `en:cereals-and-potatoes` | 50 203 | **84,9 %** | Produits du petit-déjeuner et féculents. |
| 6 | **Produits laitiers** | `en:dairies` | 59 861 | **83,9 %** | Yaourts, desserts lactés, fromages. |

---

## 6. Mentions légales et crédits

Conformément aux exigences de réutilisation :
* Les données nutritionnelles et textuelles sont issues d'**Open Food Facts** et exploitées sous licence **ODbL** (Open Database License).
* Les visuels associés sont hébergés via le bucket public Open Food Facts sous licence **CC-BY-SA 3.0**.
* Tout jeu de données dérivé ou enrichi par NutriScope sera redistribué sous licence compatible.