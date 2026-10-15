-- @nom: comptage_par_rayon
SELECT 
    COALESCE(pnns_groups_1, 'unknown') AS rayon,
    COUNT(*) AS nb_produits,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS part_pourcentage
FROM product
GROUP BY pnns_groups_1
ORDER BY nb_produits DESC;


-- @nom: completude
SELECT 
    COALESCE(p.pnns_groups_1, 'unknown') AS rayon,
    ROUND(COUNT(CASE WHEN p.nutriscore_grade IN ('a', 'b', 'c', 'd', 'e') THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_nutriscore,
    ROUND(COUNT(CASE WHEN n.energy_kcal_100g IS NOT NULL 
                      AND n.fat_100g IS NOT NULL 
                      AND n.saturated_fat_100g IS NOT NULL 
                      AND n.carbohydrates_100g IS NOT NULL 
                      AND n.sugars_100g IS NOT NULL 
                      AND n.proteins_100g IS NOT NULL 
                      AND n.salt_100g IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_7_nutriments,
    ROUND(COUNT(p.main_category) * 100.0 / COUNT(*), 2) AS pct_categories
FROM product p
LEFT JOIN nutriment n ON p.id = n.product_id
GROUP BY p.pnns_groups_1;


-- @nom: doublons
SELECT 'codes_en_double' AS indicateur, COUNT(*) - COUNT(DISTINCT code) AS valeur FROM product
UNION ALL
SELECT 'couples_nom_marque_repetes' AS indicateur, COUNT(*) FROM (
    SELECT name, brands FROM product GROUP BY name, brands HAVING COUNT(*) > 1
) t;


-- @nom: bornes_et_coherences
SELECT 'nutriment_hors_0_100' AS anomalie, COUNT(*) AS nb_lignes FROM nutriment WHERE fat_100g NOT BETWEEN 0 AND 100 OR saturated_fat_100g NOT BETWEEN 0 AND 100 OR carbohydrates_100g NOT BETWEEN 0 AND 100 OR sugars_100g NOT BETWEEN 0 AND 100 OR proteins_100g NOT BETWEEN 0 AND 100 OR salt_100g NOT BETWEEN 0 AND 100
UNION ALL
SELECT 'energie_hors_0_900' AS anomalie, COUNT(*) AS nb_lignes FROM nutriment WHERE energy_kcal_100g NOT BETWEEN 0 AND 900
UNION ALL
SELECT 'sucres_superieur_glucides' AS anomalie, COUNT(*) AS nb_lignes FROM nutriment WHERE sugars_100g > carbohydrates_100g
UNION ALL
SELECT 'satures_superieur_lipides' AS anomalie, COUNT(*) AS nb_lignes FROM nutriment WHERE saturated_fat_100g > fat_100g
UNION ALL
SELECT 'sel_different_sodium_x2_5' AS anomalie, COUNT(*) AS nb_lignes FROM nutriment WHERE ABS(salt_100g - (sodium_100g * 2.5)) > 0.01
UNION ALL
SELECT 'energie_nulle_avec_macronutriments' AS anomalie, COUNT(*) AS nb_lignes FROM nutriment WHERE energy_kcal_100g = 0 AND (fat_100g > 0 OR carbohydrates_100g > 0 OR proteins_100g > 0);


-- @nom: distribution_nutriscore
SELECT 
    COALESCE(p.nutriscore_grade, 'unknown') AS grade,
    COUNT(*) AS nb_produits,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS part_pourcentage,
    ROUND(AVG(n.energy_kcal_100g)::numeric, 1) AS score_moyen_energie
FROM product p
LEFT JOIN nutriment n ON p.id = n.product_id
GROUP BY p.nutriscore_grade
ORDER BY grade ASC;
