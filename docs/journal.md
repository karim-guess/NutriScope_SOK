
***TP1:***  

**Format retenu, taille, date de l'export, pourquoi celui-là ?**  
Le format retenu est le format "parquet"

1. **Efficacité du stockage** : 70 à 90 % plus compact que les fichiers CSV
2. **Performances** : Opérations de lecture 5 à 10 fois plus rapides
3. **Typage sûr** : Préserve les types de données sans nécessiter d'analyse (parsing)

Comparaison des performances:

| Format | Taille fichier | Vitesse de lecture | Préservation des types | Compression |
|--------|-----------|------------|-------------------|-------------|
| CSV    | 100 MB    | 1.0x       | ❌                | ❌          |
| Parquet| 15 MB     | 5-10x      | ✅                | ✅          |

**Nombre total de lignes:**  
| | Nombre de lignes |  
|-|--------------------|
**CSV + DataFrame** | 4532767 |  
**Parquet + DataFrame** | 4636471 |

**Combien de produits vendus en France ?**  
| | Méthode | Nombre de produits |  
|-----|---------|--------------------|
**CSV + DataFrame** | df["countries"].str.contains("fr") | 590241 |  
**Parquet + DataFrame** | df["lang"].eq("fr") | 1336912 |

**Quelle part a un Nutri-Score renseigné ?**  
| | colonne | méthode | non renseignés | % renseignés |  
|-|---------|---------|----------------|--------------|
**CSV + DataFrame** | nutriscore_score | .isna().sum() | 3157914 | 30.33% |  
**Parquet + DataFrame** | nutriscore_score | .isna().sum() | 1336912 | 29.79% |  
**Parquet + DataFrame** | nutriscore_grade | .isna().sum() | 43447 | 99.06% |

**Les dix marques les plus présentes ?**  
**CSV + DataFrame:**
|Marque | Nbre  |
|-------|-------|
| Carrefour | 25641 |
| Auchan | 18107 |
| Coop | 14067 |
| Lidl | 13804 |
| U | 12286 |
| BonÀrea | 12193 |
| Aldi | 11683 |
| Hacendado | 10490 |
| Tesco | 10282 |
| Delhaize | 9741 |  

**Parquet + DataFrame:**
|Marque | Nbre  |
|-------|-------|
| Carrefour | 20732 |
| Coop | 14545 |
| Lidl | 14243 |
| U | 12384 |
| Aldi | 12353 |
| BonÀrea | 12155 |
| Hacendado | 10658 |
| Auchan | 10590 |
| Tesco | 10503 |

**Le taux de manquants sur les nutriments clés (energy_100g, sugars_100g, salt_100g ) ?**  
**CSV + DataFrame:**
| colonne | non renseignés | % renseignés | 
|---------|----------------|--------------|
| energy_100g | 2296811 | 49.33 |
| sugars_100g | 2388528 | 47.31 |
| salt_100g | 2580977 | 43.06 |

**Parquet + DataFrame:**  
Les données sont dans un champs de type objet

**Qu'est-ce qui vous semble le plus « sale » dans ces données ?**  