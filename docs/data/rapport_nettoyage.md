
---
### Crédits
Données issues de la base de données ouverte [Open Food Facts][https://openfoodfacts.org](https://openfoodfacts.org).  
Ces données sont publiées sous la licence [Open Database License (ODbL)][https://opendatacommons.org](https://opendatacommons.org).
    
**Généré le :** 05/10/2026 à 08:43

### Volumetrie
- **Avant:** 1261274 lignes, 33 colonnes
- **Après:** 536188 lignes, 48 colonnes
    
### Compte rendu du nettoyage

**Règle:** normaliser_unites  
**Avant:** 1235349 lignes  
**Après:** 1235349 lignes  
**Modifiée(s):** 119479 lignes(s)  
**Détails:**  
energy_kcal_100g_manquant_calcul_derivees: 322  
energy_kcal_100g_hors_borne_recalculees: 116190  
salt_100g_manquant_calcul_derivees: 0  
sodium_100g_manquant_calcul_derivees: 0  
sodium_100g_incoherent_recalculees: 3209
        

**Règle:** borner_nutriments  
**Avant:** 1235349 lignes  
**Après:** 1235349 lignes  
**Modifiée(s):** 1999 lignes(s)  
**Détails:**  
fat_100g_hors_bornes: 46  
saturated-fat_100g_hors_bornes: 20  
carbohydrates_100g_hors_bornes: 84  
sugars_100g_hors_bornes: 53  
proteins_100g_hors_bornes: 34  
salt_100g_hors_bornes: 60  
fruits-vegetables-legumes_100g_hors_bornes: 1154  
sugars_incoherent_glucides: 433  
saturated_incoherent_fat: 207
        

**Règle:** corriger_energie  
**Avant:** 1235349 lignes  
**Après:** 1235349 lignes  
**Modifiée(s):** 863927 lignes(s)  
**Détails:**  
energy_kcal_100g_nulles_recalculees: 286  
energy_kcal_100g_plus_900_recalculees: 132  
energy_kcal_100g_plus_900_invalidees: 81  
incoherentes_energy-kcal_100g_recalculees: 2659
        

**Règle:** dedupliquer_codes  
**Avant:** 1235349 lignes  
**Après:** 1235323 lignes  
**Modifiée(s):** 26 lignes(s)  
**Détails:**  
sans_code: 0  
doublons_supprimes: 26
        

**Règle:** traiter_categories_vides  
**Avant:** 1235323 lignes  
**Après:** 634321 lignes  
**Modifiée(s):** 601002 lignes(s)  
**Détails:**  
rayon_manquant_unknown: 0  
drapeau_categorie_vide_ajoute: 601003  
main_category_derivee: 1  
inclassables_supprimes: 601002
        

**Règle:** normaliser_textes  
**Avant:** 634321 lignes  
**Après:** 634321 lignes  
**Modifiée(s):** 612765 lignes(s)  
**Détails:**  
grades_unknown_nettoyes: 0  
noms_vides_nettoyes: 1  
marques_harmonisees: 42682
        

**Règle:** typer_colonnes  
**Avant:** 634321 lignes  
**Après:** 634321 lignes  
**Modifiée(s):** 0 lignes(s)  
**Détails:**  
statut: le DataFrame à été modifié
        

**Règle:** strategie_manquants  
**Avant:** 634321 lignes  
**Après:** 536188 lignes  
**Modifiée(s):** 98092 lignes(s)  
**Détails:**  
colonnes_analysees: 24  
colonnes_traitees: 14  
colonnes_supprimees: 2  
drapeaux_crees: 14  
lignes_nutriments_cles_supprimees: 98092  
lignes_completeness_inf_025_supprimees: 41
        