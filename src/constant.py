CSV_SELECTED_COLUMNS = [
    'code',
    'product_name',
    'brands',
    'quantity',
    'categories_tags',
    'main_category',
    'pnns_groups_1',
    'pnns_groups_2',
    'countries_tags',
    'labels_tags',
    'stores',
    'ingredients_text',
    'allergens',
    'additives_n',
    'nova_group',
    'nutriscore_score',
    'nutriscore_grade',
    'environmental_score_grade',
    'serving_size',
    'completeness',
    'created_t',
    'image_url'
]
FLAG_COLUMNS = [
    'product_name_manquant',
    'brands_manquant',
    'quantity_manquant',
    'categories_tags_manquant',
    'main_category_manquant',
    'ingredients_text_manquant',
    'allergens_manquant',
    'additives_n_manquant',
    'fat_100g_manquant',
    'saturated_fat_100g_manquant',
    'carbohydrates_100g_manquant',
    'fiber_100g_manquant',
    'proteins_100g_manquant',
    'fruits_vegetables_legumes_100g_manquant'
]
FINAL_SELECTED_COLUMNS = [
    'code',
    'product_name',
    'brands',
    'quantity',
    'categories_tags',
    'main_category',
    'pnns_groups_1',
    'pnns_groups_2',
    'countries_tags',
    'ingredients_text',
    'allergens',
    'additives_n',
    'nova_group',
    'nutriscore_score',
    'nutriscore_grade',
    'environmental_score_grade',
    'serving_size',
    'completeness',
    'created_t',
    'image_url'
]
CSV_SELECTED_NUTRIMENT_COLUMNS = [
    'energy-kcal_100g',
    'energy_100g',
    'fat_100g',
    'saturated-fat_100g',
    'carbohydrates_100g',
    'sugars_100g',
    'fiber_100g',
    'proteins_100g',
    'salt_100g',
    'sodium_100g',
    'fruits-vegetables-legumes_100g'
]
CSV_SELECTED_CATEGORIES = [
    'Sugary snacks',
    'Fish Meat Eggs',
    'Cereals and potatoes',
    'Milk and dairy products',
    'Beverages',
    'Fat and sauces',
    'Composite foods',
    'Fruits and vegetables',
    'Salty snacks'
]
TEXT_TYPE = [
    'code',
    'product_name',
    'brands',
    'quantity',
    'categories_tags',
    'main_category',
    'pnns_groups_1',
    'pnns_groups_2',
    'countries_tags',
    'labels_tags',
    'stores',
    'ingredients_text',
    'allergens',
    'nutriscore_grade',
    'environmental_score_grade',
    'serving_size',
    'image_url'
]
NUMERIC_TYPE = [
    "additives_n",
    "nova_group",
    "nutriscore_score",
    "completeness"
]
MORE_10_PERCENT_MISSING = [
    'product_name',
    'brands',
    'quantity',
    'categories_tags',
    'main_category',
    'labels_tags',
    'stores',
    'ingredients_text',
    'allergens',
    'additives_n',
    'nova_group',
    'nutriscore_score',
    'serving_size',
    'energy-kcal_100g',
    'energy_100g',
    'fat_100g',
    'saturated-fat_100g',
    'carbohydrates_100g',
    'sugars_100g',
    'fiber_100g',
    'proteins_100g',
    'salt_100g',
    'sodium_100g',
    'fruits-vegetables-legumes_100g'
]
STRATEGIE_PAR_DEFAUT = {
    'product_name': 'drapeau', # NA
    'brands': 'drapeau', # NA, MAR
    'quantity': 'drapeau', # NA, MNAR
    'categories_tags': 'drapeau', # regle metier (supprimer si main_category + categories_tags = NA), NA, MAR / MNAR
    'main_category': 'drapeau', # substitution par categories_tags
    'labels_tags': 'supprimer_colonne',
    'stores': 'supprimer_colonne',
    'ingredients_text': 'drapeau', # NA, MAR
    'allergens': 'drapeau', # NA, MNAR
    'additives_n': 'drapeau', # NA, MAR
    'nova_group': 'mode', # MAR
    'nutriscore_score': 'garder', # unknown -> NA, MAR
    'serving_size': 'garder', # feature derivee, NA si illisible, MCAR-proche
    'energy-kcal_100g': 'mediane_rayon', # imputation metier, MAR
    'energy_100g': 'garder', # imputation metier
    'fat_100g': 'drapeau', # NA, MNAR
    'saturated-fat_100g': 'drapeau', # NA, MNAR
    'carbohydrates_100g': 'drapeau', # NA, MNAR
    'sugars_100g': 'garder', # NA, MAR
    'fiber_100g': 'drapeau', # NA, MNAR
    'proteins_100g': 'drapeau', # NA, MNAR
    'salt_100g': 'garder', # imputation metier (calcul), NA, MAR
    'sodium_100g': 'garder', # imputation metier (calcul)
    'fruits-vegetables-legumes_100g': 'drapeau' # NA, MNAR
}