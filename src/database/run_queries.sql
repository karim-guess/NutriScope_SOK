-- @nom: comptage_par_rayon
SELECT 
    rayon,
    COUNT(*) AS nb_produits,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS part_pourcentage
FROM produits
GROUP BY rayon;

-- @nom: completude
SELECT 
    rayon,
    ROUND(COUNT(CASE WHEN nutriscore_grade IN ('a', 'b', 'c', 'd', 'e') THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_nutriscore,
    ROUND(COUNT(CASE WHEN "energy-kcal_100g" IS NOT NULL 
                      AND fat_100g IS NOT NULL 
                      AND "saturated-fat_100g" IS NOT NULL 
                      AND carbohydrates_100g IS NOT NULL 
                      AND sugars_100g IS NOT NULL 
                      AND proteins_100g IS NOT NULL 
                      AND salt_100g IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_7_nutriments,
    ROUND(COUNT(main_category) * 100.0 / COUNT(*), 2) AS pct_categories
FROM produits
GROUP BY rayon;

-- @nom: doublons
SELECT 'codes_en_double' AS indicateur, COUNT(*) - COUNT(DISTINCT code) AS valeur FROM produits
UNION ALL
SELECT 'couples_nom_marque_repetes' AS indicateur, COUNT(*) FROM (
    SELECT product_name, brands FROM produits GROUP BY product_name, brands HAVING COUNT(*) > 1
) t;

-- @nom: bornes_et_coherences
SELECT 'nutriment_hors_0_100' AS anomalie, COUNT(*) AS nb_lignes FROM produits WHERE fat_100g NOT BETWEEN 0 AND 100 OR "saturated-fat_100g" NOT BETWEEN 0 AND 100 OR carbohydrates_100g NOT BETWEEN 0 AND 100 OR sugars_100g NOT BETWEEN 0 AND 100 OR proteins_100g NOT BETWEEN 0 AND 100 OR salt_100g NOT BETWEEN 0 AND 100
UNION ALL
SELECT 'energie_hors_0_900' AS anomalie, COUNT(*) AS nb_lignes FROM produits WHERE "energy-kcal_100g" NOT BETWEEN 0 AND 900
UNION ALL
SELECT 'sucres_superieur_glucides' AS anomalie, COUNT(*) AS nb_lignes FROM produits WHERE sugars_100g > carbohydrates_100g
UNION ALL
SELECT 'satures_superieur_lipides' AS anomalie, COUNT(*) AS nb_lignes FROM produits WHERE "saturated-fat_100g" > fat_100g
UNION ALL
SELECT 'sel_different_sodium_x2_5' AS anomalie, COUNT(*) AS nb_lignes FROM produits WHERE ABS(salt_100g - (sodium_100g * 2.5)) > 0.01
UNION ALL
SELECT 'energie_nulle_avec_macronutriments' AS anomalie, COUNT(*) AS nb_lignes FROM produits WHERE "energy-kcal_100g" = 0 AND (fat_100g > 0 OR carbohydrates_100g > 0 OR proteins_100g > 0);

-- @nom: distribution_nutriscore
SELECT 
    COALESCE(nutriscore_grade, 'unknown') AS grade,
    COUNT(*) AS nb_produits,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS part_pourcentage,
    AVG("energy-kcal_100g") AS score_moyen_energie
FROM produits
GROUP BY nutriscore_grade;
