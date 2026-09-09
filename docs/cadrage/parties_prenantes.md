# NutriScope — Alignement Stratégique & Gestion du Produit

Ce document rassemble la cartographie des acteurs clés du projet NutriScope ainsi que la définition des personas cibles pour orienter les développements techniques et l'expérience utilisateur (UX).

---

## 1. Cartographie des Parties Prenantes (Matrice Pouvoir / Intérêt)

Pour réussir le lancement de **NutriScope**, nous devons piloter nos relations selon le niveau d'influence (**Pouvoir**) et l'engagement (**Intérêt**) de chaque acteur.

### Matrice Visuelle

```text
       ÉLEVÉ |  [A satisfaire en permanence]    [A gérer étroitement]
             |  • L'équipe d'infrastructure     • Direction (Sponsor)
             |    de données et de gouvernance  • Équipe Data/IA (Nous)
P            |    de données (RGPD)                     
O            |---------------------------------------------------------
U            |  [A surveiller]                  [A tenir informées]
V            |  • Open Food Facts               • Équipe Marketing
O            |    (Data / licence)              • Utilisateurs finaux
I            |  • Concurrents indirects           (parents, diabétiques, etc)
R     FAIBLE |_________________________________________________________
             | FAIBLE                                            ÉLEVÉ
                                  INTÉRÊT
```
### Plan d'Engagement Détaillé

| Partie Prenante | Pouvoir | Intérêt | Stratégie d'engagement |
| :--- | :--- | :--- | :--- |
| **Direction (NutriScope)** | Élevé | Élevé | **Acteur clé** : Elle valide les budgets, la feuille de route et l'atteinte des KPI business (ROI, acquisition). |
| **Équipe Data/IA** | Élevé | Élevé | **Acteur clé** : Nous concevons l'architecture technique, de la base Parquet aux modèles d'IA, et garantissons la fiabilité. |
| **Délégué à la Protection des Données (DPO)** | Élevé | Faible/Modéré | **Gérer de près** : Pouvoir de veto légal. Il s'assure de la conformité RGPD/AI Act dès le premier jour. |
| **Équipe Marketing** | Faible/Modéré | Élevé | **Maintenir informés** : Elle a besoin des tableaux de bord et des segments produits pour concevoir les campagnes et l'image de marque. |
| **Utilisateurs finaux** | Faible | Élevé | **Maintenir informés & Co-construire** : Leur adoption fera le succès du service. Leurs retours guident l'UX et la pertinence du chatbot. |
| **Open Food Facts** | Faible | Faible | **Surveiller** : Fournisseur de la donnée brute sous licence ouverte. Risque technique faible mais dépendance forte sur la structure de leur API. |
---

## 2. Personas Utilisateurs

Pour concevoir une application et un assistant conversationnel (RAG) pertinents, nous ciblons trois profils d'utilisateurs aux exigences bien distinctes.

### A. Thomas, 38 ans – Le parent pressé
> **Axe principal :** Recherche de simplicité et rapidité d'exécution.

* **Situation d’usage :** Fait les grosses courses de la semaine le samedi après-midi dans un hypermarché bondé à Lille, avec ses deux enfants.
* **Objectifs :** Trouver rapidement des alternatives plus saines (moins de sucre/additifs) pour les goûters des enfants, sans y passer des heures.
* **Freins & Points de douleur :** Manque de temps flagrant. Si l'application demande plus de trois essais pour scanner un produit avant de répondre, il abandonne.
* **Besoin IA / Produit :** Une lecture d'image instantanée (OCR/classification rapide des paquets) et un moteur de substitution immédiat (*"Prenez plutôt ce produit 2 rayons plus loin"*).

### B. Inès, 62 ans – La senior active diabétique
> **Axe principal :** Exigence de santé, fiabilité et accessibilité.

* **Situation d’usage :** Fait ses courses de proximité en centre-ville, lit attentivement les étiquettes à l'aide de ses lunettes de lecture.
* **Objectifs :** Contrôler strictement son index glycémique et traquer les sucres cachés.
* **Freins & Points de douleur :** Complexité des tableaux nutritionnels et jargon technique des additifs. Peur de l'erreur médicale. Interface mobile parfois trop petite ou illisible (Enjeu majeur d'accessibilité **RGAA**).
* **Besoin IA / Produit :** Un assistant conversationnel (**Chatbot RAG**) rassurant capable de répondre à : *"Ce produit est-il compatible avec un diabète de type 2 ?"* en se basant sur des sources médicales certifiées.

### C. Lucas, 21 ans – L’étudiant au budget serré
> **Axe principal :** Arbitrage permanent entre prix et santé.

* **Situation d’usage :** Fait ses courses chez un discounter (Lidl/Aldi) avec un budget alimentaire de **40€ par semaine**.
* **Objectifs :** Manger le plus équilibré possible (atteindre ses objectifs en protéines pour le sport) sans faire exploser son budget.
* **Freins & Points de douleur :** Les produits "healthy" ou Bio sont souvent trop chers. Les alternatives proposées par l'application doivent impérativement respecter sa contrainte financière.
* **Besoin IA / Produit :** Un moteur de substitution multicritère (**Score nutritionnel ET prix équivalent ou inférieur**) associé à une segmentation claire du catalogue premier prix.

# Entretien direction – NutriScope
 
## 1. Objectif de l’application
 
**Question :**  
Qu’est-ce qui est le plus important pour vous : avoir une application rapide, intelligente ou simple à utiliser ?
 
**Réponse :**  
L’application doit être **rapide, intelligente et réellement utile** pour l’utilisateur.
 
---
 
## 2. Délais du projet
 
**Question :**  
Quelles sont les fonctionnalités indispensables pour avoir une première version utilisable dans les délais ?
 
**Réponse :**  
L’application doit être utilisable par le **public dans 4 mois**, avec une version pour la direction dans **10 semaines**.
 
---
 
## 3. Priorités
 
**Question :**  
Quelles sont les deux fonctionnalités les plus importantes pour les familles ?
 
**Réponse :**  
Les deux priorités sont la **recherche de produits** et le **scan d’un produit**.
 
---
 
## 4. Fiche produit
 
**Question :**  
Quelles informations voulez-vous que l’utilisateur comprenne facilement lorsqu’il consulte un produit ?
 
**Réponse :**  
La fiche produit doit être **simple et compréhensible**.
 
---
 
## 5. Public cible
 
**Question :**  
Est-ce que l’application doit rester destinée au grand public ou proposer des fonctionnalités spécifiques pour certaines personnes ?
 
**Réponse :**  
L’application doit rester **grand public**, sans fonction médicale ni recommandations spécialisées pour certaines personnes.
 
---
 
## 6. Sources de données
 
**Question :**  
Comment souhaitez-vous faire évoluer les données pour ne pas dépendre uniquement d’Open Food Facts ?
 
**Réponse :**  
Il faut **limiter la dépendance à Open Food Facts**.
 
---
 
## 7. Personnalisation
 
**Question :**  
Est-ce que les informations et recommandations doivent pouvoir être personnalisées en fonction de chaque produit ?
 
**Réponse :**  
Oui, l’application doit pouvoir être **personnalisable pour chaque produit**.
 
---
 
## 8. Interface
 
**Question :**  
Qu’est-ce qui serait le plus utile pour faciliter la recherche de produits pour les familles ?
 
**Réponse :**  
L’interface doit être **simple et fluide**, avec des **filtres pour les produits**.
 
---
 
## 9. Retours utilisateurs
 
**Question :**  
Comment souhaitez-vous avoir rapidement des retours sur l’application ?
 
**Réponse :**  
L’objectif est d’avoir **rapidement des utilisateurs et leurs retours** afin d’améliorer l’application.
 
---
 
## 10. Réussite du lancement
 
**Question :**  
Qu’est-ce qui vous ferait dire, dans 4 mois, que le lancement est réussi ?
 
**Réponse :**  
Avoir une première version rapidement, avec **de vrais utilisateurs et des retours permettant d’améliorer l’application**.