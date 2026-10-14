# Rapport de Contrôle Qualité

Ce rapport valide la cohérence des données issues du stockage Parquet partitionné.

## comptage_par_rayon

| rayon | nb_produits | part_pourcentage |
| --- | --- | --- |
| alcoholic-beverages | 8330 | 1.55 |
| fat-and-sauces | 35688 | 6.66 |
| fish-meat-eggs | 82171 | 15.33 |
| cereals-and-potatoes | 51303 | 9.57 |
| unknown | 54996 | 10.26 |
| baby-foods | 2526 | 0.47 |
| fruits-and-vegetables | 33504 | 6.25 |
| composite-foods | 38239 | 7.13 |
| beverages | 42678 | 7.96 |
| milk-and-dairy-products | 56237 | 10.49 |
| sugary-snacks | 101934 | 19.01 |
| salty-snacks | 28582 | 5.33 |

## completude

| rayon | pct_nutriscore | pct_7_nutriments | pct_categories |
| --- | --- | --- | --- |
| sugary-snacks | 89.97 | 92.24 | 100.0 |
| alcoholic-beverages | 0.58 | 23.71 | 100.0 |
| fat-and-sauces | 87.27 | 93.26 | 100.0 |
| fish-meat-eggs | 94.38 | 94.67 | 100.0 |
| unknown | 68.43 | 87.04 | 100.0 |
| baby-foods | 0.0 | 91.88 | 100.0 |
| composite-foods | 94.78 | 96.49 | 100.0 |
| salty-snacks | 94.83 | 95.33 | 100.0 |
| beverages | 75.89 | 84.84 | 100.0 |
| cereals-and-potatoes | 89.64 | 92.95 | 100.0 |
| fruits-and-vegetables | 86.88 | 88.4 | 100.0 |
| milk-and-dairy-products | 94.45 | 95.02 | 100.0 |

## doublons

| indicateur | valeur |
| --- | --- |
| codes_en_double | 0 |
| couples_nom_marque_repetes | 34088 |

## bornes_et_coherences

| anomalie | nb_lignes |
| --- | --- |
| nutriment_hors_0_100 | 0 |
| energie_hors_0_900 | 17 |
| sucres_superieur_glucides | 256 |
| satures_superieur_lipides | 304 |
| sel_different_sodium_x2_5 | 952 |
| energie_nulle_avec_macronutriments | 2 |

## distribution_nutriscore

| grade | nb_produits | part_pourcentage | score_moyen_energie |
| --- | --- | --- | --- |
| b | 49497 | 9.23 | 232.35677906493748 |
| not-applicable | 26364 | 4.92 | 203.68599333671375 |
| d | 121920 | 22.74 | 291.53635272490413 |
| a | 62825 | 11.72 | 172.70869878505565 |
| unknown | 47787 | 8.91 | 257.4008806542544 |
| c | 95912 | 17.89 | 192.00368891264586 |
| e | 131883 | 24.6 | 389.01518107884203 |

