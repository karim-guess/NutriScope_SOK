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
    name TEXT NULL,
    tags TEXT NULL
);

-- Création de la table 'product'
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NULL,
    countries TEXT NULL,
    nutriscore_score REAL NULL, 
    nutriscore_grade VARCHAR(1) NULL CHECK (nutriscore_grade IN ('A', 'B', 'C', 'D', 'E')),
    category_id INT NULL,
    brand_id INT NULL,
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL,
    CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) REFERENCES brand(id) ON DELETE SET NULL
);

-- Création d'un index unique sur le code produit pour l'idempotence et les performances
CREATE UNIQUE INDEX IF NOT EXISTS uq_product_code ON product(code);

-- Création de la table 'nutriment_100g'
CREATE TABLE nutriment (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    energy REAL NULL,
    energy_unit VARCHAR(255) NULL,
    sugars REAL NULL,
    sugars_unit VARCHAR(255) NULL,
    saturated_fat REAL NULL,
    saturated_fat_unit VARCHAR(255) NULL,
    salt REAL NULL,
    salt_unit VARCHAR(255) NULL,
    sodium REAL NULL,
    sodium_unit VARCHAR(255) NULL,
    fiber REAL NULL,
    fiber_unit VARCHAR(255) NULL,
    proteins REAL NULL,
    proteins_unit VARCHAR(255) NULL,
    fruits_vegetables_legumes REAL NULL,
    fruits_vegetables_legumes_unit VARCHAR(255) NULL,
    fat REAL NULL,
    fat_unit VARCHAR(255) NULL,
    CONSTRAINT fk_nutriment_product FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    CONSTRAINT uq_nutriment_product UNIQUE (product_id)
);