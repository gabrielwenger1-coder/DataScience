# Exploration des sources de données (13/10/2026)

Notes issues de l'exploration en lecture seule des 8 sources P1 du plan, faite le 13/10/2026 par des agents d'exploration. **Aucune donnée n'a encore été nettoyée et `src/` n'existe pas encore.** Les URL, les noms de colonnes et les chiffres ci-dessous ont été observés ce jour-là : les jeux de l'Éducation nationale changent (l'annuaire est mis à jour chaque jour), donc revérifier avant de s'appuyer sur un chiffre. Les noms de colonnes sont copiés tels quels depuis les fichiers.

Pour la suite : `CLAUDE.md` demande de lire la section d'une source avant tout ticket qui la touche, et de la corriger si la réalité diffère.

## 1. Où en est le projet

- **Fait** : le harness Claude Code (`.claude/`, `CLAUDE.md`, `ruff.toml`), cette exploration, et la vérification que les dépendances du plan se résolvent ensemble sous Python 3.13.
- **Pas fait** : aucun ticket. Ni `pyproject.toml`, ni `src/`, ni test.
- **Ordre proposé** :
  1. T0, puis T1 (`stockage.py`).
  2. T2 (annuaire), qui n'est bloqué par rien.
  3. Les entrées de la Fig. 1 : zonage AAV et IPS.
  4. Le choix des 3 aires par les étudiants (jalon S1, avant le 18/10).
  5. T3 et T5 ensuite, pour ne pas régler la question de Lyon avant de savoir si l'aire est retenue.
- **Branche de T0** : le harness n'est pas encore sur `main`, donc créer `feat/squelette` depuis `chore/harness-claude`, ou fusionner la PR du harness d'abord.
- **T0 en 5 lignes (à faire valider)** :
  1. Branche `feat/squelette`.
  2. `pyproject.toml` en Python 3.13 : dépendances du §8.2 sans `pynsee`, plus `python-calamine` et `cartiflette==0.4.0` ; outils de développement pytest, ruff, nb-clean, pre-commit.
  3. Arborescence du §7 : `src/cadres_lycees/` avec `config.py` minimal (URL confirmées ci-dessous, CRS, rayons), `tests/`, `notebooks/exploration/`.
  4. `.gitignore` complété (`.venv/`, `_site/`, `.ipynb_checkpoints`…), `.pre-commit-config.yaml` avec nb-clean, README squelette. Aucune logique métier.
  5. Fait quand : `uv sync` fonctionne et `import cadres_lycees` ne plante pas.

### Corrections factuelles au plan (une ligne chacune au journal §13)

Ce ne sont pas des changements de choix fixés avant les résultats. À faire appliquer par le pilote, avec validation de l'étudiant (le plan n'est modifiable que par lui).

| Constat | Ligne de journal proposée |
|---|---|
| La source 1 n'est pas en COG 2025 : RP2011 est en COG 2013 et RP2022 en COG 2024. | Conversion vers le COG 2025 par la table de passage annuelle 2025 (§8 ci-dessous). Le dénominateur de la source 1 est « actifs occupés + chômeurs ayant déjà travaillé ». |
| `pip install git+https://github.com/inseefrlab/cartiflette` installe un autre paquet (le pipeline de production), sans `carti_download`. | `cartiflette==0.4.0` depuis PyPI, épinglé. Appels avec `year=2025`, `simplification=0`, puis `.to_crs(2154)`. |
| `pynsee` impose `pandas<3.0` et n'est pas nécessaire : les fichiers de l'Insee se lisent directement. | `pynsee` abandonné. |
| Les xlsx de l'Insee ne s'ouvrent pas avec openpyxl, le moteur par défaut de pandas. | `python-calamine` ajouté, avec `engine="calamine"`. Testé le 13/10 : il lit les 4 xlsx (table de passage, AAV, table d'appartenance, séries CSP), seul, sans openpyxl. |
| Les colonnes `voie_*` de l'annuaire sont trop souvent vides ou fausses. | Les lycées sont filtrés par `code_nature` (§3). |

### Décisions en attente

| Décision | Défaut recommandé | Quand |
|---|---|---|
| Filtre des lycées | Celui du plan, tel que défini au §3 ci-dessous. Les variantes (sections rattachées à un LP, lycées militaires, agricoles par drapeau) vont en robustesse. | T2 |
| IPS par aire (Fig. 1) | Moyenne simple des lycées de l'aire, car il n'y a pas d'effectifs. Colonne `ips_voie_gt` pour rester sur le périmètre général et technologique. | Fig. 1 |
| Choix des 3 aires | Aux étudiants. Les données de la Fig. 1 sont prêtes : §7 (communes par aire), §3 (lycées), §4 (IPS). | avant le 18/10 |
| Lyon : arrondissements | Seulement si Lyon est retenue. Les arrondissements viennent alors des tableaux ACT5 (§9), ce qui change légèrement le dénominateur. | après le choix des aires |
| Dénominateur de la variable à expliquer | Fichier série tel quel (occupés + chômeurs ayant déjà travaillé). ACT5 (occupés seulement) si Lyon est retenue avec ses arrondissements. | T5 |
| Fiabilité de l'IVAL pour H3 | À examiner dans `/pilotage`. La valeur ajoutée d'un lycée est peu stable dans le temps (§5). | après T0 |
| Scissions de communes, petites communes, communes à population nulle | À traiter à T5 avec des `assert` explicites. | T5 |

## 2. Pièges qui traversent plusieurs sources

- **Codes en chaîne de caractères, toujours.** `dtype=str` ou équivalent : `REG` revient en entier (`01` devient `1`), `code_departement` de l'annuaire vaut `035`, `AAV2020` vaut `013`, la Corse est `2A`/`2B`.
- **Quatre géographies différentes selon la source** : source 1 en COG 2013 (RP2011) et 2024 (RP2022) ; recensement, cartiflette 2025 et AAV 2025 en COG 2025 ; annuaire, IPS et IVAL en codes courants, où l'on a trouvé 93059 (Pierrefitte-sur-Seine, fusionnée dans 93066) dans l'IPS ; ACT5 2022 en COG 2025.
- **Lyon, Marseille, Paris** : selon la source, parent, arrondissements, ou les deux.

| Source | Lyon (69123) | Marseille (13055) | Paris (75056) |
|---|---|---|---|
| Source 1 (séries CSP) | parent seul | parent seul | arrondissements 75101-75120, sans parent |
| ACT5 (2011 et 2022) | parent (`COM`) et arrondissements 69381-69389 (`ARM`) | parent et 13201-13216 | parent et 75101-75120 |
| Recensement evol-struct | parent et arrondissements (**à dédoublonner**) | idem | idem |
| AAV 2025, `Composition_communale` | parent seul | parent seul | parent seul |
| Table d'appartenance, feuille `ARM` | 9 arrondissements, `AAV2020` = `002` | 16 | 20 |
| cartiflette `COMMUNE_ARRONDISSEMENT` | `INSEE_COM` = parent, `INSEE_COG` = arrondissement | idem | idem |
| Annuaire, IPS, IVAL | arrondissements 693xx (le parent n'apparaît pas) | 132xx (annuaire : une ligne en 13055, non retenue) | 751xx |

  **Piège Fig. 1** : l'annuaire place les lycées de Lyon en 693xx alors que l'AAV n'a que 69123. Rattacher chaque arrondissement à son parent avant la jointure, sinon une quarantaine de lycées disparaissent sans erreur.
- **Moyennes** : une part de cadres ne se moyenne pas. Après une fusion de communes, sommer numérateur et dénominateur.
- **Ne jamais joindre sur un libellé** (`nom_commune`, `LIBGEO`, `libelle_commune`) : libellés tronqués, accents remplacés par `?` dans l'IVAL, noms qui diffèrent selon l'année, un même libellé pour deux codes (« Valence » = `049` et `396`).
- **Dépendances** : `uv add python-calamine` ; `pandas` 3.x se résout sans `pynsee` ; installer `cartiflette==0.4.0` depuis PyPI.

## 3. Annuaire de l'éducation (source 3)

- **Jeu** : `fr-en-annuaire-education` sur data.education.gouv.fr (API Opendatasoft v2.1), 68 562 lignes et 71 champs à la date du 13/10/2026, Licence Ouverte v2.0. Instantané mis à jour **chaque jour**, donc figer une copie brute dans `raw/` dès le premier téléchargement.
- **Base** : `https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education`
- **Endpoints**
  - `/records?where=…&limit=100&offset=0&order_by=identifiant_de_l_etablissement` : `limit` ≤ 100 et `offset + limit` ≤ 10 000 (erreur 400 sinon). `limit=-1` ne renvoie que 100 lignes. À éviter.
  - `/exports/parquet?where=…` : **voie recommandée.** Pas de limite de lignes. GeoParquet, colonne `position` en WKB, CRS84, codes en chaîne. Se lit avec `geopandas.read_parquet` ou `duckdb`. Le jeu entier fait 11 Mo ; avec le filtre ci-dessous, 0,5 Mo.
  - `/exports/csv` : séparateur `;`, BOM UTF-8 (`encoding="utf-8-sig"`) ; lire avec `dtype=str`, sinon `code_departement` devient l'entier 31.
  - `/exports/geojson` : 13 géométries `null` sur les 2 571 retenues.
- **Champs utiles** (noms exacts)

| Besoin | Champ |
|---|---|
| UAI | `identifiant_de_l_etablissement` |
| Nom | `nom_etablissement` |
| Public ou privé | `statut_public_prive` (`Public`, `Privé`, null) |
| Type | `type_etablissement` |
| Nature détaillée | `code_nature` (entier), `libelle_nature` |
| Voies | `voie_generale`, `voie_technologique`, `voie_professionnelle` (texte `"0"` ou `"1"`, null), **inutilisables seules** |
| Contrat du privé | `type_contrat_prive`, `code_type_contrat_prive` |
| Agricole | `lycee_agricole` (`"0"`, `"1"`), `ministere_tutelle` |
| Commune | `code_commune` (5 caractères), `nom_commune` |
| Département | `code_departement` (**3 caractères** : `035`, `02A`, `971`) |
| Coordonnées | `latitude`, `longitude`, `position`, `coordx_origine`, `coordy_origine`, `epsg_origine` |
| Autres | `precision_localisation`, `etat`, `multi_uai`, `etablissement_mere`, `type_rattachement_etablissement_mere`, `date_ouverture`, `date_maj_ligne` |

- **Pas de nombre d'élèves.** Deux jeux d'effectifs existent au catalogue, non inspectés : `fr-en-lycee_gt-effectifs-niveau-sexe-lv` et `fr-en-lycee_pro-effectifs-niveau-sexe-lv`.
- **Filtre du plan (§2.4)**, vérifié : `total_count` = 2 571 lignes (2 542 UAI) en France.
  ```
  type_etablissement="Lycée" and code_nature in (300,301,302,306) and ministere_tutelle!="AGRICULTURE" and not lycee_agricole="1" and (statut_public_prive="Public" or (statut_public_prive="Privé" and code_type_contrat_prive in ("30","31")))
  ```
  Les natures retenues sont, dans les libellés de l'annuaire : 300 LEGT, 301 LET, 302 LEG et 306 lycée polyvalent. `30` est le contrat d'association toutes classes, `31` la partie des classes. Le type `Lycée` isole la partie lycée d'une cité scolaire : la partie collège, typée `Collège`, partage le même UAI.
  - Retenus : 1 674 lignes publiques et 897 privées sous contrat ; en métropole 2 442 lignes (2 413 UAI).
  - Exclus (en lignes) : LP `320` 1 695, sections professionnelles `334` 757, sections générales et technologiques `335` 109, GT ou polyvalent agricole 101, GT ou polyvalent privé hors contrat 275, etc.
- **Dans les 8 départements candidats** (lignes / UAI / public / privé sous contrat)

| Dép. | Lignes | UAI | Public | Privé |
|---|---|---|---|---|
| 035 Rennes | 38 | 37 | 20 | 17 |
| 044 Nantes | 56 | 54 | 27 | 27 |
| 031 Toulouse | 44 | 44 | 32 | 12 |
| 033 Bordeaux | 51 | 51 | 34 | 17 |
| 069 Lyon | 80 | 73 | 39 | 34 |
| 038 Grenoble | 47 | 47 | 35 | 12 |
| 059 Lille | 101 | 99 | 57 | 42 |
| 067 Strasbourg | 42 | 42 | 31 | 11 |
| Total | 459 | 447 | 275 | 172 |

  Un `assert` sur ces comptes protège la jointure avec l'AAV.
- **Doublons d'UAI** : 54 lignes pour 25 UAI parmi les retenus au niveau national, 21 lignes pour 9 UAI dans les 8 départements (établissements multi-sites). `code_commune` et coordonnées sont identiques sur toutes les lignes d'un même UAI : `drop_duplicates("identifiant_de_l_etablissement")` ne perd rien.
- **Coordonnées** : 0 manquante dans les 8 départements ; 13 manquantes sur 2 571 retenus, toutes en Polynésie ou à Wallis. Les annexes situées dans une autre commune sont placées au site principal.
- **Variantes du filtre** (8 départements : lignes / UAI) : + sections `335` rattachées à un LP, 472 / 460 ; exclusion de l'agricole par la seule tutelle, 461 / 449 ; garder un UAI si une ligne a une voie G ou T, 446 / 434 (non recommandé : retire de vrais lycées généraux). 11 lycées militaires ou Légion d'honneur au niveau national, 1 dans les 8 départements (`0381513N`).
- **Pour H3** : 35 des 447 UAI ont une `date_ouverture` postérieure à 2011. L'instantané ne contient que des établissements ouverts.

## 4. IPS des lycées (source 5)

- **Jeu** : `fr-en-ips-lycees-ap2023` (Opendatasoft), moissonné par data.gouv.fr (dataset `664d720768d6ab64e06740f0`). Licence Ouverte v2.0.
- **URL à utiliser** : `https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-lycees-ap2023/exports/csv`. Le lien de data.gouv ajoute `?use_labels=true` et donne des libellés français à la place des noms techniques ; le contenu est identique. Garder les noms techniques.
- **Format** : `;`, UTF-8 avec BOM, point décimal, manquants = chaîne vide. 10 905 lignes, 48 colonnes, une ligne par lycée et par rentrée (clé : `uai` + `rentree_scolaire`). Rentrées 2023-2024 (3 612 lignes), 2024-2025 (3 631), 2025-2026 (3 662). `/records` plafonne à 10 000 lignes : utiliser l'export.
- **Colonnes** : `rentree_scolaire`, `code_region`, `code_region_insee`, `region_academique`, `code_academie`, `academie`, `code_du_departement`, `departement`, `code_insee_de_la_commune`, `nom_de_la_commune`, `uai`, `nom_de_l_etablissement`, `secteur` (`public`, `privé sous contrat`), `type_de_lycee` (`LEGT`, `LPO`, `LP`), `ips_voie_gt`, `ips_voie_pro`, `ips_post_bac`, `ips_etab`, `ecart_type_voie_gt`, `ecart_type_voie_pro`, `ecart_type_etablissement`, plus 27 colonnes de référence `ips_national_*`, `ips_academique_*`, `ips_departemental_*`, **recopiées sur chaque ligne** : ce ne sont pas des variables d'établissement.
- **Manquants** : `ips_voie_gt` 31,5 %, `ips_voie_pro` 42,7 %, `ips_post_bac` 44,5 %, `ips_etab` 5 lignes (toutes privé sous contrat). Les remplissages par type : LEGT `ips_voie_gt` 97,9 % ; LPO 94,2 % ; LP `ips_voie_pro` 99,9 %.
- **Ce qui manque à la source** : pas de coordonnées, pas d'effectifs, pas de privé hors contrat. Le §5.6 du plan (robustesse hors contrat) ne pourra pas utiliser l'IPS.
- **Jointure** : sur `uai`, sans doublon par rentrée. Mais 24 UAI changent de `type_de_lycee` entre rentrées (filtrer par rentrée), 8 changent de commune, 525 changent de nom. Ne garder de cette source que `uai`, `secteur`, `type_de_lycee` et l'IPS ; la géographie vient de l'annuaire.
- **Écart public/privé** (rentrée 2025-2026, métropole, moyennes simples non pondérées de `ips_etab`) : LEGT privé 130,3 contre public 114,9 (+15,4) ; LPO 116,0 contre 102,3 (+13,7) ; LP +17,4. LEGT et LPO regroupés : 126,9 contre 109,1 (+17,8). Écart stable sur les 3 rentrées.
- **Mises en garde de la DEPP** : ne pas sur-interpréter des différences de 3 points ou moins ; la remontée de la 2e PCS a augmenté dans le privé sous contrat à la rentrée 2023 (environ +3 points d'IPS).
- **Données 2025-2026** : ajoutent des COM et la Nouvelle-Calédonie ; un filtre « métropole » = longueur du code département ≤ 2. Le code `99130` (Andorre-la-Vieille) est étranger.

## 5. IVAL, lycées généraux et technologiques (source 6)

- **Jeu** : `fr-en-indicateurs-de-resultat-des-lycees-gt_v2` (data.gouv : `6707515c84dfa4012c3ecd45`). Dernier traitement 2026-04-03, session 2025 incluse.
- **URL à utiliser** : `https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-indicateurs-de-resultat-des-lycees-gt_v2/exports/csv` (sans `use_labels`). L'export est généré à la demande : garder une copie brute sur S3.
- **Format** : `;`, UTF-8 avec BOM, CRLF, point décimal. 32 485 lignes, 88 colonnes, une ligne par `uai` et `annee` (session du bac, 2012 à 2025). 2 546 UAI.
- **Colonnes utiles** : `annee`, `uai`, `libelle_uai`, `secteur`, `code_commune`, `libelle_commune`, `code_departement`, `libelle_departement`, `libelle_academie`, `code_region`, `libelle_region`, `presents_total` (poids, jamais manquant), `eff_2nde`, `taux_acces_2nde` et `va_acces_2nde` (indicateur principal du plan), `taux_reu_total` et `va_reu_total`, `taux_men_total` et `va_men_total`, `eff_1ere`, `eff_term`.
  - Toutes en points de pourcentage et en entiers. `va_acces_2nde` va de −77 à 46, moyenne ≈ −1,1.
  - Pas de colonne de taux attendu : attendu = `taux_acces_2nde` − `va_acces_2nde` (référence : France entière, public et privé sous contrat).
  - `taux_men_total` et `va_men_total` sont vides de 2012 à 2016.
- **Libellés abîmés** (`MARMAE`, `?` à la place des accents) : joindre uniquement sur `uai` et `code_commune`.
- **Manquants** : `va_acces_2nde` manquant sur 580 lignes (1,8 %), dont 58 lycées sans aucune valeur. **Rupture en 2024** : le seuil de présents passe de 20 à 40, donc 4,8 % de manquants en 2024 et 6,0 % en 2025, dont 91 des 140 de 2025 dans le privé sous contrat.
- **Comparabilité dans le temps** : `taux_acces_2nde` n'est pas comparable d'une session à l'autre (moyenne 68,2 en 2012, 76,4 en 2017, 87,9 en 2020, 85,1 en 2025), à cause de changements de définition en 2016 et 2017.
- **Stabilité de `va_acces_2nde`** (corrélation d'un lycée entre deux sessions) : 0,56 à 1 an, 0,43 à 3 ans, 0,32 à 5 ans, 0,18 à 10 ans, 0,12 entre 2012 et 2025 (ICC(1) = 0,34). **Risque pour H3**, qui relie l'IVAL récent à l'évolution des cadres 2011-2022 ; moyenner plusieurs sessions atténue le bruit. Le plan (§3.2) prévoyait ce risque.
- **Ancienne version** (data.gouv `5889d042a3a72974c1f0d607`) : valeurs identiques à la v2 sur les 27 808 lignes communes, donc pas de millésime indépendant pour tester la stabilité ; la v2 contient déjà 14 sessions.
- **Jointure avec l'annuaire** : 94,3 % des 2 457 lycées GT de l'annuaire sont dans l'IVAL 2025 ; 6 UAI IVAL 2025 n'existent pas comme lycée dans l'annuaire. **Trois privés de Saint-Sébastien-sur-Loire** (`0440256P`, `0440279P`, `0441653H`, aire de Nantes) sont fusionnés dans l'annuaire sous l'UAI `0443088T` (multi-sites) : une jointure naïve les perd. 16 UAI changent de `code_commune` selon la session.
- **Non lus** : les guides méthodologiques 2016, 2020 et 2023 (seul celui de 2025 l'a été, partiellement).

## 6. cartiflette, contours communaux (source 7)

- **Installation** : `uv add "cartiflette==0.4.0"` depuis PyPI. Testé avec Python 3.13.15. Dépendances : `duckdb>=1.5`, `geopandas>=1.0.1`, `pyarrow>=17`.
  - `pip install git+https://github.com/inseefrlab/cartiflette` installe `cartiflette-pipeline 0.5.0`, qui n'a pas `carti_download`. La forme qui marche : `…#subdirectory=python-package/cartiflette`.
  - **Épingler la version** : le client a été réécrit le 26/09/2026 (0.2.0), la 0.3.0 (06/10) a changé la simplification par défaut, la 0.4.0 date du 12/10. Les 0.1.x ne lisent pas les millésimes 2023 et plus.
  - Au premier appel, duckdb installe les extensions `httpfs` et `spatial` (accès à extensions.duckdb.org nécessaire). Les données sont lues sur `minio.lab.sspcloud.fr/projet-cartiflette`, sans identifiant. Non observé : un SSPCloud réellement neuf.
- **Signature** (copiée de `inspect.signature`) : `carti_download(values, borders='COMMUNE', filter_by='REGION', territory='metropole', vectorfile_format='auto', year=None, crs=4326, simplification=None, bucket='projet-cartiflette', path_within_bucket='production', provider='IGN', dataset_family='ADMINEXPRESS', source='EXPRESS-COG-CARTO-TERRITOIRE', filename='raw', return_as_json=False, engine='geopandas', con=None, force=False, where=None)`.
- **Trois défauts qui contredisent le plan (§2.1)** : `year=None` vaut l'année courante (2026) donc toujours `year=2025` ; `simplification` vaut 80 par défaut donc passer `simplification=0` (sinon les centroïdes bougent, de 52 m au maximum sur le département 35) ; seul EPSG:4326 est publié (`crs=2154` lève une erreur), donc `.to_crs(2154)`.
- **Appel testé** : `carti_download(values="35", borders="COMMUNE", filter_by="DEPARTEMENT", year=2025, simplification=0)` → 332 communes, EPSG:4326, aucune géométrie vide. Millésimes 2022 à 2026 disponibles. `filter_by` accepte aussi `AIRE_ATTRACTION_VILLES` (par exemple `values="013"` pour Rennes, 183 communes).
- **Colonnes** : `ID`, `NOM`, `INSEE_COM`, `STATUT`, `POPULATION`, `AREA`, `CTCD`, `EPCI`, `EPT`, `ARR`, `CANOV`, `ZE2020`, `UU2020`, `AAV2020`, `BV2022`, `INSEE_DEP`, `INSEE_REG`, `LIBELLE_DEPARTEMENT`, `LIBELLE_REGION`, `PAYS`, `SOURCE`, `geometry`. `AREA` désigne un territoire (`metropole`, `martinique`…), pas une surface. Le millésime de `POPULATION` n'est pas documenté.
- **Exactitude** : les 34 875 communes de 2025 correspondent exactement au fichier Insee `v_commune_2025.csv`. `AAV2020` est identique à la table Insee, mais il n'y a **pas** `CATEAAV2020` (pôle ou couronne) : la source 8 reste nécessaire.
- **Arrondissements** : avec `borders="COMMUNE_ARRONDISSEMENT"`, Lyon passe de 397 à 405 unités. `INSEE_COM` garde le code du **parent** (69123) et n'est pas unique ; le code d'arrondissement est dans `INSEE_COG` (unique, égal à `INSEE_COM` pour les autres communes). `STATUT` vaut `Arrondissement municipal`.
- **Autres** : 6 communes ont `POPULATION == 0`. La commune-centre « la plus peuplée du pôle » serait Lyon 3e au niveau arrondissement : la définir au niveau commune ou par `CATEAAV2020 == '11'`.
- **Alternative si besoin** : `https://geo.api.gouv.fr/communes?codeDepartement=35&format=geojson&geometry=contour&fields=code,nom,population` (COG courant, pas épinglé à 2025).

## 7. Zonage en aires d'attraction des villes 2020 (source 8)

- **Fichier** : « Base des aires d'attraction des villes 2020 », page `https://www.insee.fr/fr/information/4803954`. Lien direct, géographie au 01/01/2025 : `https://www.insee.fr/fr/statistiques/fichier/4803954/AAV2020_au_01-01-2025.zip` (1 104 231 octets ; contient `AAV2020_au_01-01-2025.xlsx`). sha256 du zip : `738f81b1…ee8181`. Le millésime 2026 existe (`…AAV2020_au_01-01-2026.zip`) mais il est identique commune par commune sur ces colonnes : rester sur 2025.
- **Lecture** : feuille `Composition_communale`, lignes 1 à 4 de métadonnées, noms de variables à la ligne 6 : `pd.read_excel(chemin, sheet_name="Composition_communale", header=5, dtype=str, engine="calamine")` → 34 875 lignes, 7 colonnes (testé). Le CSV est lu en `dtype=str` pour garder `013`.
- **Colonnes** : `CODGEO`, `LIBGEO`, `AAV2020`, `LIBAAV2020`, `CATEAAV2020`, `DEP`, `REG`.
- **`CATEAAV2020`** (libellés dans la feuille `Documentation`, à écrire en dur dans `config.py`) : `11` commune-centre (692), `12` autre commune du pôle principal (1 017), `13` commune d'un pôle secondaire (33), `20` commune de la couronne (24 236), `30` commune hors attraction des villes (8 897, c'est-à-dire `AAV2020` = `000`).
- **Les 8 aires candidates** (COG 2025)

| Aire | `AAV2020` | Communes | Pôle (11+12) | Couronne (20) | Commune-centre | Départements présents |
|---|---|---|---|---|---|---|
| Rennes | `013` | 183 | 5 | 178 | 35238 | 22, 35 |
| Nantes | `008` | 116 | 7 | 109 | 44109 | 44, 85 |
| Toulouse | `005` | 527 | 18 | 509 | 31555 | 09, 11, 31, 32, 81, 82 |
| Bordeaux | `006` | 275 | 18 | 257 | 33063 | 17, 33, 40 |
| Lyon | `002` | 397 | 30 | 367 | **69123** | 01, 38, 42, 69 |
| Grenoble | `014` | 204 | 16 | 188 | 38185 | 38 |
| Lille (partie française) | `004` | 201 | 37 | 164 | 59350 | 59, 62 |
| Strasbourg (partie française) | `010` | 268 | 11 | 257 | 67482 | 57, 67, 88 |

  Chaque aire a une seule commune-centre et aucun pôle secondaire. Rennes déborde sur le 22 et Nantes sur le 85 : à inclure dans la requête de l'annuaire.
- **Lyon et les arrondissements** : cette base ne contient que `69123`. Les arrondissements 69381 à 69389 sont dans la **table d'appartenance géographique** (`https://www.insee.fr/fr/statistiques/fichier/7671844/table-appartenance-geo-communes-2025.zip`, feuille `ARM`, 45 lignes : 20 Paris, 16 Marseille, 9 Lyon), avec `AAV2020` = `002` et `COM` = `69123`. Avec les arrondissements, l'aire de Lyon compte 405 unités et la vérification « même nombre de communes que la table AAV » (§4, étape A) ne tient plus telle quelle.
- **Pièges** : un `CODGEO` n'est jamais en double mais « Valence » correspond à deux codes, donc filtrer sur `AAV2020`. 8 897 communes hors aire. La table d'appartenance ne contient ni `CATEAAV2020` ni `LIBAAV2020`.

## 8. Table de passage des codes communes (source 9)

- **Fichier recommandé** : table de passage annuelle 2025, page `https://www.insee.fr/fr/information/7671867`, lien direct `https://www.insee.fr/fr/statistiques/fichier/7671867/table_passage_annuelle_2025.zip` (960 555 octets ; contient `table_passage_annuelle_2025.xlsx`). Ne pas prendre le millésime 2026 de la même page. sha256 du zip : `803527a0…787d595b`.
- **Lecture** : feuille `COM`, titres aux lignes 1 à 4, libellés à la ligne 5, noms de variables à la ligne 6 : `pd.read_excel(chemin, sheet_name="COM", header=5, dtype=str, engine="calamine")` → 36 760 lignes, 47 colonnes, en 2,7 s (testé).
- **Colonnes** : `NIVGEO` (`COM` ou `ARM`), puis pour chaque année de 2003 à 2025 `CODGEO_<année>` et `LIBGEO_<année>`. Une case vide = la commune n'existait pas cette année-là.
- **Une ligne par chemin de filiation, pas par commune** : 850 communes de 2025 ont plusieurs lignes (maximum 22). **Réduire à des paires uniques `(CODGEO_<année>, CODGEO_2025)` avant de joindre**, sinon les sommes sont comptées plusieurs fois.
- **Quelle colonne joindre pour la source 1** : `CODGEO_2013` pour la feuille `COM_2011` et `CODGEO_2024` pour la feuille `COM_2022`, et non l'année du recensement. L'écart est nul dans les deux sens (hors les 20 arrondissements de Paris), ce qui rejoint la documentation de l'Insee.
- **Fusions et scissions** : 837 communes de 2025 sont formées de plusieurs codes de RP2011 (46 pour RP2022). Une scission rend le 1 pour 1 impossible : 55298 (2011) donne 55138 et 55298 ; 76108 et 76676 pour 2011 ; 15141 pour 2022 donne 5 communes. Aucune dans les 8 départements candidats (elles sont dans le 55, le 76 et le 15). Options : zone regroupée (recommandation de l'Insee), répartition par poids, ou exclusion.
- **Poids** : 4,93 % des codes de RP2011 (1,03 % des cadres en emploi) et 0,19 % de ceux de RP2022 (0,07 %) ne sont pas dans le COG 2025 mais ont une cible. Après passage, 18 communes de 2025 n'ont aucune ligne de source (Paris `75056` et Mayotte). Le critère « moins de 1 % sans correspondance » de l'étape B est tenable.
- **Écartés** : la table cumulée `table_passage_geo2003_geo2025` (sans année, mélange toutes les époques, pas d'arrondissements) et le fichier des mouvements `v_mvt_commune_2025.csv` (14 écarts avec la table annuelle sur la géographie 2013, des fusions suivies d'un rétablissement).
- **Changements de département** (4 entre 2011 et 2025) : Freigné 49144 vers 44180, Pont-Farcy 14513 vers 50592, Le Fresne-sur-Loire 44060 vers 49160, Gernicourt 02344 vers 51171. Tous couplés à une fusion.
- **Test** : un `assert` d'une seule cible par code source, sauf les scissions listées.

## 9. Variable à expliquer : séries historiques de population active (source 1)

- **Page** : `https://www.insee.fr/fr/statistiques/1893185`, « Structure de la population active de 25 à 54 ans selon la catégorie socioprofessionnelle, selon le niveau de diplôme, selon le sexe ou le secteur d'activité (1968 à 2022) », parue le 04/12/2025.
- **Fichier** : `https://www.insee.fr/fr/statistiques/fichier/1893185/pop-act2554-csp-cd-6822.zip` (27 601 928 octets ; un xlsx de 29 917 320 octets). sha256 du zip : `cdbcb350a9c1315135471fc7f40e60e578428735eb6b1f8756ec26da82d4e168`. **Pas de version CSV.** La même page propose 5 autres zips, dont `pop-act2554-empl-csp-cd-trav-6822.zip`, qui donne la CSP au **lieu de travail** : ce n'est pas celui-là.
- **Contenu** : 21 feuilles : `Présentation`, `Documentation`, `Modifications_territoriales`, `DEP_1968` à `DEP_2022`, `COM_1968`, `COM_1975`, `COM_1982`, `COM_1990`, `COM_1999`, `COM_2006`, `COM_2011`, `COM_2016`, `COM_2022`. Actifs de 25 à 54 ans, 6 groupes de CSP (1 agriculteurs, 2 artisans-commerçants-chefs d'entreprise, **3 cadres et professions intellectuelles supérieures**, 4 professions intermédiaires, 5 employés, 6 ouvriers), chacun croisé avec la position : 1 en emploi, 2 chômeur. Champ cité : « actifs ayant un emploi et chômeurs ayant déjà eu un emploi, âgés de 25 à 54 ans ».
- **Lecture** : feuille `COM_2022` ou `COM_2011`, noms de variables à la ligne Excel 16, données dès la ligne 17 : `pd.read_excel(chemin, sheet_name="COM_2022", header=15, dtype=str, engine="calamine")` → 38 214 lignes, 18 colonnes (testé), puis conversion des 12 colonnes de valeurs en nombres. Sans calamine : environ 1 000 lignes vides en fin de feuille.
- **Colonnes** : `RR`, `DR`, `CR`, `STABLE`, `DR24`, `LIBELLE`, puis 12 colonnes `csx_rec{CS}taxtypac_rec{T}rpop{ANNEE}` avec CS de 1 à 6 et T = 1 (en emploi) ou 2 (chômeurs). L'année change d'une feuille à l'autre (`rpop2011`, `rpop2016`, `rpop2022`) : construire les noms dans le code.
  - **Cadres** : `csx_rec3taxtypac_rec1rpop2022` + `csx_rec3taxtypac_rec2rpop2022`. Dénominateur : somme des 12 colonnes.
  - **Code commune** = `DR[:2] + CR` (métropole : `DR` sur 2 caractères ; Corse : `2A`/`2B` ; DOM : `DR` sur 3 caractères, prendre les 2 premiers pour obtenir `97101`).
  - Les 364 lignes `DR` = `20` sont des anciens codes corses vides.
- **Géographie** : `COM_2011` = COG au 01/01/2013 ; `COM_2022` = COG 2024 (écart nul avec le COG 2024 ; 68 codes absents du COG 2025 et 8 communes du COG 2025 manquantes). Voir la table de passage (§8).
- **Valeurs** : effectifs pondérés **décimaux** (exploitation complémentaire). Une cellule vide signifie que la commune n'existait pas ce recensement. Parts nationales de cadres : 16,18 % en 2011 et 20,27 % en 2022.
- **Couverture** : 38 214 codes distincts (union des communes de 1968 à 2024). Des données pour 36 683 communes en 2011, 34 937 en 2022, 34 934 aux deux dates ; 1 749 en 2011 seulement (fusionnées depuis) ; 3 en 2022 seulement (55138, 76095, 76601).
- **Petites communes** : 181 communes à zéro actif en 2022 (80 en 2011) : part indéfinie. 57,6 % des communes ont moins de 200 actifs en 2022, mais seulement 7 % des actifs.
- **Pièges** : `STABLE` = `0` s'il y a eu un événement géographique entre 1968 et 2024, ce qui ne rend pas la donnée inutilisable (Lille a `STABLE` = `0` mais inclut déjà Hellemmes et Lomme). Seize communes ont changé de département (feuille `Modifications_territoriales`) : Colombier-Saugnieu a une ligne `38119` vide et une ligne `69299` qui porte les données.
- **Lyon et Marseille** : seulement `69123` et `13055`. **Paris** : 75101-75120, sans 75056.

### Source de substitution : tableaux ACT5

Elle contient les arrondissements et reproduit exactement le fichier série pour les actifs occupés.
- **2022** : `https://www.insee.fr/fr/statistiques/fichier/8581605/TD_ACT5_2022_csv.zip` (11 Mo ; `TD_ACT5V3_2022.csv`, 63 Mo). `;`, format long `NIVGEO;CODGEO;LIBGEO;GS;AGEQ65;SEXE;NB`, 34 858 `COM` et 45 `ARM`. `GS` de 1 à 6 ; `AGEQ65` de `015` à `065` : les 25-54 ans sont `025,030,035,040,045,050`. Point décimal. **COG 2025 exactement.**
- **2011** : `https://www.insee.fr/fr/statistiques/fichier/2048156/BTT_TD_ACT5_2011.zip` (8,6 Mo ; `BTT_TD_ACT5_2011.txt`, 62,5 Mo). `NIVGEO;CODGEO;LIBGEO;CS1_6;AGEQ65;SEXE;NB`, 36 603 `COM` et 45 `ARM`. **Virgule décimale** ; `AGEQ65` de `15` à `65` sans zéro initial : les 25-54 ans sont `25,30,35,40,45,50`.
- **Limite** : actifs occupés seulement, sans les chômeurs. Écart de définition mesuré (cadres sur occupés, contre cadres sur occupés + chômeurs) : 17,38 % contre 16,18 % en 2011, 21,52 % contre 20,27 % en 2022, avec une corrélation de 0,996 entre communes (200 actifs et plus) et un écart médian de 0,62 à 0,69 point.
- **Vérification croisée** : en 2011, égalité avec le fichier série pour les 36 683 communes ; en 2022, égalité pour 34 827 communes sur 34 937, les 110 autres s'expliquant par les fusions de 2025.

## 10. Recensement 2022, évolution et structure de la population (source 2)

- **Page** : `https://www.insee.fr/fr/statistiques/8581696`. **Fichier** : `https://www.insee.fr/fr/statistiques/fichier/8581696/base-cc-evol-struct-pop-2022_csv.zip` (48 961 124 octets ; `base-cc-evol-struct-pop-2022.CSV`, 128,6 Mo, et `meta_base-cc-evol-struct-pop-2022.CSV`). Les données sont diffusées en géographie du 1er janvier 2025.
- **Format** : UTF-8 sans BOM, `;`, CRLF, en-tête ligne 1. 34 903 communes, 313 colonnes : `pd.read_csv(chemin, sep=';', dtype={'CODGEO': str})`.
- **Colonnes utiles** : `CODGEO` ; `P22_POP`, `P16_POP`, `P11_POP` ; tranches d'âge `P22_POP0014`, `P22_POP1529`, `P22_POP3044`, `P22_POP4559`, `P22_POP6074`, `P22_POP7589`, `P22_POP90P`.
  - `P22_POP` a du bruit flottant (`458.999999999999`) : arrondir.
  - Cadres des 15 ans ou plus (**robustesse du plan §2.3 : le plan voit juste**) : 2022 `C22_POP15P_STAT_GSEC13_23` sur `C22_POP15P` ; 2011 `C11_POP15P_CS3` sur `C11_POP15P`. Autres groupes 2022 : `…_GSEC11_21`, `…_GSEC12_22`, `…_GSEC14_24`, `…_GSEC15_25` (employés), `…_GSEC16_26` (ouvriers), `…_GSEC32` (retraités), `…_GSEC40` (autres sans activité). Les retraités et inactifs sont **dans** le dénominateur : ce n'est pas une part parmi les actifs. Parts nationales : 11,4 % en 2022 et 9,5 % en 2011.
  - Variantes par âge : `C22_POP2554_STAT_GSEC13_23` / `C22_POP2554`, et en 2011 `C11_POP2554_CS1` à `CS8`.
- **Superficie absente de ce fichier.** La densité (§2.5) s'obtient depuis la **série historique 2022** (`https://www.insee.fr/fr/statistiques/fichier/8582555/base-cc-serie-historique-2022_csv.zip`, 6,7 Mo, `base-cc-serie-historique-2022.CSV`) : colonne `SUPERF` en km², sans manquants, même ordre de `CODGEO`, avec aussi `P22_POP` et `P11_POP`.
- **Pièges**
  - **Dictionnaire de la page faux** : il nomme les employés `C22_POP15P_STAT_GSEC16_25` (en doublon avec `…_GSEC16_26`). Le fichier et le `meta_*.CSV` donnent `…_GSEC15_25`. Recopier les noms depuis l'en-tête.
  - `REG`, `DEP` et `LIBGEO` sont annoncés par la page mais absents du CSV ; les libellés sont dans `meta_*.CSV` (lignes `COD_VAR == 'CODGEO'`).
  - **Double comptage** : les parents 75056, 69123 et 13055 sont présents avec leurs arrondissements. Retirer les 3 parents garde la France hors Mayotte (71 272 267 → 67 760 573 habitants).
  - 4 communes entièrement vides (15031, 15035, 15047, 15171) ; 6 communes à population 0 (55039, 55050, 55139, 55189, 55239, 55307) : division par zéro à prévoir.
  - 17 communes diffèrent entre ce fichier et la série historique à cause des fusions, et `P11_POP` et `P16_POP` ne sont pas entièrement en COG 2025 (7 communes absorbées ont `P11_POP` manquant). Sans effet sur la robustesse 15+, qui n'utilise que 2022.
  - Les libellés de `meta_*` ne suivent pas le COG 2025.
- **Signalé** : la page « Dossier complet » (5359146, septembre 2026) propose des recensements plus récents (2012, 2017, 2023 en géographie 2026). Le plan reste sur 2022.

## 11. Ce qui n'a pas été vérifié

- **Source 1** : la comparabilité du groupe 3 (cadres) entre 2011 et 2022, qui repose sur la documentation de l'Insee.
- **Source 2** : que `P22_POP` soit la population municipale (cohérent avec 227 830 pour Rennes mais non écrit) ; le fichier xlsx ; la variable `SUPERF` du dossier complet.
- **Annuaire** : quels départements voisins la marge de 10 km autour des aires fait entrer ; les deux jeux d'effectifs du catalogue.
- **IPS** : la pièce jointe de passage PCS vers IPS (absente de l'API) ; la méthode des colonnes `ips_national_*` ; le Parquet généré par data.gouv.
- **IVAL** : les guides 2016, 2020 et 2023 ; la concordance des `code_commune` avec le COG 2025.
- **cartiflette** : un SSPCloud neuf (extensions duckdb) ; le millésime de `POPULATION`.
- **Table de passage** : la légende des codes `MOD` du fichier de mouvements, déduite des lignes.
