# Lycées et géographie des cadres dans trois aires urbaines de province

> **Projet** : Python pour la data science (ENSAE), groupe de 3 personnes **Rendu** : mardi 24 novembre 2026 · **Soutenance** : janvier 2027 **Grille d'évaluation** : https://pythonds.linogaliana.fr/content/annexes/evaluation.html **Statut du document** : plan de référence du projet. Toute décision qui s'en écarte est notée dans le journal des décisions (section 13).

------------------------------------------------------------------------

## Sommaire

0.  Résumé du projet
1.  Problématique, contexte et hypothèses
2.  Périmètre et choix structurants (fixés avant de voir les résultats)
3.  Sources de données
4.  Construction de la base communale (pipeline)
5.  Méthodologie d'analyse
6.  Plan du rapport final
7.  Organisation du dépôt
8.  Conventions de travail
9.  Calendrier, rôles et jalons
10. Risques et ordre de sacrifice
11. Checklist de rendu
12. Instructions pour Claude Code : par où commencer
13. Journal des décisions

------------------------------------------------------------------------

## 0. Résumé du projet

**Question.** Dans des aires urbaines de province aux traditions scolaires contrastées, les communes offrant un meilleur accès à des lycées privés ou à forte valeur ajoutée concentrent-elles davantage de cadres que leurs voisines, et ce lien résiste-t-il face aux autres infrastructures ?

**Approche.**

- On construit une base à une ligne par commune pour trois aires d'attraction des villes (hors Paris), en croisant le recensement, les données de l'Éducation nationale et des données d'infrastructures.
- On mesure l'accès de chaque commune aux lycées, et non leur simple présence dans la commune.
- On compare les communes à position égale dans l'aire : par anneaux de distance au centre, puis par paires de communes contiguës.

**Statut des résultats.** Le projet décrit des associations, pas des effets causaux. Un résultat nul bien établi est un résultat valable et sera présenté comme tel.

------------------------------------------------------------------------

## 1. Problématique, contexte et hypothèses

### 1.1 Contexte et littérature

- **Fack G. et Grenet J. (2010)**, « When do better schools raise housing prices? Evidence from Paris public and private schools », *Journal of Public Economics*, 94(1-2), p. 59-77. À Paris, une hausse d'un écart-type de la performance des collèges publics augmente les prix immobiliers de 1,4 à 2,4 %. Cet effet diminue quand l'offre privée à proximité augmente. C'est notre mécanisme de départ : l'offre scolaire entre dans les choix résidentiels, et le privé joue le rôle d'option de repli.
- **Black S. (1999)**, « Do Better Schools Matter? Parental Valuation of Elementary Education », *Quarterly Journal of Economics*. C'est la référence méthodologique sur la comparaison de logements situés de part et d'autre des limites de secteurs scolaires. Notre comparaison entre communes contiguës en est une version simplifiée.
- **Le contraste régional (DEPP, Repères et références statistiques).** En métropole, environ 78 % des élèves du second degré sont scolarisés dans le public, contre seulement six sur dix environ dans les académies de Rennes et de Nantes. Dans l'Ouest, le privé est un choix courant. On s'attend donc à ce qu'il y soit moins socialement sélectif.

### 1.2 Hypothèses

Elles sont fixées avant toute analyse. L'indicateur principal est défini en section 2.4.

| ID | Énoncé | Mesure | Test principal | Figure |
|-------------|-------------|-------------|---------------------|-------------|
| H1 | À distance égale du centre de l'aire, la part de cadres est plus élevée dans les communes ayant un meilleur accès aux lycées privés sous contrat. | `dist_lyc_prive_min` (principale) et `n_lyc_prive_5km` (secondaire) contre `part_cadres_2022` | Différences entre communes contiguës (5.3), complétées par les anneaux de distance (5.2) | Fig. 5, 4 |
| H2 | Ce lien est plus faible dans l'aire de l'Ouest, où le privé est plus répandu. | H1 estimée aire par aire | Comparaison des écarts entre aires (5.4) | Fig. 4 (une facette par aire) |
| H3 | C'est la qualité des lycées accessibles (valeur ajoutée IVAL), plus que leur nombre, qui accompagne la hausse de la part de cadres entre 2011 et 2022. | `ival_moy_5km` contre `evol_cadres_pts`, à nombre de lycées égal | Section 5.5 | Fig. 6 |
| H4 | L'association avec les lycées est plus forte que celle avec les autres infrastructures (gares, médecins, équipements). | Même fonction d'accessibilité appliquée à chaque infrastructure | Section 5.7 | Fig. 7 |

### 1.3 Ce que le projet ne peut pas montrer

- **Causalité inverse.** Les lycées privés peuvent s'implanter ou se maintenir là où vivent déjà les familles aisées.
- **Sélection résidentielle non observée.** Les préférences des ménages ne sont pas mesurées.
- **Mesure d'accès imparfaite.** Les distances sont calculées à vol d'oiseau depuis un point de référence unique par commune.

Ces limites sont annoncées dès l'introduction du rapport et reprises dans la conclusion.

------------------------------------------------------------------------

## 2. Périmètre et choix structurants (fixés avant de voir les résultats)

Fixer ces choix à l'avance évite de chercher la spécification qui « marche ». Toute modification est justifiée dans le journal des décisions (section 13).

### 2.1 Unité et géographie

- **Unité d'observation** : la commune. Pour Lyon, Marseille et Paris, ce sont les arrondissements municipaux.
- **Géographie de référence** : le Code officiel géographique (COG) au 1er janvier 2025, celui du recensement 2022. Toutes les sources sont ramenées à cette géographie grâce à la table de passage de l'Insee.
- **Projection** : Lambert 93 (EPSG:2154) pour tous les calculs de distance, en mètres. WGS84 (EPSG:4326) uniquement pour les cartes interactives.

### 2.2 Périmètre géographique

- **Trois aires d'attraction des villes** (zonage Insee 2020), pôle et couronne compris. Paris est exclu, à cause du poids des transports en commun.
- **Choix des aires (semaine 1, à partir des données).**
  - Candidates : Rennes, Nantes, Toulouse, Bordeaux, Lyon, Grenoble, Lille, Strasbourg.
  - Critères :
    - (a) au moins une aire de l'Ouest (Rennes ou Nantes) ;
    - (b) un contraste dans le poids du privé, mesuré par la part de lycées privés sous contrat et l'écart d'IPS moyen entre public et privé ;
    - (c) des tailles d'aire comparables (population de l'aire : somme de `P22_POP` du recensement 2022) ;
    - (d) au moins une dizaine de lycées privés par aire (seuil indicatif) ;
    - (e) un support suffisant de l'exposition : le nombre de cellules estimables à 10 km (règle du §5.2, après fusion des anneaux et contrôle de l'équilibre de distance) et le nombre de paires de communes contiguës dont le statut exposé/non exposé diffère (au moins un lycée privé sous contrat à 10 km). Les valeurs à 5 km sont journalisées à côté. L'aire de l'Ouest retenue est celle qui maximise le nombre de cellules estimables ; à égalité, celle qui compte le plus de paires de statut différent ;
    - (f) la faisabilité : le coût réel de Lyon est mesuré avant toute décision ; mesuré le 20/10, il est nul pour la variable à expliquer, la source du §2.3 donnant les arrondissements avec la même définition (A11). Une exclusion de Lyon est justifiée par écrit, en rappelant que d'après les premiers comptes d'exposition Lyon est l'aire la mieux dotée en support.
  - Les valeurs de tous les critères (a) à (f) pour les 8 candidates sont journalisées au moment du choix (§13), dans le tableau de support décrit au §5.2.
  - Le choix et ses justifications forment la section 3.1 du rapport.

### 2.3 Variable à expliquer

- **Principale** : la part des cadres et professions intellectuelles supérieures (groupe socioprofessionnel 3) parmi les actifs de 25 à 54 ans, en 2011 et en 2022.
  - **Source** : recensement 2022, « Évolution et structure de la population » (source 2), qui donne 2011 et 2022 en COG 2025, avec les arrondissements de Lyon. Numérateur `C22_POP2554_STAT_GSEC13_23` (2022) et `C11_POP2554_CS3` (2011) ; dénominateur, la somme des 6 groupes socioprofessionnels des 25-54 ans, c'est-à-dire les actifs occupés et les chômeurs ayant déjà travaillé. C'est la définition des séries historiques de l'Insee, la même pour les deux années, et leurs valeurs sont identiques (A11).
  - **Pourquoi 25-54 ans** : c'est l'âge des parents de lycéens, et cela neutralise les écarts de structure par âge (les retraités en particulier).
- **Dérivée** : `evol_cadres_pts` = part en 2022 moins part en 2011, en points de pourcentage.
- **Robustesse** : la part de cadres dans la population de 15 ans ou plus (recensement 2022, base « Évolution et structure de la population »).
- Le passage à la nomenclature PCS 2020 dans le recensement 2022 ne change pas les deux premiers niveaux. Le groupe des cadres reste donc comparable dans le temps.

### 2.4 Indicateur principal d'accès aux lycées (fixé maintenant)

- **Lycées retenus** : lycées d'enseignement général et technologique, et lycées polyvalents, publics et privés sous contrat. Les lycées professionnels seuls, les lycées agricoles et le privé hors contrat sont exclus de l'indicateur principal et réintégrés en robustesse.
- **Point de référence de la commune** : son centroïde géométrique. Le chef-lieu (point mairie de la couche ADMIN EXPRESS de l'IGN) est une alternative testée en robustesse.
- **Rayon principal : 5 km.** Les rayons de 3 et 10 km servent en robustesse.
- **Indicateurs calculés pour chaque commune** :
  - `n_lyc_prive_5km`, `n_lyc_public_5km` : nombre de lycées dans le rayon ;
  - `dist_lyc_prive_min`, `dist_lyc_public_min` : distance au plus proche, en km ;
  - `ival_moy_5km` : pour chaque lycée, moyenne simple des `va_acces_2nde` des sessions 2012 à 2022, à condition d'avoir au moins 5 sessions valides (`va_acces_2nde` renseignée) ; puis moyenne des lycées du rayon, pondérée par la moyenne de `presents_total` sur ces sessions. Les lycées de moins de 5 sessions valides restent comptés dans les `n_lyc_*` mais sortent de l'IVAL. Le stock de lycées est l'instantané de l'annuaire du 13/10/2026 (les lycées fermés en sont absents).
- **Effet de bord** : les indicateurs sont calculés sur tous les lycées retenus de France métropolitaine (2 413 UAI dans l'annuaire du 13/10/2026), y compris hors des aires. Une marge de 10 km au-delà de l'aire suffit pour les comptes, mais pas pour la distance au plus proche lycée. Les lycées étrangers sont absents de l'annuaire.

### 2.5 Variables de contrôle et « mauvais contrôles »

- **Contrôles** :
  - `dist_centre_km` : distance au centroïde de la commune-centre de l'aire (`CATEAAV2020` = 11 dans le zonage de l'Insee ; Lyon entière, réunion de ses arrondissements) ;
  - `densite` : habitants par km² (`P22_POP` / `SUPERF`, série historique du recensement 2022), en logarithme népérien partout où elle sert de contrôle (`log_densite` dans les cellules du §5.2, `d_log_densite` dans les paires du §5.3) ;
  - `aire` : effet fixe, c'est-à-dire qu'on compare toujours à l'intérieur d'une même aire.
- **Mauvais contrôles**, jamais utilisés comme contrôles dans la spécification principale :
  - le niveau de vie médian (Filosofi), qui est en grande partie une conséquence de la part de cadres ;
  - l'IPS des lycées, construit à partir de la profession des parents et donc quasi mécaniquement lié à la part de cadres.
  - Ces deux variables restent purement descriptives.
- **Prix immobiliers (DVF)** : ils sont à la fois cause et conséquence. On les présente avec et sans ce contrôle, et on discute l'écart.

------------------------------------------------------------------------

## 3. Sources de données

Priorité : **P1** = indispensable aux hypothèses H1 à H3, **P2** = partie 5 et contrôles, **P3** = bonus si le temps le permet. Les URL marquées « à confirmer » doivent être vérifiées en semaine 1, et le lien direct de téléchargement copié dans `config.py`.

### 3.1 Tableau des sources

| # | Source | Producteur | Maille | Accès | Rôle | Priorité |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| 1 | Séries historiques : population active de 25-54 ans par CSP (1968-2022) — https://www.insee.fr/fr/statistiques/1893185 | Insee | Commune | Fichier | Contrôle de cohérence de la source 2 (même définition, mêmes valeurs), non utilisée par le pipeline | Hors pipeline |
| 2 | Recensement 2022, « Évolution et structure de la population » — https://www.insee.fr/fr/statistiques/8581696 | Insee | Commune et arrondissement | Fichier | Variable à expliquer (2011, 2022) ; robustesse (cadres 15 ans ou plus) | P1 |
| 2 bis | Recensement 2022, séries historiques — https://www.insee.fr/fr/statistiques/8582555 | Insee | Commune | Fichier | Population (`P22_POP`), superficie (`SUPERF`), densité ; population de l'aire (critère c) | P1 |
| 3 | Annuaire de l'éducation — https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/api/ | Ministère de l'Éducation nationale | Établissement (point) | **API** Opendatasoft | Liste des lycées, statut public/privé, coordonnées | P1 |
| 4 | Adresse et géolocalisation des établissements — https://www.data.gouv.fr/datasets/adresse-et-geolocalisation-des-etablissements-denseignement-des-premier-et-second-degres | Ministère de l'Éducation nationale | Point | Fichier ou API | Coordonnées de secours si l'annuaire en manque | P1 |
| 5 | IPS des lycées (à partir de 2023) — https://www.data.gouv.fr/datasets/ips-lycees-a-partir-de-2023 | DEPP | Établissement | Fichier ou API | Descriptif : écart public/privé par aire (choix des aires, H2) | P1 |
| 6 | IVAL, lycées d'enseignement général et technologique — https://www.data.gouv.fr/datasets/6707515c84dfa4012c3ecd45 | DEPP | Établissement | Fichier ou API | Qualité des lycées (H3) | P1 |
| 7 | Contours communaux (IGN ADMIN EXPRESS via `cartiflette`) — https://github.com/inseefrlab/cartiflette | IGN / InseeFrLab | Commune (polygone) | Package Python | Géométries, centroïdes, contiguïté | P1 |
| 8 | Zonage en aires d'attraction des villes 2020 (table d'appartenance des communes) — insee.fr, *à confirmer* | Insee | Commune | Fichier | Périmètre, pôle et couronne, commune-centre | P1 |
| 9 | Table de passage annuelle des codes communes (COG) — insee.fr, *à confirmer* | Insee | Commune | Fichier | Harmonisation des géographies | P1 |
| 10 | DVF géolocalisées — https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees | DGFiP / Etalab | Transaction (point) | Fichier par département | Prix médian au m² (contrôle discuté) | P2 |
| 11 | Filosofi 2021, communes — https://www.insee.fr/fr/statistiques/7756855?sommaire=7756859 | Insee | Commune | Fichier | Descriptif uniquement | P2 |
| 12 | Gares de voyageurs — https://data.gouv.fr/fr/datasets/gares-de-voyageurs-1 | SNCF Gares & Connexions | Point | Fichier ou API | H4 : accès au train | P2 |
| 13 | APL aux médecins généralistes — https://www.observatoire-des-territoires.gouv.fr/accessibilite-potentielle-localisee-apl-aux-medecins-generalistes | DREES | Commune | Fichier | H4 : santé (indicateur déjà calculé en accessibilité) | P2 |
| 14 | Base permanente des équipements, équipements géolocalisés — https://www.data.gouv.fr/datasets/base-permanente-des-equipements-2 | Insee | Point | Fichier | H4 : équipements culturels et services | P2 |
| 15 | Data ES, équipements sportifs — https://www.data.gouv.fr/datasets/recensement-des-equipements-sportifs-espaces-et-sites-de-pratiques-2 | Ministère des Sports | Point | Fichier ou API | H4 : sport | P2 |
| 16 | Migrations résidentielles, fichier détail MIGCOM 2022 — https://www.insee.fr/fr/statistiques/8589767 | Insee | Individu (Parquet, environ 17 millions de lignes) | Fichier | Bonus : soldes migratoires de cadres | P3 |
| 17 | Fiscalité locale des particuliers — https://data.economie.gouv.fr/explore/dataset/fiscalite-locale-des-particuliers-geo | DGFiP | Commune | API | Bonus : taux de taxe foncière | P3 |
| 18 | Aménagements cyclables — https://www.data.gouv.fr/datasets/60a37b7f303fdf4f2654b73d | Geovelo / OpenStreetMap | Ligne | Parquet | Bonus : cadre de vie | P3 |

### 3.2 Points d'attention à documenter dans le rapport (encadré « choix et biais »)

- **IPS** : les données du privé ne sont pas comparables avant 2023, car la remontée des professions des parents s'y est fortement améliorée. On n'utilise que la série à partir de 2023. L'IPS reste descriptif (voir 2.5).
- **IVAL** : c'est une mesure relative, qui ne couvre que le public et le privé sous contrat, et qui comprend plusieurs indicateurs (taux de réussite, taux d'accès de la seconde au bac, taux de mentions). Indicateur principal : **valeur ajoutée du taux d'accès de la seconde au bac**, car il reflète le parcours complet de l'élève. Le taux de réussite sert en robustesse. Décalage temporel : les IVAL sont récents, alors que l'évolution des cadres porte sur 2011-2022. Vérification faite le 13/10/2026 : l'ancienne version de data.gouv est identique à la v2 (pas de millésime indépendant), et la valeur ajoutée d'un lycée est peu stable d'une session à l'autre (corrélation de 0,56 à un an, 0,32 à cinq ans, 0,12 entre 2012 et 2025). On retient donc la moyenne des sessions 2012 à 2022 (§2.4), qui couvre la période entre les deux recensements ; c'est un choix de conception, pas un constat de stabilité. Contrôle sans cadres : pas de rupture de la corrélation de `va_acces_2nde` autour de 2016-2017 (0,60 entre 2016 et 2017), un creux vers 2017-2020 de cause non vérifiée, guides méthodologiques 2016 et 2020 non lus. **Fiabilité**, calculée et journalisée après le choix des aires et avant le premier commit de T5 : pour les lycées de la règle du §2.4 qui ont au moins 3 sessions valides dans chaque moitié, on calcule deux `ival_moy_5km` par commune, l'un sur 2012-2017, l'autre sur 2018-2022, avec les poids de l'indicateur principal ; on prend la corrélation de Pearson entre les deux sur les communes de la population de H3 (§5.5) des 3 aires retenues, après centrage par aire, corrigée par Spearman-Brown (2r / (1 + r)). Seule cette valeur, toutes aires ensemble, tranche H3 ; les valeurs par aire sont descriptives. Le nombre de lycées distincts est donné à côté de chaque valeur : des communes voisines partagent les mêmes lycées (leurs disques de 5 km se recouvrent), ce qui réduit l'effectif réel et peut gonfler la corrélation. En dessous de 0,5, H3 est « non testable avec cette mesure » (ni confirmée ni infirmée). Robustesse : moyenne sur 2012-2025.
- **Filosofi** : le millésime 2021 est le dernier de l'ancien dispositif. Le millésime 2023 (Filosofi 2) n'est pas comparable et ne fournit que deux indicateurs à la commune.
- **Secret statistique et petites communes** : on signale les communes de moins de 200 actifs de 25-54 ans (seuil indicatif). Les moyennes sont pondérées par le nombre d'actifs. On teste aussi l'exclusion de ces communes.
- **DVF** : fenêtre de cinq ans glissants. On utilise les ventes d'appartements et de maisons sur 2020-2024, puis la médiane du prix au m² par commune, à condition d'avoir au moins 10 ventes (sinon valeur manquante, signalée).

------------------------------------------------------------------------

## 4. Construction de la base communale (pipeline)

``` mermaid
flowchart LR
    A[Référentiel communes<br/>AAV + COG + contours] --> D[Accessibilité<br/>fonction générique]
    B[Recensement<br/>cadres 2011 et 2022] --> G[Base communale<br/>final/base_communale.parquet]
    C[Lycées<br/>API annuaire + IPS + IVAL] --> D
    E[Autres points<br/>gares, BPE, Data ES] --> D
    D --> G
    F[Contrôles<br/>distance centre, densité, DVF] --> G
    A --> P[Paires contiguës<br/>final/paires.parquet]
    G --> P
```

Chaque étape correspond à une fonction de `src/cadres_lycees/`. Elle lit les données brutes depuis S3 (et les télécharge si elles n'y sont pas encore), puis écrit son résultat sur S3. Chaque étape se termine par des **vérifications** (`assert`) qui font échouer le code bruyamment si une jointure perd des lignes. Tous les téléchargements passent par une seule fonction, `stockage.copie_controlee(url, chemin, sha256)`, qui échoue si le `sha256` diffère. Les sources mutables sont collectées une fois par leur API (export Opendatasoft de l'annuaire, cartiflette pour les contours) en une copie gelée datée ; le rapport lit ces copies, dont la date, l'URL d'origine et le `sha256` sont donnés dans le README et dans la section 2.1 du rapport.

| Étape | Fonction(s) | Sortie | Vérifications |
|----------------|-------------------|----------------|----------------------|
| A. Référentiel | `geo.referentiel_communes(aires)` | GeoDataFrame des communes des 3 aires : `code_commune`, `aire`, `pole_couronne`, `geometry`, `centroide`, `dist_centre_km` | Nombre de communes égal à celui de la table AAV ; codes uniques ; aucune géométrie vide |
| B. Cadres | `collecte.evol_struct_rp2022()`, `nettoyage.part_cadres()` | `part_cadres_2011`, `part_cadres_2022`, `evol_cadres_pts`, `actifs_2022` | Parts comprises entre 0 et 1 ; aucune commune manquante (fichier en COG 2025) |
| C. Lycées | `collecte.annuaire_education()` (France métropolitaine, copie gelée du 13/10/2026), `collecte.ips_lycees()`, `collecte.ival_lycees()`, `nettoyage.lycees_geo()` découpée en quatre fonctions (lycées retenus, aire, IPS, IVAL) | GeoDataFrame des lycées : `uai`, `secteur`, `aire`, `ips`, `ival`, `poids_ival`, `geometry` | Identifiants UAI uniques ; part des lycées géolocalisés > 98 % ; part des lycées avec IVAL indiquée dans le rapport ; un lycée sans statut public/privé fait échouer la collecte, sauf `0271911F`, écarté nommément ; listes d'UAI nommées propres aux 3 aires retenues |
| D. Accessibilité | `accessibilite.indicateurs(communes, points, prefixe, rayons, attribut, poids)`, filtre public/privé fait avant l'appel | Colonnes `n_<x>_<r>km`, `dist_<x>_min`, `<attr>_moy_<r>km` | Tests unitaires sur données jouets (`tests/test_accessibilite.py`) ; `assert` dans le pipeline : les comptes du tableau de support (§2.2, §5.2) sont reproduits pour les aires retenues |
| E. Contrôles | `collecte.dvf(departements)`, `nettoyage.prix_m2()`, `collecte.serie_historique_rp2022()`, `nettoyage.population()` | `prix_m2_med`, `densite`, `niveau_vie_med` (descriptif) | Nombre de ventes par commune ; règle du seuil de 10 ventes appliquée |
| F. Paires | `geo.paires_contigues(communes, variables)` | Une ligne par paire (i < j, ordre des codes) de communes contiguës au sens Queen (bord ou point commun) dans une même aire, avec les écarts `d_part_cadres`, `d_n_lyc_prive_5km`, etc. | Pas de doublon (i,j)/(j,i) ; les deux communes appartiennent à la même aire ; une commune sans voisine fait échouer |
| G. Table finale | `pipeline.construire_base(aires)`, appelée par `rapport.ipynb` : le rapport reconstruit la base depuis les copies gelées, `final/` n'est qu'une sortie | `final/base_communale.parquet`, `final/paires.parquet`, `docs/dictionnaire_variables.md` | Une ligne par commune ; dictionnaire à jour ; moins de 30 minutes depuis le brut gelé, bootstrap compris, mesuré dès le test complet de S4 |

------------------------------------------------------------------------

## 5. Méthodologie d'analyse

Rappel : l'ENSAE n'attend plus de partie modélisation. L'analyse repose sur des comparaisons transparentes. Une régression linéaire peut apparaître, uniquement comme outil descriptif (« à distance au centre égale, l'écart vaut… »), jamais comme exercice de prédiction.

### 5.1 Descriptif (sections 3.1 à 3.3 du rapport)

- **Fig. 1** : pour les 8 candidates, les 3 aires retenues mises en avant : part du privé sous contrat en nombre de lycées et pondérée par les candidats au bac (moyenne de `presents_total` de l'IVAL, couverture indiquée), et IPS de chaque lycée par secteur (un point par lycée, moyenne et écart privé moins public). Justifie le choix des aires ; pour H2, elle montre les deux dimensions du critère (b), la prévalence du privé et sa sélectivité sociale (§1.1).
- **Fig. 2** : part de cadres selon la distance au centre, avec une courbe lissée par aire. Montre pourquoi il faut comparer à distance égale.
- **Fig. 3** : carte folium par aire retenue, en 3 onglets Quarto avec un seul commentaire (à vérifier au premier `quarto render`, une carte placée dans un onglet caché pouvant s'afficher à taille nulle ; repli : les trois cartes à la suite) : distance au lycée privé sous contrat le plus proche par commune, lycées en points selon le secteur ; en dernier et si le temps le permet, une couche des limites entre communes contiguës de statut différent.

### 5.2 H1 : comparaison par anneaux de distance (complément des paires)

Les anneaux complètent l'estimation par paires (5.3) là où les cellules sont estimables.

- **Anneaux** : 0-5, 5-10, 10-20, 20-30 et plus de 30 km du centre.
- **Cellule estimable.** Une cellule (aire × anneau) n'est estimée que si les deux conditions suivantes sont remplies, au rayon considéré :
  - chacun des deux groupes, communes **avec** au moins un lycée privé dans le rayon et communes **sans**, compte au moins 15 communes. Sinon, on fusionne, aire par aire et séparément à chaque rayon : tant qu'une cellule ne remplit pas la condition, la plus proche du centre de ces cellules est fusionnée avec sa voisine (anneau immédiatement intérieur ou extérieur, déjà fusionné ou non) qui compte le moins de communes, la plus proche du centre à égalité. Si la dernière cellule restante ne remplit pas la condition, l'aire est « non estimable » par anneaux. Le seuil de 15 communes est celui du plan d'origine ;
  - l'écart entre les distances moyennes au centre des deux groupes, vérifié après fusion, ne dépasse pas 2 km (moyennes simples ; borne proposée le 13/10 et validée le 20/10 ; elle correspond à 20 % de la largeur d'un anneau de 10 km), et la comparaison est contrôlée par `dist_centre_km` et la densité (§2.5) dans la cellule. Une cellule qui dépasse la borne est non estimable, sans nouvelle fusion.
- Dans chaque cellule estimable, l'estimation est l'écart avec/sans dans une régression de `part_cadres_2022` sur l'exposition et les contrôles de la cellule, pondérée par les actifs ; l'écart brut des parts moyennes pondérées est donné à côté.
- Intervalles de confiance par **bootstrap** sur les communes (1 000 tirages avec remise dans chaque groupe de la cellule, percentiles 2,5 et 97,5).
- **Rayons.** Le rayon de 5 km reste principal. Le rayon de 10 km, qui reste une spécification de robustesse (§2.4), est calculé pour les mêmes aires et rapporté à côté du 5 km sans le remplacer ; sa concordance avec le 5 km entre dans le verdict de H1 (§5.3). Comme les fusions diffèrent selon le rayon, la concordance se lit par anneau d'origine : on compare les estimations des deux cellules estimables qui le contiennent, une à chaque rayon.
- **Tableau de support**, livrable commité dans `docs/` avant que le choix des aires soit journalisé, et publié avant tout résultat sur les cadres. Pour chacune des 8 candidates, à 5 et à 10 km : population de l'aire, nombre et part de communes exposées, effectifs avec/sans par cellule après fusion, distance moyenne au centre de chaque groupe, nombre de cellules estimables, nombre de paires de statut différent (l'indicateur 0/1 « au moins un lycée privé sous contrat dans le rayon » diffère entre les deux communes), corrélation non centrée (indépendante du sens i − j) entre `d_dist_lyc_prive_min` et `d_dist_centre_km` dans les paires, et, pour Lille et Strasbourg (seules candidates proches d'une frontière terrestre), nombre de communes à moins de 10 km du contour national (critère f). Il est calculé une seule fois, avec les règles ci-dessus.
- **Fig. 4** : estimations de H1 par aire, en points avec intervalles à 95 %, trois panneaux à axes propres : pente principale des paires, pente secondaire, écarts des cellules estimables à 5 et à 10 km. Les aires sont sur la même ligne d'un panneau à l'autre, ce qui sert aussi H2 (§5.4) ; les cellules non estimables sont nommées en note.

### 5.3 H1 : différences entre communes contiguës (résultat principal)

- Pour chaque paire de communes qui se touchent : `d_part_cadres` comparé à `d_dist_lyc_prive_min`, l'écart de distance au plus proche lycée privé sous contrat. C'est l'estimation principale de H1 et elle porte le verdict. Les écarts de distance au centre (`d_dist_centre_km`) et de densité (`d_log_densite`) sont en contrôle (§2.5), car la distance au plus proche lycée varie avec la distance à la ville et avec la densité.
- `d_n_lyc_prive_5km` est l'estimation secondaire.
- **Logique** : tout ce que deux voisines partagent (marché de l'emploi, climat, prix régionaux) s'annule dans la différence.
- **Fig. 5** : nuage de points regroupé par classes (binned scatter) sur les paires symétrisées (chaque paire dans les deux sens), avec la pente d'une régression des écarts de part de cadres sur les écarts d'accès et les écarts des contrôles. Le sens i − j suit l'ordre des codes : toutes les pentes des paires (principale, secondaire, H4) sont estimées sans constante, sans pondération. Un panneau par aire retenue.
- **Limite** : les paires ne sont pas indépendantes, car une même commune apparaît dans plusieurs paires. Les intervalles sont calculés par bootstrap **par commune**, et non par paire : 1 000 tirages avec remise des communes de l'aire, chaque paire comptée autant de fois que le produit des tirages de ses deux communes, percentiles 2,5 et 97,5.
- **Verdict de H1**, aire par aire, lu sur la pente principale (`d_part_cadres` sur `d_dist_lyc_prive_min`, intervalle de confiance à 95 %). Sens attendu : plus proche d'un lycée privé, plus de cadres (pente négative). Deux estimations « concordent » si elles ont le même signe et des intervalles qui se recoupent (estimations de 5 et de 10 km, cellule estimable par cellule estimable) ; pour les deux écarts d'accès des paires, on compare seulement le sens.
  - « confirmée » : pente principale dans le sens attendu avec un intervalle qui exclut zéro, pente secondaire dans le sens attendu, estimations de 5 et de 10 km concordantes dans chaque cellule estimable ;
  - « nuancée » : intervalle qui exclut zéro dans le sens attendu, mais pente secondaire de sens contraire ou estimations de 5 et de 10 km non concordantes ;
  - « infirmée » : pente de sens contraire dont l'intervalle exclut zéro, ou **résultat nul établi**, c'est-à-dire un intervalle qui contient zéro avec des cellules estimables aux deux rayons (5 et 10 km) dont les estimations concordent. Un résultat nul n'est jamais dit « établi » sans cellules estimables aux deux rayons ;
  - « non concluante » : tous les autres cas, en particulier un intervalle qui contient zéro sans cellule estimable aux deux rayons.

### 5.4 H2 : hétérogénéité entre aires

- On répète 5.2 et 5.3 aire par aire, puis on compare les écarts. Ce sont les facettes de la Fig. 4.
- **H2 est descriptive** : une seule aire de l'Ouest parmi trois. On compare les estimations aire par aire avec leurs intervalles, au même rayon, sans test de différence entre aires.

### 5.5 H3 : qualité ou simple présence

- **Population** : les communes ayant au moins un lycée retenu (§2.4, public ou privé) à 5 km. Celles dont aucun de ces lycées n'a d'IVAL (59 sur 658 dans les 8 candidates, dont 30 sur 97 à Toulouse et 11 sur 62 à Bordeaux, surtout des ouvertures récentes) forment une catégorie « sans IVAL », montrée à part dans la Fig. 6 et exclue des terciles.
- On croise `evol_cadres_pts` avec `ival_moy_5km` (en terciles), à nombre de lycées accessibles comparable et anneau par anneau.
- **Fig. 6** : `evol_cadres_pts` par tercile d'IVAL, en points avec intervalles, une couleur par aire, la catégorie « sans IVAL » à part.

### 5.6 Robustesse (un tableau récapitulatif)

- Rayons de 3 et 10 km.
- Résultats avec et sans le contrôle des prix au m².
- Part de cadres parmi les 15 ans ou plus (recensement 2022) à la place des 25-54 ans.
- Lycées professionnels et privé hors contrat inclus.
- Commune-centre exclue.
- Communes de moins de 200 actifs exclues.
- Si Lille ou Strasbourg est retenue : communes à moins de 10 km du contour national exclues, car les lycées étrangers manquent à l'annuaire.
- Sans contrôle de densité.
- **Autocorrélation spatiale** : indice I de Moran (packages `esda` et `libpysal`, contiguïté de type Queen) sur `part_cadres_2022`, puis sur les écarts restants après comparaison par anneaux. On interprète ce que cela implique pour les intervalles de confiance.

### 5.7 H4 : lycées et autres infrastructures

- La même fonction `accessibilite.indicateurs` est appliquée aux gares, aux équipements sportifs (Data ES) et aux équipements culturels (BPE). L'APL est utilisée directement, puisqu'elle est déjà calculée par la DREES.
- Toutes les mesures d'accès sont standardisées (centrées réduites) à l'intérieur de chaque aire. On compare leurs associations avec la part de cadres, anneau par anneau et dans les paires contiguës.
- **Fig. 7** : un point par infrastructure avec son intervalle de confiance, triés de la plus forte à la plus faible association.

### 5.8 Règle contre la multiplication des tests

- Seules les spécifications de la section 2.4 constituent les résultats principaux. Tout le reste est présenté comme robustesse ou exploration.
- Si une hypothèse est infirmée, on le dit clairement : on ne cherche pas une autre spécification jusqu'à ce que « ça marche ».

------------------------------------------------------------------------

## 6. Plan du rapport final (`rapport.ipynb`, publié avec Quarto)

**Titre : « À quelques kilomètres près : lycées et géographie des cadres dans trois aires urbaines de province »**

0.  **Résumé** en cinq lignes : la question, les données, le résultat principal, la limite principale.
1.  **Introduction**
    - 1.1 Pourquoi les lycées : Fack et Grenet (2010), le contraste régional public/privé.
    - 1.2 Question et hypothèses H1 à H4 (tableau de la section 1.2).
    - 1.3 Ce que le projet peut et ne peut pas montrer.
2.  **Construire la base : une ligne par commune, quatre familles de variables**
    - 2.1 Schéma du pipeline et tableau des sources.
    - 2.2 Variable à expliquer.
    - 2.3 Variable d'intérêt : l'accessibilité aux lycées (définition, rayon, effet de bord).
    - 2.4 Contrôles et mauvais contrôles.
    - 2.5 Encadré « choix et biais ».
3.  **Trois aires, trois profils**
    - 3.1 Pourquoi ces trois aires (Fig. 1).
    - 3.2 Le gradient centre-périphérie des cadres (Fig. 2).
    - 3.3 La géographie de l'accès aux lycées (Fig. 3).
4.  **À position égale, l'accès aux lycées fait-il une différence ?**
    - 4.1 Comparaison par anneaux (Fig. 4).
    - 4.2 Comparaison entre communes contiguës (Fig. 5).
    - 4.3 L'Ouest est-il différent ?
    - 4.4 Qualité ou présence ? (Fig. 6)
    - 4.5 Robustesse : tableau récapitulatif et indice de Moran.
5.  **Les lycées face aux autres infrastructures** (Fig. 7).
6.  **Conclusion**
    - Tableau des hypothèses (confirmée, nuancée ou infirmée).
    - Limites.
    - Pistes : échelle IRIS, flux migratoires MIGCOM, temps de trajet.
7.  **Annexes**
    - Reproduire le projet.
    - Dictionnaire des variables.
    - Journal des décisions.

**Règles de rédaction.**

- Chaque figure a un titre qui énonce le message (et pas seulement le sujet), des axes nommés avec leurs unités et une source. Elle est suivie de deux ou trois phrases d'interprétation.
- Aucune sortie brute (`describe()`, `head()`) n'est laissée sans commentaire dans le rapport final.
- Le code long vit dans `src/`. Les cellules du rapport appellent des fonctions et ne copient-collent jamais de code d'une cellule à l'autre.
- Taille visée : 7 figures principales, 1 tableau de robustesse, une lecture de 20 à 25 minutes.
- Charte commune dans `figures.py` : couleurs fixes pour le public, le privé et chaque aire, source et champ en note ; matplotlib pour les figures statiques, folium pour les cartes seulement.
- Le titre-message de chaque figure est écrit par le groupe dans le notebook et passé à la fonction de `figures.py` en argument obligatoire, sans valeur par défaut.

------------------------------------------------------------------------

## 7. Organisation du dépôt

```         
projet-cadres-lycees/
├── README.md                  # question, résultats clés, reproduire sur un compte neuf (uv sync, sans BUCKET_S3), date, URL et sha256 des copies gelées, usage de l'IA générative, lien du site
├── PLAN.md                    # ce document
├── CLAUDE.md                  # consignes pour Claude Code (importe PLAN.md)
├── pyproject.toml             # dépendances (gérées avec uv)
├── uv.lock
├── .gitignore                 # data/, .env, __pycache__, _site/, .ipynb_checkpoints
├── .pre-commit-config.yaml    # nb-clean : retire les sorties des notebooks
├── _quarto.yml                # rendu du rapport en site web (GitHub Pages)
├── rapport.ipynb              # LE notebook rendu, exécutable de bout en bout
├── src/cadres_lycees/
│   ├── __init__.py
│   ├── config.py              # aires, rayons, URL, chemins S3, CRS : toutes les constantes ici
│   ├── stockage.py            # lecture et écriture Parquet sur S3, cache local en secours
│   ├── collecte.py            # une fonction par source (téléchargement et cache)
│   ├── nettoyage.py           # harmonisation COG, filtres, variables dérivées
│   ├── geo.py                 # référentiel communes, centroïdes, distances, paires contiguës
│   ├── accessibilite.py       # fonction générique d'accessibilité
│   ├── analyse.py             # anneaux, bootstrap, comparaisons, indice de Moran
│   ├── figures.py             # une fonction par figure, avec une charte graphique commune
│   └── pipeline.py            # construire_base() enchaîne les étapes A à G
├── tests/
│   ├── test_accessibilite.py
│   ├── test_analyse.py        # 3 tests au plus : fusion des anneaux, poids du bootstrap par commune, invariance au sens i − j
│   └── test_geo.py
├── notebooks/exploration/     # brouillons individuels, jamais rendus (prefixe_initiales_sujet.ipynb)
└── docs/
    └── dictionnaire_variables.md
```

**Stockage des données.** Les données sont sur le S3 du SSPCloud, dans `s3://<bucket>/projet-cadres-lycees/`, avec trois sous-dossiers : `raw/` (fichiers sources inchangés), `interim/` (étapes intermédiaires) et `final/`. Les identifiants viennent des variables d'environnement injectées par le SSPCloud, jamais du code ; le nom du bucket vient de la variable `BUCKET_S3`. Si les identifiants AWS ou `BUCKET_S3` manquent, les données vont dans le dossier local `data/`, avec un avertissement (module `warnings`, jamais `print`) : un compte qui n'a pas défini `BUCKET_S3` ne fait donc pas échouer le code.

- **Copie gelée.** Seules les sources qui changent sans prévenir (annuaire, IPS, IVAL, contours de cartiflette, et DVF si elle est utilisée) sont gelées : une copie datée, avec son `sha256` dans `config.py`. Pour ces sources, il n'y a jamais de repli silencieux vers l'URL d'origine : une copie gelée absente, ou dont le `sha256` diffère, fait échouer le code bruyamment. Les zips de l'Insee, permanents, sont téléchargés à leur URL d'origine avec un contrôle du `sha256`.
- **Lecture publique** de `raw/` et de `final/`, pour que le correcteur puisse les charger : **à confirmer par un `curl` anonyme, depuis l'extérieur du compte, avant de s'y appuyer** (le chemin d'URL qu'impose la publication peut changer l'arborescence). Repli si elle n'est pas possible : une release GitHub.

------------------------------------------------------------------------

## 8. Conventions de travail

### 8.1 Git

- La branche `main` est protégée : personne n'y pousse directement.
- Une branche par tâche : `feat/collecte-lycees`, `fix/jointure-cog`, `docs/intro`.
- Chaque branche est fusionnée via une pull request **relue par un autre membre**.
- Les tâches sont des *issues* GitHub. Chaque pull request référence son issue (`Closes #12`).
- Commits petits et fréquents, messages à l'impératif (« Ajoute la fonction d'accessibilité »).
- Jamais deux personnes sur `rapport.ipynb` en même temps : on prévient le groupe avant d'y toucher. `nb-clean` est installé en *pre-commit* pour retirer les sorties des notebooks.

### 8.2 Code

- Python 3.13 et dépendances déclarées dans `pyproject.toml`. Gestion avec `uv`, comme dans l'environnement du cours.
- Dépendances principales : `pandas`, `geopandas`, `pyarrow`, `s3fs`, `requests`, `python-calamine`, `cartiflette`, `libpysal`, `esda`, `matplotlib`, `folium`, `jupyter`, `nb-clean`, `pytest`. `duckdb` vient avec `cartiflette` ; `libpysal` et `esda` sont retirés si l'indice de Moran est sacrifié (§10).
- Fonctions documentées (docstring), annotations de type et noms en français cohérents avec le dictionnaire des variables.
- Aucun chemin ni aucune URL en dur hors de `config.py`.
- Les fonctions de collecte sont **idempotentes** : si le fichier brut est déjà sur S3, elles ne le retéléchargent pas.

### 8.3 Usage de l'IA générative (politique du cours)

- Le cours autorise les assistants de code utilisés avec discernement, mais **interdit le vibe coding** et sanctionne les usages abusifs.
- Chaque membre doit pouvoir expliquer, en soutenance, tout le code du dépôt, et en particulier `accessibilite.py` et `analyse.py`.
- Les interprétations des résultats et le texte du rapport sont écrits par le groupe.

------------------------------------------------------------------------

## 9. Calendrier, rôles et jalons

**Rôles** (chacun est référent d'une dimension, tout le monde code partout) :

- **R1, collecte** : étapes A, B, C, E et sources P2 ;
- **R2, analyse spatiale** : étapes D et F, sections 5.2 à 5.7 ;
- **R3, visualisation et rapport** : `figures.py`, Quarto, structure du rapport, pilotage de la semaine 6.

| Semaine | R1 collecte | R2 analyse spatiale | R3 visualisation et rapport | Jalon de fin de semaine |
|--------------|--------------|--------------|-----------------|--------------|
| **S1** 13-18 oct | Confirmer les URL (sources 8 et 9) ; `stockage.py` ; collecte de l'annuaire par API ; collecte de l'AAV, livrée seule en premier ; collecte de l'IPS | `geo.referentiel_communes` pour les 8 aires candidates ; tableau de support (§2.2, §5.2), commité | Dépôt, `pyproject`, pre-commit, Quarto ; squelette de `rapport.ipynb` ; Fig. 1 provisoire | **Note de cadrage envoyée au chargé de TD** et choix des 3 aires journalisé (tableau de support commité, PR fusionnée, tag `plan-fige` posé après la fusion) ; une PR par membre, relue par un autre. Si S1 glisse : le squelette du notebook d'abord, puis les PR et le choix des aires, jusqu'au 20/10, puis jusqu'au 22/10 (deuxième report, décidé le 20/10) : copies gelées (annuaire, IPS, IVAL, contours) lisibles par un `curl` anonyme depuis l'extérieur du compte (repli : release GitHub), tableau de support calculé depuis ces copies, PR du choix des aires fusionnée et tag posé, et au moins une PR écrite par chacun des deux autres membres (R2 : fusion des anneaux et tableau de support ; R3 : section « Usage de l'IA générative » du README), relue par un autre membre. T5 n'attend que le tag. Si R2 n'a pas ouvert sa PR le 22/10, Giulio écrit la fusion et R2 la relit avec des commentaires visibles ; le tag ne glisse pas au-delà du 24/10. La PR de R3 reste un livrable daté du 22/10, suivi dans `.claude/pilotage.md` |
| **S2** 19-25 oct | Étapes B et C (cadres, lycées, IPS, IVAL) ; harmonisation COG | `accessibilite.py` et ses tests sur données jouets | Charte graphique ; Fig. 1 et 2 | Base communale v0 sur S3, avec les variables des étapes A à C |
| **S3** 26 oct-1 nov | Étape E (DVF, densité) ; début des sources P2 | Étapes D et F sur données réelles ; anneaux | Fig. 3 (carte interactive) ; rédaction des sections 2 et 3 | Base v1 complète pour H1 à H3 ; premières comparaisons |
| **S4** 2-8 nov | Sources P2 (gares, BPE, Data ES, APL) | H1 (anneaux et paires), H2, H3 | Fig. 4, 5 et 6 en version de travail ; rédaction de la section 4 | **Point de décision le 8 novembre** ; **premier test complet sur un SSPCloud neuf** |
| **S5** 9-15 nov | Bonus P3 si de l'avance (MIGCOM avec DuckDB) | H4 ; robustesse ; indice de Moran | Fig. 7 ; versions finales des figures | Analyse complète ; deuxième test complet |
| **S6** 16-22 nov | README, dictionnaire, nettoyage du code | Relecture croisée de la méthode | Rédaction finale : résumé, conclusion, limites | **Gel du code le 22 novembre** |
| **23-24 nov** | Tous | Tous | Tous | Exécution sur un SSPCloud neuf, publication Quarto, **rendu le 24 novembre** |

**Point de décision du 8 novembre.** Il ne sert pas à changer de question.

- Si H1 à H3 sont traitées et robustes, la semaine 5 couvre H4 en entier.
- Sinon, la semaine 5 consolide d'abord H1 à H3, et H4 est réduite à deux infrastructures (gares et APL).

**Soutenance (décembre-janvier).** Le support est construit autour des Fig. 1, 2, 4 et 7. Une répétition chronométrée est prévue, avec une liste de questions probables (pourquoi 5 km ? pourquoi pas de causalité ? que fait votre fonction d'accessibilité ?).

------------------------------------------------------------------------

## 10. Risques et ordre de sacrifice

| Risque | Probabilité | Parade |
|--------------------|--------------------------------|--------------------|
| Le notebook ne tourne pas de bout en bout (moyenne impossible) | Moyenne | Test complet hebdomadaire dès la S4 ; gel du code le 22 novembre |
| Codes communes non concordants entre sources | Élevée | Table de passage dès la S2 ; vérification par `assert` après chaque jointure |
| Trop peu de lycées privés dans certaines couronnes | Moyenne | Indicateur d'accès par rayon ; critère (d) dans le choix des aires |
| L'API de l'annuaire change ou tombe | Faible | Copie des données brutes sur S3 dès le premier téléchargement ; source 4 en secours |
| Fichiers DVF volumineux | Moyenne | Téléchargement par département, filtrage immédiat, Parquet |
| Retard global | Moyenne | Ordre de sacrifice ci-dessous |

**Ordre de sacrifice en cas de retard :** 1. abandonner les bonus P3 ; 2. réduire H4 à deux infrastructures ; 3. abandonner l'indice de Moran (le mentionner dans les limites) ; 4. passer à deux aires au lieu de trois.

**À ne jamais sacrifier** : la section 4.2 (paires contiguës), qui fait l'originalité du projet, et l'exécution complète du notebook.

------------------------------------------------------------------------

## 11. Checklist de rendu (24 novembre)

- [ ] `rapport.ipynb` s'exécute de bout en bout sans erreur sur un service SSPCloud **neuf**, en suivant uniquement le README.
- [ ] Les données sont chargées depuis les copies gelées publiques (sources mutables) ou depuis leur URL d'origine avec contrôle du `sha256` (zips de l'Insee).
- [ ] Test « compte neuf » : un autre membre, sur son propre compte, sans définir `BUCKET_S3`, suit uniquement le README et exécute `rapport.ipynb` de bout en bout.
- [ ] `construire_base()` s'exécute depuis le brut gelé en 30 minutes au plus.
- [ ] Les dépendances s'installent en une commande (`uv sync`).
- [ ] Toute dépendance déclarée est importée dans `src/` ou dans `rapport.ipynb`.
- [ ] Chaque figure a un titre qui énonce le message, des axes nommés, une source et une interprétation.
- [ ] Le résumé, le tableau des hypothèses et les limites sont présents.
- [ ] Le site Quarto est publié et son lien figure dans le README.
- [ ] L'historique Git montre des commits réguliers des trois membres et des pull requests relues.
- [ ] Aucun secret (jeton, identifiant S3) n'apparaît dans le dépôt.
- [ ] Le journal des décisions est à jour.

------------------------------------------------------------------------

## 12. Instructions pour Claude Code : par où commencer

### 12.1 Cadre

Tu assistes un groupe de trois étudiants sur un projet noté. Le cours interdit le *vibe coding*. Les étudiants doivent comprendre et pouvoir défendre chaque ligne. En conséquence :

- Travaille **par petites étapes**, en suivant l'ordre des tickets ci-dessous. Une seule fonction ou un seul fichier à la fois.
- **Explique** brièvement chaque choix non trivial (jointure, projection, filtre) dans ta réponse et dans les docstrings.
- **N'invente jamais** un nom de colonne, un code ou une URL. Charge d'abord un échantillon, affiche le schéma (`df.columns`, `df.dtypes`, `df.head()`), puis écris le code. Si une URL est marquée « à confirmer », demande-la.
- **Ne rédige pas** les interprétations de résultats ni le texte du rapport. Propose au plus une structure.
- Respecte les choix fixés en section 2. Si tu penses qu'un choix doit changer, propose-le et attends la validation. Les étudiants l'ajouteront au journal des décisions.
- Toutes les constantes vont dans `config.py`. Aucun secret dans le code.
- Termine chaque ticket en indiquant les commandes pour tester ce qui a été fait, ainsi qu'un message de commit proposé.

### 12.2 Tickets de démarrage

**Ordre d'exécution** (il diffère de la numérotation) : T0, T1, T2, puis T3 sur les 8 aires candidates (la collecte de l'AAV est livrée seule, en premier), T6 réduit à la collecte de l'IPS et à la figure, tableau de support, choix des 3 aires, puis T4 (semaine 2) et T5. - Le tableau de support (§2.2, §5.2) est un livrable commité dans `docs/`, et non un brouillon de `notebooks/exploration/`, avant que le choix des aires soit journalisé. T4 en reproduit les comptes pour les aires retenues par un `assert` du pipeline (§4, étape D). - Le choix des aires est journalisé (§13) dans une pull request fusionnée dans `main`, avant le premier commit de T5. La ligne de journal cite les comptes exacts du tableau et le hash de son commit. - Un tag annoté `plan-fige` sera posé après cette fusion, sur le commit fusionné dans `main`, puis poussé. L'historique n'est plus réécrit ensuite. - Une pull request par membre dès la semaine 1, relue par un autre membre.

**T0. Squelette du dépôt.** Crée l'arborescence de la section 7 : `pyproject.toml` (dépendances de la section 8.2, Python 3.13, `cartiflette` installé depuis GitHub), `.gitignore`, `.pre-commit-config.yaml` avec nb-clean, un `config.py` minimal et un README squelette. *Fait quand* : `uv sync` fonctionne et `python -c "import cadres_lycees"` ne lève pas d'erreur.

**T1. `stockage.py`.** Fonctions `ecrire_parquet(df, chemin)` et `lire_parquet(chemin)`. Elles utilisent S3 via `s3fs` si les variables d'environnement AWS sont présentes, et un dossier local `data/` sinon. Ajoute aussi `existe(chemin)`. *Fait quand* : un aller-retour écriture puis lecture d'un petit DataFrame fonctionne en local.

**T2. `collecte.annuaire_education(departements)`.** Télécharge via l'API Opendatasoft de data.education.gouv.fr (point d'export plutôt que pagination si possible), filtre sur les départements demandés et les lycées, stocke le brut dans `raw/`. - Commence par interroger l'API sur 10 lignes et affiche le schéma. - Repère avec les étudiants les champs de statut public/privé, de type d'établissement, de voies de formation et de coordonnées. *Fait quand* : un GeoDataFrame des lycées des départements de test est produit, avec le compte par statut affiché.

**T3. `geo.referentiel_communes(aires)`.** Contours via `cartiflette` (vérifier la signature actuelle de `carti_download` dans la documentation du package), passage en Lambert 93, centroïdes, appartenance aux aires (source 8, URL à fournir par les étudiants), commune-centre et `dist_centre_km`. *Fait quand* : les vérifications de l'étape A (section 4) passent pour une aire de test.

**T4. `accessibilite.indicateurs(...)`.** Signature : `indicateurs(communes, points, rayons=(3, 5, 10), prefixe="lyc_prive", attribut=None, marge_km=10) -> DataFrame`. - Utilise une jointure spatiale par zone tampon (buffer) ou `sjoin_nearest`. - Inclut les points situés jusqu'à `marge_km` au-delà de l'aire. - Écris d'abord les tests (`tests/test_accessibilite.py`) sur une grille jouet dont les résultats se calculent à la main. *Fait quand* : `pytest` passe.

**T5. `collecte.evol_struct_rp2022()` et `nettoyage.part_cadres()`.** Télécharge « Évolution et structure de la population » (source 2, contrôle du `sha256`), lit les colonnes du §2.3 pour 2011 et 2022 (numérateur `…_GSEC13_23` et `…_CS3`, dénominateur la somme des 6 groupes) et garde les arrondissements de Lyon sans leur parent 69123. Pas de table de passage : le fichier est en COG 2025. *Fait quand* : les vérifications de l'étape B passent.

**T6. Figure 1 provisoire (choix des aires).** Pour les 8 aires candidates : part de lycées privés sous contrat et écart d'IPS public/privé. Fonction dans `figures.py`, appelée depuis `rapport.ipynb`. *Fait quand* : la figure s'affiche et les étudiants peuvent trancher sur les aires.

### 12.3 Prompt de démarrage suggéré

> « Lis PLAN.md, en particulier les sections 2, 4, 7, 8 et 12. Commence par le ticket T0. Avant d'écrire du code, résume en cinq lignes ce que tu vas faire et attends ma validation. »

------------------------------------------------------------------------

## 13. Journal des décisions

| Date | Décision | Raison | Auteur |
|-----------------|---------------------|-----------------|-----------------|
| 13/10/2026 | Rayon principal 5 km ; lycées généraux, technologiques et polyvalents, privés sous contrat ; variable cible : cadres parmi les actifs de 25-54 ans | Fixé avant les résultats (section 2) | Groupe |
| 13/10/2026 | Source 1 : conversion vers le COG 2025 par la table de passage annuelle 2025 ; dénominateur de la part de cadres = actifs occupés + chômeurs ayant déjà travaillé | Le fichier n'est pas livré en COG 2025 (RP2011 en COG 2013, RP2022 en COG 2024) et c'est la définition des actifs qu'il donne | Giulio |
| 13/10/2026 | `cartiflette==0.4.0` depuis PyPI, version épinglée, au lieu de l'installation GitHub du §12.2 ; appels avec `year=2025` et `simplification=0`, puis `.to_crs(2154)` | L'installation GitHub donne un autre paquet, sans `carti_download` ; par défaut l'appel prend l'année courante, une simplification de 80 et ne publie qu'en EPSG:4326, alors que le §2.1 fixe le COG 2025 et le Lambert 93 | Giulio |
| 13/10/2026 | `pynsee` abandonné | Il impose `pandas<3.0` et n'est pas nécessaire : les fichiers de l'Insee se lisent directement | Giulio |
| 13/10/2026 | `python-calamine` ajouté, xlsx de l'Insee lus avec `engine="calamine"` | openpyxl, le moteur par défaut de pandas, n'ouvre pas ces fichiers ; calamine lit les 4 xlsx testés le 13/10 | Giulio |
| 13/10/2026 | Lycées du §2.4 repérés par `code_nature` (300, 301, 302, 306) et non par les colonnes `voie_*` | Les `voie_*` de l'annuaire sont trop souvent vides ou fausses | Giulio |
| 13/10/2026 | Collecte de l'annuaire : l'export complet est copié tel quel dans `raw/`, puis filtré en pandas, au lieu d'un `where` côté serveur | L'annuaire change chaque jour et les variantes du §5.6 refont le filtre sans retélécharger ; le filtre pandas donne les mêmes 2 571 lignes que le `where` | Giulio |
| 13/10/2026 | Collecte de l'annuaire : une ligne par site, les doublons d'UAI sont traités au nettoyage | 21 lignes pour 9 UAI dans les 8 départements candidats (établissements multi-sites), avec la même commune et les mêmes coordonnées sur toutes les lignes d'un UAI | Giulio |
| 13/10/2026 | Un lycée sans statut public ou privé fait échouer la collecte (l'UAI est nommé) au lieu d'être écarté | Un filtre `== "Public"` perdrait sans erreur un lycée public (`0271911F`, département 27) dont le statut est vide | Giulio |
| 13/10/2026 | Stockage sur S3 si `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY` sont définies, avec le nom du bucket dans la variable d'environnement `BUCKET_S3` ; sinon dossier local `data/` | Le nom du bucket dépend du compte, il ne peut donc pas être écrit dans `config.py` | Giulio |
| 13/10/2026 | pytest et nb-clean (listés au §8.2 parmi les dépendances principales), ruff et pre-commit déclarés en dépendances de développement | Ils servent au développement et non à l'exécution du rapport | Giulio |
| 13/10/2026 | Hooks pre-commit locaux (nb-clean et ruff) lancés avec `uv run` | Ils utilisent les versions de `uv.lock`, comme le reste du projet | Giulio |
| 13/10/2026 | Python borné à `>=3.13,<3.14` | Les dépendances ont été résolues et testées sous Python 3.13 seulement | Giulio |
| 13/10/2026 | A1. `ival_moy_5km` : moyenne simple des `va_acces_2nde` des sessions 2012-2022 par lycée (au moins 5 sessions valides), puis moyenne des lycées du rayon pondérée par la moyenne de `presents_total` ; lycées de moins de 5 sessions comptés dans les `n_lyc_*` et exclus de l'IVAL ; stock = annuaire du 13/10/2026. H3 « non testable avec cette mesure » (ni confirmée ni infirmée) si la fiabilité de `ival_moy_5km` au niveau commune (corrélation des moyennes 2012-2017 et 2018-2022, corrigée par Spearman-Brown) est inférieure à 0,5. Moyenne 2012-2025 en robustesse ; variante « session 2025 seule » abandonnée | La valeur ajoutée d'un lycée est peu stable entre sessions et la rupture de 2024 touche surtout le privé (exploration du 13/10) ; décision prise avant tout calcul de part de cadres. Lu avant la décision, sans cadres : corrélation de 0,50 entre les moyennes 2012-2017 et 2018-2022 au niveau lycée (0,66 corrigée), 0,60 entre 2016 et 2017. Le seuil de 0,5 est une convention (la pente observée serait au plus la moitié de la vraie) | pilote, validé par Giulio |
| 13/10/2026 | A2, sous réserve d'un `curl` anonyme réussi depuis l'extérieur du compte (à confirmer avant de s'y appuyer ; repli : release GitHub). Stockage local `data/` avec avertissement (`warnings`) si `BUCKET_S3` ou les identifiants AWS manquent (remplace la ligne du 13/10 sur le stockage) ; copie gelée datée, avec `sha256` dans `config.py`, des seules sources mutables (annuaire, IPS, IVAL, DVF si utilisée) ; jamais de repli silencieux vers l'URL d'origine pour ces sources (échec bruyant) ; zips de l'Insee à l'URL d'origine avec contrôle du `sha256` ; test « compte neuf » (un autre membre, sans `BUCKET_S3`, README seul) et `construire_base()` en 30 minutes au plus depuis le brut gelé ajoutés à la checklist §11 | Constaté le 13/10 : sur le SSPCloud les identifiants AWS sont définis mais pas `BUCKET_S3`, donc `stockage.existe` échoue ; un `export` en terminal ne se propage pas au noyau Jupyter ; l'annuaire change chaque jour et l'export IVAL est généré à la demande ; §11 | pilote, validé par Giulio |
| 13/10/2026 | A3. Ordre d'exécution T0, T1, T2, T3 sur les 8 candidates (AAV en premier, seule), T6 réduit à l'IPS et à la figure, tableau de support commité (reproduit par un `assert` de T4), choix des 3 aires journalisé dans une PR fusionnée avant le premier commit de T5 ; T4 en semaine 2 ; tag annoté `plan-fige` à poser après cette fusion puis à pousser, sans réécriture d'historique ensuite ; une PR par membre en semaine 1, relue par un autre ; si S1 glisse, squelette du notebook d'abord, PR et choix des aires jusqu'au 20/10 ; valeurs de tous les critères journalisées au choix. La ligne du choix citera les comptes exacts et le hash du commit du tableau | Le choix des aires ne doit pas dépendre de la variable à expliquer ; la Fig. 1 et le tableau de support n'ont besoin ni de T4 ni de T5. Vu avant le tag : supports d'exposition des 8 candidates (communes exposées, cellules, paires), population par aire, stabilité et fiabilité de l'IVAL, et les comparaisons de dénominateur de `docs/exploration_sources.md` §9 (cadres sur occupés contre occupés et chômeurs), qui ne croisent pas l'exposition. Aucune comparaison de la part de cadres selon l'exposition n'a été faite | pilote, validé par Giulio |
| 13/10/2026 | A4. H1 : estimation principale par les paires contiguës avec `d_dist_lyc_prive_min`, contrôlée par l'écart de distance au centre ; `d_n_lyc_prive_5km` secondaire ; anneaux en complément là où les cellules sont estimables (15 communes par groupe, fusion des anneaux, écart de distance au centre entre groupes de 2 km au plus, borne proposée à valider avant `plan-fige`) ; 5 km principal, 10 km rapporté à côté sans le remplacer ; verdict défini en chiffres au §5.3, « résultat nul établi » seulement avec des cellules estimables aux deux rayons ; H2 descriptive ; critères (e) et (f) ajoutés au choix des aires, règle de choix de la candidate de l'Ouest ; `assert` sur les départements de la marge de 10 km | Support de l'exposition mesuré le 13/10 sans donnée sur les cadres : communes exposées à 5 km, 15/183 (Rennes), 19/116 (Nantes), 20/527 (Toulouse) ; sur les 8 candidates, 4 cellules estimables sur 40 à 5 km (Lille 1, Lyon 3) et 11 sur 40 à 10 km avec la règle des 15 par groupe seule ; avec fusion et borne de 2 km, à 10 km Lyon 2, Nantes 1, Rennes 1, Strasbourg 1 et 0 ailleurs ; corrélation de 0,29 (Nantes), 0,44 (Toulouse) et 0,51 (Rennes) entre l'écart de `dist_lyc_prive_min` et l'écart de distance au centre en paires. Le seuil de 15 communes est hérité du §5.2 d'origine, écrit avant les données ; les critères (e) et (f), la borne et les règles de verdict ont été fixés après lecture de ces supports d'exposition et avant tout croisement avec la part de cadres | pilote, validé par Giulio |
| 20/10/2026 | Accessibilité calculée sur tous les lycées retenus de France métropolitaine (2 413 UAI, annuaire du 13/10) au lieu d'une marge de 10 km (§2.4) ; `collecte.annuaire_education()` sans argument ; `0271911F` (statut vide) écarté nommément, tout autre lycée sans statut fait échouer ; `assert` sur les départements de la marge (A4, §4 C) retiré, sans objet | Avec la marge seule, `dist_lyc_prive_min` était faux pour 161 communes sur 2 179 (jusqu'à 39,5 km d'écart à Toulouse) et `dist_lyc_public_min` pour 29 ; comptes à 3, 5 et 10 km identiques ; les départements de l'AAV oubliaient `0560016N` et `0260008T`. Le gel de l'annuaire (A2) devient indispensable : l'annuaire du 20/10 contient `0451844K` (lycée public du Loiret, ouvert le 01/09/2026, absent de la copie du 13/10), sans coordonnées, qui fait échouer `nettoyage.lycees_geo` sur un compte neuf. Vérifié sans donnée sur les cadres | Giulio |
| 20/10/2026 | `accessibilite.indicateurs(communes, points, prefixe, rayons, attribut, poids)` : filtre public/privé avant l'appel, comptes par `sjoin(predicate="dwithin")` bord compris, distance au plus proche sans plafond, moyenne pondérée par `poids` ; `marge_km` supprimé | Une zone tampon est un polygone inscrit dans le cercle et perd des points près du bord ; 10 couples centroïde-lycée sont à moins de 1 m d'un rayon, dont 2 font basculer l'exposition d'une commune au public | Giulio |
| 20/10/2026 | Paires : contiguïté Queen (bord ou point commun) ; `geo.paires_contigues(communes, variables)` ; `d_<v>` = v_i − v_j avec i < j dans l'ordre des codes (sens arbitraire) ; échec si une commune n'a pas de voisine dans son aire | Même voisinage que l'indice de Moran (§5.6) : 5 890 paires sur les 8 candidates, dont 100 par un seul point, identiques à libpysal Queen ; une commune isolée disparaîtrait sans signal | Giulio |
| 20/10/2026 | Comptes de A4 corrigés, sans réécrire la ligne A4 : ils avaient été faits sans les lycées hors des aires. Communes exposées à 10 km (valeur de A4 entre parenthèses) : Strasbourg 53 (29), Lyon 242 (193), Lille 173 (143), Bordeaux 93 (78), Nantes 64 (58), Toulouse 81 (77), Rennes 52 (50), Grenoble 65 (65) ; à 5 km, Rennes 15, Nantes 19 et Toulouse 20 inchangés. Les cellules estimables citées dans A4 sont caduques : seul le tableau de support fait foi | Conséquence de la ligne du 20/10 sur l'accessibilité ; aucune donnée sur les cadres | Giulio |
| 20/10/2026 | Population et densité : `P22_POP` et `SUPERF` de la série historique du recensement 2022 (page 8582555) au lieu de « Évolution et structure » (source 2, gardée pour la robustesse 15 ans ou plus) ; `densite` = `P22_POP` / `SUPERF` ; `nettoyage.population()` au lieu de `nettoyage.densite()` | « Évolution et structure » n'a pas de superficie ; même source pour la population et la superficie ; `P22_POP` entière, sans bruit flottant ; les superficies de l'Insee et de l'IGN diffèrent de plus de 10 % pour 28 unités sur 2 179 (plans d'eau, estuaires), corrélation de rang des deux densités d'au moins 0,997 dans chaque aire | Giulio |
| 20/10/2026 | IVAL : session valide = `va_acces_2nde` renseignée ; poids = moyenne de `presents_total` sur ces sessions ; lycées publiés sous un autre UAI que l'annuaire rattachés session par session, en moyenne pondérée par les présents (Saint-Sébastien-sur-Loire, 3 UAI → `0443088T` ; `0332835C` → `0332346W` ; `0690535G` → `0690574Z`) ; colonnes `ival` et `poids_ival` au lieu de `ival_acces` ; export du 20/10 gelé avec son `sha256` | Une jointure par UAI perdait sans erreur l'IVAL de ces 5 lycées. Résultat, sans donnée sur les cadres : 2 182 des 2 413 lycées ont une IVAL (302 sur 339 dans les 8 aires) ; 599 des 658 communes ayant un lycée à 5 km ont un `ival_moy_5km` | Giulio |
| 20/10/2026 | A5. Texte du plan aligné sur les lignes du 20/10 ci-dessus : effet de bord et session valide (§2.4), commune-centre (§2.5), source de la population (§3.1), fonctions des étapes C à F (§4) ; contours de cartiflette ajoutés aux copies gelées (§7) ; jalon S1 reporté une deuxième fois, au 22/10, avec copies gelées lisibles par un `curl` anonyme (repli : release GitHub), choix des aires, tag et une PR de chacun des deux autres membres ; T5 n'attend que le tag ; si R2 n'a pas ouvert sa PR le 22/10, Giulio écrit la fusion et R2 la relit, le tag ne glissant pas au-delà du 24/10 (§9). Mise en forme seule, sans changement de contenu : listes des §7 et §9 rétablies, `\#`, `\>` et `\<` retirés aux §3.1 et §4 | Le plan guide les tickets et prescrivait encore `filtre`, `departements` et l'`assert` des départements. La règle littérale de la commune-centre donnerait Lyon 3e au grain arrondissement. Le client cartiflette a été réécrit le 26/09, sa simplification par défaut a changé le 06/10, et duckdb télécharge des extensions au premier appel. Un compte neuf simulé a planté le 20/10 faute de copie gelée de l'annuaire. Git n'a qu'un seul auteur au 20/10. Aucune donnée sur les cadres | pilote, validé par Giulio |
| 20/10/2026 | A6. Règles fixées avant tout calcul de cellule et avant le choix des aires : fusion des anneaux (cellule en échec la plus proche du centre d'abord, avec la voisine qui compte le moins de communes, la plus proche du centre à égalité ; fusions séparées par rayon, concordance lue par anneau d'origine) ; borne de 2 km validée, sur des moyennes simples ; estimation de cellule par une régression pondérée par les actifs avec les contrôles du §2.5 ; paires de statut différent sur l'indicateur 0/1 ; corrélation non centrée ; pentes des paires sans constante et sans pondération, Fig. 5 sur paires symétrisées ; bootstrap par commune défini ; distance au contour national pour Lille et Strasbourg seulement, dans le tableau et en robustesse si l'une est retenue ; §1.2 aligné sur A4 ; `tests/test_analyse.py` (3 tests au plus) ; tableau commité et hash cité au journal du choix, avant le tag et le premier commit de T5. Mise en forme seule : liste du §5.2 rétablie | Le sens i − j suit l'ordre des codes : une constante ou une corrélation centrée changeraient si l'on renumérotait les communes. Pentes des paires non pondérées : chaque paire compare deux voisines, et une pondération par la taille donnerait 21 % à 47 % du poids total aux 5 % de paires les plus lourdes selon l'aire (calcul sur la population, 32 % à Lyon pour les 39 paires qui touchent un arrondissement) ; le bruit des petites communes est traité par la robustesse « moins de 200 actifs exclues ». 720 paires de statut différent à 10 km sur l'indicateur 0/1, contre 1 595 avec `d_n_lyc_prive_10km` non nul. Lycées étrangers absents de l'annuaire (Lille 110 communes sur 201, Strasbourg 55 sur 268 à moins de 10 km de la frontière). Règle de fusion fixée sans avoir calculé de cellule avec elle ni avec une autre règle ; borne de 2 km proposée le 13/10. Aucune donnée sur les cadres | pilote, validé par Giulio |
| 20/10/2026 | A7. Densité en logarithme (`log_densite`, `d_log_densite`) partout où elle sert de contrôle, dans la spécification principale comme le prévoit le §2.5 ; « sans contrôle de densité » en robustesse. Population de H3 : communes avec au moins un lycée retenu à 5 km ; les 59 sur 658 dont aucun lycée n'a d'IVAL forment une catégorie à part, hors terciles. Fiabilité de l'IVAL : lycées de la règle A1 ayant au moins 3 sessions valides dans chaque moitié, poids de l'indicateur principal, communes de la population de H3 des 3 aires retenues, corrélation après centrage par aire, Spearman-Brown ; seule la valeur toutes aires ensemble tranche H3, valeurs par aire descriptives, nombre de lycées distincts à côté de chaque valeur ; calculée et journalisée avant le premier commit de T5 | Forme du contrôle fixée sur sa propre distribution, sans donnée sur les cadres : densité de 4 à 19 232 hab/km², asymétrie 8,2 (0,4 en log) ; 43 paires de Lyon et Villeurbanne font 34 % de la somme des carrés de `d_densite` ; `d_log_densite` corrélé à `d_dist_lyc_prive_min` de −0,21 à −0,46 selon l'aire. Les 59 communes sans IVAL sont surtout des ouvertures récentes en périurbain (Toulouse 30 sur 97, Bordeaux 11 sur 62) : les exclure en silence sélectionnerait les communes en croissance. A1 laissait ouverts l'inclusion par moitié, les poids, le périmètre et la valeur qui tranche ; H3 se lit dans chaque aire, d'où le centrage | pilote, validé par Giulio |
| 20/10/2026 | A9. Figures : Fig. 1 avec un point par lycée, part du privé en nombre de lycées et pondérée par les candidats au bac, les deux dimensions du critère (b) ; Fig. 3 en 3 onglets à vérifier au rendu, avec repli, couche des paires de statut différent en dernier ; Fig. 4 en graphique d'estimations par aire, trois panneaux ; Fig. 5 par aire ; Fig. 6 en points avec la catégorie « sans IVAL » ; charte commune, matplotlib et folium seulement ; titres-messages écrits par le groupe, passés en argument obligatoire ; `plotly` et `duckdb` retirés des dépendances directes, `pynsee` retiré du texte (§8.2). Mise en forme seule : liste des règles de rédaction du §6 rétablie | Avis du correcteur du 20/10 : Fig. 1 sans message, 8 cartes sans commentaire. La part pondérée par les candidats au bac est la mesure la plus proche du chiffre en élèves de la DEPP (§1.1), sans nouvelle source. Avec peu de cellules estimables, des panneaux par anneau seraient presque vides. `plotly` n'est utilisé nulle part et `duckdb` n'est importé que par cartiflette. Pas d'interprétation : les titres restent au groupe | pilote, validé par Giulio |
| 20/10/2026 | A10. Téléchargements factorisés dans `stockage.copie_controlee` ; collecte par API gardée comme production unique des copies gelées datées, que le rapport lit ; date, URL et `sha256` documentés dans le README et la section 2.1 du rapport ; `lycees_geo` découpée en quatre fonctions ; listes d'UAI propres aux 3 aires ; le rapport appelle `pipeline.construire_base(aires)` depuis les copies gelées (point ouvert du 13/10 tranché), 30 minutes mesurées en S4 ; toute dépendance déclarée est importée (§4, §7, §11). Mise en forme seule, sans changement de contenu : listes du §0 et du §12.1 rétablies, puces vides du §2.2 retirées | Motif `sha256` répété 4 fois (`collecte.py`) ; compte neuf simulé planté le 20/10 (`0451844K`) ; égalités exactes des listes d'UAI calibrées sur 8 aires (`nettoyage.py`) ; la grille valorise la collecte par API et demande un rendu qui part des données brutes ; avis du correcteur du 20/10. La mise en forme répare la réécriture de l'éditeur Quarto (commit `2ef62fd`) | pilote, validé par Giulio |
| 20/10/2026 | A11. Part de cadres 2011 et 2022 tirée de « Évolution et structure de la population » (source 2, page 8581696) pour toutes les communes : numérateur `C22_POP2554_STAT_GSEC13_23` et `C11_POP2554_CS3`, dénominateur la somme des 6 groupes socioprofessionnels des 25-54 ans (actifs occupés et chômeurs ayant déjà travaillé, dénominateur inchangé) ; fichier en COG 2025, arrondissements de Lyon natifs, plus de table de passage pour cette variable ; séries historiques (source 1) gardées comme contrôle de cohérence, hors pipeline ; critère (f) : coût de Lyon nul pour la variable à expliquer (§2.2, §2.3, §3.1, §4 B, §12.2 T5). Remplace, sans l'effacer, la ligne du 13/10 « Source 1 : conversion vers le COG 2025 par la table de passage annuelle 2025 ; dénominateur… » | Même définition que la source 1 et mêmes valeurs : totaux nationaux égaux (16,18 % en 2011, 20,27 % en 2022) ; hors des aires, égalité commune par commune avec la source 1 passée au COG 2025 (2022 : 32 701 sur 32 701 ; 2011 : 32 688 sur 32 692, les 4 écarts hors des aires) ; Paris et Marseille égaux ; les 9 arrondissements de Lyon y sont, et leur somme égale 69123, égal à la source 1. Seule source qui donne les arrondissements de Lyon avec cette définition (aucun tableau ACT ne croise la CSP avec les chômeurs). Vérifié le 20/10 (`docs/exploration_sources.md` §10, commit `20ee6fb`) sans lire aucune part ni aucun effectif de cadres des 8 aires : pour Lyon et les aires, seulement des présences et des écarts nuls | pilote, validé par Giulio |
|  |  |  |  |