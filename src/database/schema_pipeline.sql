-- Script de création de la base de données nutriscope (PostgreSQL)

-- Suppression des tables si elles existent (ordre respectant les clés étrangères)
DROP TABLE IF EXISTS nutriment CASCADE;
DROP TABLE IF EXISTS brand CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS categories_tags CASCADE;
DROP TABLE IF EXISTS category_tag CASCADE;
DROP TABLE IF EXISTS category CASCADE;


-- Table des catégories
CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- Table des tags
CREATE TABLE category_tag (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Table d'association (Many-to-Many)
CREATE TABLE categories_tags (
    category_id INT NOT NULL,
    category_tag_id INT NOT NULL,
    PRIMARY KEY (category_id, category_tag_id),
    CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE,
    CONSTRAINT fk_category_tag FOREIGN KEY (category_tag_id) REFERENCES category_tag(id) ON DELETE CASCADE
);

-- Création de la table 'brand'
CREATE TABLE brand (
    id SERIAL PRIMARY KEY,
    name TEXT NULL
);

-- Création de la table 'product'
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NULL,
    created_t REAL NULL,
    countries_tags TEXT NULL,
    nutriscore_score REAL NULL, 
    nutriscore_grade TEXT NULL CHECK (nutriscore_grade IN ('a', 'b', 'c', 'd', 'e', 'unknown', 'not-applicable')),
    quantity TEXT NULL,
    brands TEXT NULL,
    categories_tags TEXT NULL,
    ingredients_text TEXT NULL,
    allergens TEXT NULL,
    serving_size TEXT NULL,
    additives_n REAL NULL,
    nova_group REAL NULL,
    pnns_groups_1 TEXT NULL,
    pnns_groups_2 TEXT NULL,
    environmental_score_grade TEXT NULL,
    completeness REAL NULL,
    main_category TEXT NULL,
    image_url TEXT NULL,
    category_id INT NULL,
    brand_id INT NULL,
    product_name_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    brands_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    quantity_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    categories_tags_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    main_category_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    ingredients_text_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    allergens_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    additives_n_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    fat_100g_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    saturated_fat_100g_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    carbohydrates_100g_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    fiber_100g_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    proteins_100g_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    fruits_vegetables_legumes_100g_manquant BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL,
    CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) REFERENCES brand(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_product_code ON product(code);

-- Création de la table 'nutriment_100g'
CREATE TABLE nutriment (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    energy_kcal_100g REAL NULL,
    energy_100g REAL NULL,
    fat_100g REAL NULL,
    saturated_fat_100g REAL NULL,
    carbohydrates_100g REAL NULL,
    sugars_100g REAL NULL,
    fiber_100g REAL NULL,
    proteins_100g REAL NULL,
    salt_100g REAL NULL,
    sodium_100g REAL NULL,
    fruits_vegetables_legumes_100g REAL NULL,
    CONSTRAINT fk_nutriment_product FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    CONSTRAINT uq_nutriment_product UNIQUE (product_id)
);

GRANT CONNECT ON DATABASE nutriscope TO nutriscope_app;
-- Autoriser l'accès au schéma
GRANT USAGE ON SCHEMA public TO nutriscope_app;
-- Donner les droits sur les tables déjà existantes
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nutriscope_app;
-- Faire en sorte que les tables créées PLUS TARD héritent des mêmes droits
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO nutriscope_app;
-- Appliquer les droits sur TOUTES les séquences actuelles de la base
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nutriscope_app;