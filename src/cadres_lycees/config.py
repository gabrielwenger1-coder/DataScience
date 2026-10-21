"""Constantes du projet : les choix fixés par le plan (§2) et les paramètres des sources."""

from pathlib import Path

# Lambert 93 (mètres) pour tous les calculs de distance, WGS84 pour les cartes interactives
CRS_CALCUL = 2154
CRS_CARTES = 4326

# Rayons d'accessibilité en km : 5 est le rayon principal, 3 et 10 servent en robustesse
RAYONS_KM = (3, 5, 10)
RAYON_PRINCIPAL_KM = 5

# Comparaison par anneaux (PLAN §5.2, A6) : bornes basses des anneaux de distance au centre, en km
# (le dernier va jusqu'à l'infini), effectif minimal de chaque groupe d'une cellule (exposées et
# non exposées, hérité du plan d'origine) et écart maximal des distances moyennes au centre des
# deux groupes (20 % de la largeur d'un anneau de 10 km, borne validée le 20/10)
ANNEAUX_KM = (0, 5, 10, 20, 30)
EFFECTIF_MIN_GROUPE = 15
ECART_DIST_MAX_KM = 2

# Sorties de `pipeline.construire_base` (PLAN §4, étape G)
CHEMIN_BASE = "final/base_communale.parquet"
CHEMIN_PAIRES = "final/paires.parquet"
# Tableau de support du choix des aires (§5.2), livrable commité dans le dépôt
CHEMIN_TABLEAU_SUPPORT = Path(__file__).parents[2] / "docs" / "tableau_support.md"
# Rayons du tableau de support : le principal et le 10 km rapporté à côté (§5.2)
RAYONS_SUPPORT_KM = (5, 10)
# Aires candidates de l'Ouest, dont au moins une doit être retenue (§2.2, critère a)
AIRES_OUEST = ("Nantes", "Rennes")
# Aires candidates proches d'une frontière terrestre, où les lycées étrangers manquent, et
# distance au contour national en deçà de laquelle une commune est comptée (§5.2, A6). Elle ne
# suit pas `RAYONS_KM` : le plan la fixe à 10 km
AIRES_FRONTALIERES = ("Lille", "Strasbourg")
DIST_FRONTIERE_KM = 10
# Écarts calculés dans les paires de communes contiguës : accès principal et secondaire (§5.3),
# contrôles (§2.5, A7) et exposition 0/1 pour compter les paires de statut différent (§5.2, A6)
VARIABLES_PAIRES = (
    "dist_lyc_prive_min",
    "n_lyc_prive_5km",
    "dist_centre_km",
    "log_densite",
    "expose_lyc_prive_5km",
    "expose_lyc_prive_10km",
)

# Aires d'attraction des villes 2020 candidates : nom -> code AAV2020 (chaîne, le zéro compte)
AIRES_CANDIDATES = {
    "Rennes": "013",
    "Nantes": "008",
    "Toulouse": "005",
    "Bordeaux": "006",
    "Lyon": "002",
    "Grenoble": "014",
    "Lille": "004",
    "Strasbourg": "010",
}
# Aires retenues le 20/10 parmi les candidates, sur le tableau de support (PLAN §2.2, §13)
AIRES_RETENUES = {aire: AIRES_CANDIDATES[aire] for aire in ("Nantes", "Lyon", "Strasbourg")}

# Stockage (PLAN §7) : le S3 du SSPCloud si les identifiants AWS et le nom du bucket sont dans
# l'environnement, sinon le dossier data/ à la racine du dépôt (ignoré par git), avec un
# avertissement
VARIABLES_AWS = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
# Le nom du bucket dépend du compte : chacun le définit dans cette variable d'environnement
VARIABLE_BUCKET_S3 = "BUCKET_S3"
PREFIXE_S3 = "projet-cadres-lycees"
DOSSIER_LOCAL = Path(__file__).parents[2] / "data"
# Adresses de lecture publique des copies gelées des sources qui changent sans prévenir (PLAN §7,
# A2) : le dossier raw/ du bucket de Giulio, qui doit rester accessible jusqu'à la soutenance,
# puis en repli une release GitHub du dépôt (les deux hébergements, choix de l'étudiant du
# 20/10). Le sha256 de chaque copie est contrôlé à chaque lecture, quelle que soit sa provenance
URL_COPIES_S3 = "https://minio.lab.sspcloud.fr/gfogato/projet-cadres-lycees/"
URL_COPIES_RELEASE = (
    "https://github.com/gabrielwenger1-coder/DataScience/releases/download/donnees-20261020/"
)

# Annuaire de l'éducation (source 3) : export complet de l'API, gelé le 13/10/2026. L'annuaire
# change chaque jour : le 20/10, un lycée sans coordonnées (0451844K) y est apparu
URL_ANNUAIRE = (
    "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "fr-en-annuaire-education/exports/parquet"
)
CHEMIN_RAW_ANNUAIRE = "raw/annuaire_education_20261013.parquet"
SHA256_ANNUAIRE = "2c493f152bc8fc682aa8b1f063392015941bcff36bae2ae59a4d1a1e6334e94a"
# Délai d'attente de `requests` par lecture, pas durée totale (le téléchargement dure ~12 s)
DELAI_TELECHARGEMENT_S = 120
# Zonage en aires d'attraction des villes 2020 (source 8), géographie au 01/01/2025. Le zip de
# l'Insee est permanent : il est lu à son URL d'origine, et son sha256 est contrôlé à chaque lecture
URL_AAV = "https://www.insee.fr/fr/statistiques/fichier/4803954/AAV2020_au_01-01-2025.zip"
SHA256_AAV = "738f81b12832fe294bd24ddbfe3a31830c20d850143fc8b4393f18d4b8ee8181"
CHEMIN_RAW_AAV = "raw/AAV2020_au_01-01-2025.zip"
XLSX_AAV = "AAV2020_au_01-01-2025.xlsx"
FEUILLE_AAV = "Composition_communale"
# Les noms de variables sont à la ligne 6 de la feuille, les lignes 1 à 4 sont des métadonnées
ENTETE_AAV = 5
# Nombre de communes du COG 2025, le même que dans les contours de cartiflette
NB_COMMUNES_AAV = 34875
# Codes de `CATEAAV2020` (feuille Documentation du classeur) : 11 commune-centre, 12 autre commune
# du pôle principal, 13 commune d'un pôle secondaire, 20 commune de la couronne, 30 commune hors
# attraction des villes. Un code inconnu fait échouer la lecture
CATEGORIES_AAV = ("11", "12", "13", "20", "30")

# Série historique du recensement 2022 : population et superficie (km²) en COG 2025,
# arrondissements municipaux et communes parentes ensemble. Elle remplace la source 2 du plan
# (« Évolution et structure », §3.1) pour la population et la superficie, que ce fichier-là n'a
# pas ; P22_POP y est identique dans les 8 aires. Le zip de l'Insee est permanent : il est lu à son
# URL d'origine, et son sha256 (observé le 20/10) est contrôlé à chaque lecture
URL_SERIE_RP2022 = (
    "https://www.insee.fr/fr/statistiques/fichier/8582555/base-cc-serie-historique-2022_csv.zip"
)
SHA256_SERIE_RP2022 = "ff0187ec6bb77fd2e5da639c08159368ff152cad0682ee0908358a829830c273"
CHEMIN_RAW_SERIE_RP2022 = "raw/base-cc-serie-historique-2022_csv.zip"
CSV_SERIE_RP2022 = "base-cc-serie-historique-2022.CSV"
# Communes et arrondissements du COG 2025, Mayotte exceptée
NB_LIGNES_SERIE_RP2022 = 34903

# Carte de la part de cadres par IRIS (source 16 bis, A18) : bases infracommunales « Activité
# des résidents », en IRIS et COG 2024 pour 2022, en géographie 2013 pour 2011. Seule la tranche
# des 15-64 ans y croise la CSP : ce n'est pas la variable du §2.3 (25-54 ans). Zips permanents
# de l'Insee, sha256 observés le 20/10
URL_ACTIVITE_IRIS_2022 = (
    "https://www.insee.fr/fr/statistiques/fichier/8647006/base-ic-activite-residents-2022_csv.zip"
)
SHA256_ACTIVITE_IRIS_2022 = "f4aefb7fab425b9f7eb802e2afb475908bbf2186e0d88f542cf7a67fc70623cb"
CHEMIN_RAW_ACTIVITE_IRIS_2022 = "raw/base-ic-activite-residents-2022_csv.zip"
CSV_ACTIVITE_IRIS_2022 = "base-ic-activite-residents-2022.CSV"
NB_LIGNES_ACTIVITE_IRIS_2022 = 49276
URL_ACTIVITE_IRIS_2011 = (
    "https://www.insee.fr/fr/statistiques/fichier/2028668/infra-activite-resident-2011.zip"
)
SHA256_ACTIVITE_IRIS_2011 = "05076a23c7a3e6bab7aadae8e1b12c17ed1a2aff395340edd59df1474719e7ea"
CHEMIN_RAW_ACTIVITE_IRIS_2011 = "raw/infra-activite-resident-2011.zip"
XLS_ACTIVITE_IRIS_2011 = "base-ic-activite-residents-2011.xls"
NB_LIGNES_ACTIVITE_IRIS_2011 = 50867
# Actifs de 15 à 64 ans des 6 groupes socioprofessionnels, du groupe 1 au groupe 6 (le 3 : cadres)
ACTIFS_1564_IRIS_2022 = (
    "C22_ACT1564_STAT_GSEC11_21",
    "C22_ACT1564_STAT_GSEC12_22",
    "C22_ACT1564_STAT_GSEC13_23",
    "C22_ACT1564_STAT_GSEC14_24",
    "C22_ACT1564_STAT_GSEC15_25",
    "C22_ACT1564_STAT_GSEC16_26",
)
ACTIFS_1564_IRIS_2011 = (
    "C11_ACT1564_CS1",
    "C11_ACT1564_CS2",
    "C11_ACT1564_CS3",
    "C11_ACT1564_CS4",
    "C11_ACT1564_CS5",
    "C11_ACT1564_CS6",
)
CADRES_1564_IRIS_2022 = "C22_ACT1564_STAT_GSEC13_23"
CADRES_1564_IRIS_2011 = "C11_ACT1564_CS3"
# Seuil indicatif du §3.2 (200 actifs), appliqué à chaque IRIS et aux deux dates : en dessous, la
# part repose sur quelques dizaines de cadres au plus, dont le coefficient de variation dépasse
# 18 % sous 50 cadres (feuille « Précision » de la base 2011)
SEUIL_ACTIFS_IRIS = 200
# Contours des IRIS des aires retenues (cartiflette 0.4.0, COG 2025, sans simplification),
# copies gelées du 21/10
CHEMIN_RAW_CONTOURS_IRIS = "raw/contours_iris_{aav}_20261021.parquet"
SHA256_CONTOURS_IRIS = {
    "008": "61e52233fcdd7fe09d0f0350b6a5060719ca83f0a56c7710848a5ae35d34ff23",
    "002": "5c77cb03f2cfb55e3e2634218f4f94b6b43f13ed1496e85572919dc271b43018",
    "010": "15b57329479d4261de4a443b9b4458332f92692b286caecbb270a3b678aad82c",
}
# Code IRIS des contours (COG 2025) -> code des données 2022 (COG 2024), quand il a changé :
# Porte des Pierres Dorées, 69159 en 2024, devenue 69114 en 2025
IRIS_RECODES_2025_2024 = {"691140000": "691590000"}
# Table de passage annuelle des codes communes 2025 (source 9) : elle repère les communes qui en
# ont absorbé d'autres entre la géographie des données 2011 (2013) et celle de 2022 (2024)
URL_PASSAGE_COG = (
    "https://www.insee.fr/fr/statistiques/fichier/7671867/table_passage_annuelle_2025.zip"
)
SHA256_PASSAGE_COG = "803527a040748f4c7dc5e97777cb5838e8b7d4cc36d0b182f53a83e9787d595b"
CHEMIN_RAW_PASSAGE_COG = "raw/table_passage_annuelle_2025.zip"
XLSX_PASSAGE_COG = "table_passage_annuelle_2025.xlsx"

# Codes du filtre des lycées (PLAN §2.4) ; les libellés de la source ("Lycée", "Public"...)
# restent dans collecte.py. `code_nature` : 300 général et technologique, 301 technologique,
# 302 général, 306 polyvalent
NATURES_LYCEES = (300, 301, 302, 306)
# `code_type_contrat_prive` du privé sous contrat : 30 association (toutes classes), 31 (partie)
CONTRATS_PRIVE_RETENUS = ("30", "31")
# Lycées de métropole retenus par le type, la nature et la tutelle, mais dont l'annuaire du
# 13/10/2026 ne donne pas le statut public ou privé : leur secteur est inconnu, ils sont écartés.
# 0271911F (Eure, ouvert en 2024) n'est pas non plus dans l'IPS ; il est à 188 km de l'aire
# candidate la plus proche
UAI_SANS_STATUT = ("0271911F",)

# Contours communaux (source 7), via cartiflette. Le COG de référence est celui de 2025
# (PLAN §2.1) : sans `year`, cartiflette prendrait l'année courante ; sans `simplification=0`, il
# simplifierait les contours (les centroïdes bougeraient jusqu'à 52 m) ; il ne publie qu'en WGS84
ANNEE_COG = 2025
SIMPLIFICATION_CONTOURS = 0
# Une copie gelée par aire d'attraction, du 13/10/2026 : les données de cartiflette sont lues sur
# son serveur, qui peut changer, et son client a déjà changé de comportement par défaut
CHEMIN_RAW_CONTOURS = "raw/contours_aav_{aav}_20261013.parquet"
SHA256_CONTOURS = {
    "002": "5fc255ef5f92c540c5037f793c15c24007642c7cdce256a1e4f47d516176f231",
    "004": "6ff1e4bc0675ab567b7af3eb506774c0740ab855c5f333c66ee6b8fe1eb89982",
    "005": "c42afd4910a9a6907c54e2f8d476b8a4b6db3630bf9ffdff7b41cedf8a3b2c6e",
    "006": "6e0cb9a94a69887fd123a2d57c49068aa25b207da9541813652c00f1b2930c28",
    "008": "54665ed725b9ae364166d6dc76cd09b71b8e42397916e6fe564d8f0308786e59",
    "010": "454d27768198bb48be5882987f3aa36f88902add34bf443dff0cd37cc8be7790",
    "013": "c846f8d895d3121435037f5c04054a9e2275bb95e2de1791cae61498550b4cec",
    "014": "a1d13c20cc9565de3e2b3bb78b8d020076bae7c2a94ac2648d7aa96aa0699357",
}
# Contours des départements, copie gelée du 20/10/2026 : leur union donne le contour de la France
# métropolitaine, dont on mesure la distance pour Lille et Strasbourg (frontière, A6)
CHEMIN_RAW_DEPARTEMENTS = "raw/contours_departements_20261020.parquet"
SHA256_DEPARTEMENTS = "a6e4d3b3a7657f61b8fe9b710efa5f50c0cab76cde0d522f4cfd4adfdbe405ca"
# Départements de métropole, Corse comprise (2A et 2B)
NB_DEPARTEMENTS_METROPOLE = 96
# Pôle ou couronne d'après `CATEAAV2020`. Les codes 13 (pôle secondaire, aucun dans les 8 aires
# candidates) et 30 (hors aire) n'y sont pas : ils feraient échouer `geo.referentiel_communes`
POLE_COURONNE_AAV = {"11": "pole", "12": "pole", "20": "couronne"}
# Communes à arrondissements municipaux des aires candidates (Paris et Marseille n'en font pas
# partie) : Lyon en a 9, de 69381 à 69389. Toute autre commune est une seule unité
NB_ARRONDISSEMENTS = {"69123": 9}
# La commune-centre de l'aire, définie par l'Insee (`CATEAAV2020` = 11, PLAN §2.5)
CATEGORIE_COMMUNE_CENTRE = "11"

# IPS des lycées (source 5) : export de l'API gelé le 13/10/2026 ; le rapport lit la copie gelée,
# jamais l'API
URL_IPS = (
    "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "fr-en-ips-lycees-ap2023/exports/csv"
)
SHA256_IPS = "31b2aafd8fb4597608c55f8f78f7144444a350df795111a651fb5222ee9c8aa7"
CHEMIN_RAW_IPS = "raw/ips_lycees_20261013.csv"
NB_LIGNES_IPS = 10905
# Rentrée et mesure de l'écart d'IPS public/privé (Fig. 1, critère (b) du §2.2) : la rentrée la
# plus récente, et `ips_voie_gt` pour rester sur la voie générale et technologique
RENTREE_IPS = "2025-2026"
COLONNE_IPS = "ips_voie_gt"
# Types de lycée de l'IPS retenus : les lycées professionnels (LP) sortent du périmètre du §2.4
TYPES_LYCEES_IPS = ("LEGT", "LPO")
# Lycées de l'IPS situés dans les communes des 8 aires candidates mais absents des lycées retenus
# (annuaire du 13/10/2026, pour la rentrée et la mesure ci-dessus : en changer impose de revoir
# cette liste) : trois privés de Saint-Sébastien-sur-Loire fusionnés dans l'annuaire sous l'UAI
# 0443088T, Averroès (hors contrat dans l'annuaire, sous contrat dans l'IPS), un lycée agricole
# privé (Genech), un lycée climatique (nature 310) et une section agricole publique. Seuls ceux
# des aires étudiées sont attendus : la liste vaut pour toute partie des 8 candidates
UAI_IPS_NON_RETENUS = (
    "0352867B",
    "0380097Z",
    "0440256P",
    "0440279P",
    "0441653H",
    "0596281G",
    "0596681S",
)

# IVAL des lycées généraux et technologiques (source 6) : export de l'API gelé le 20/10/2026 ;
# le rapport lit la copie gelée, jamais l'API
URL_IVAL = (
    "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "fr-en-indicateurs-de-resultat-des-lycees-gt_v2/exports/csv"
)
SHA256_IVAL = "6ab77b391e3405f5157bb942d4548d5f1cfbacd94e76dd52b93db9b370de8658"
CHEMIN_RAW_IVAL = "raw/ival_lycees_gt_20261020.csv"
NB_LIGNES_IVAL = 32485
# Règle A1 (PLAN §2.4) : sessions du bac retenues, entre les deux recensements, et nombre
# minimal de sessions où la valeur ajoutée est renseignée
PREMIERE_SESSION_IVAL = 2012
DERNIERE_SESSION_IVAL = 2022
NB_SESSIONS_MIN_IVAL = 5
# Test de fiabilité de l'IVAL (PLAN §3.2, A7) : les deux moitiés de la période et le nombre minimal
# de sessions valides dans chacune
MOITIES_IVAL = ((2012, 2017), (2018, 2022))
NB_SESSIONS_MIN_MOITIE = 3
# Lycées publiés dans l'IVAL sous un autre UAI que celui de l'annuaire du 13/10/2026 : leurs
# sessions sont rattachées à l'UAI de l'annuaire, avec la même règle dans toutes les aires (choix
# du 20/10). Les trois lycées privés de Saint-Sébastien-sur-Loire, regroupés en 2026 sous un
# nouvel UAI ; la section d'enseignement général du lycée Philippe Cousteau (Bordeaux), qui
# porte son IVAL ; Chevreul Lestonnac (Lyon 7e), absorbé en 2019
UAI_IVAL_RATTACHES = {
    "0440256P": "0443088T",
    "0440279P": "0443088T",
    "0441653H": "0443088T",
    "0332835C": "0332346W",
    "0690535G": "0690574Z",
}
# Lycées de l'IVAL situés dans les communes des 8 aires candidates, qui remplissent la règle A1
# mais ne sont pas des lycées retenus (après rattachement) : lycées professionnels (0330018R,
# 0590125R), lycée climatique (0380097Z), lycée agricole (0596281G), hors contrat dans
# l'annuaire (0596681S Averroès, 0694086S Al Kindi) et Sainte-Claire (0593113N), absent de
# l'annuaire. Seuls ceux des aires étudiées sont attendus : la liste vaut pour toute partie des
# 8 candidates. Changer de règle impose de la revoir
UAI_IVAL_NON_RETENUS = (
    "0330018R",
    "0380097Z",
    "0590125R",
    "0593113N",
    "0596281G",
    "0596681S",
    "0694086S",
)

# Secteur de l'annuaire (`statut_public_prive`) -> secteur du projet
SECTEURS = {"Public": "public", "Privé": "prive"}
# Secteur de l'IPS (`secteur`) -> secteur du projet
SECTEURS_IPS = {"public": "public", "privé sous contrat": "prive"}
# Couleurs des figures, les mêmes partout : bleu et orange pour les secteurs, qui restent
# distincts en cas de daltonisme ; gris pour le texte et pour relier deux points
COULEURS_SECTEURS = {"public": "#2a78d6", "prive": "#eb6834"}
COULEUR_TEXTE = "#52514e"
COULEUR_LIAISON = "#c3c2b7"
# Grille des axes, très claire pour rester en arrière-plan
COULEUR_GRILLE = "#ececea"
# Bande de fond qui met en avant les aires retenues parmi les candidates (Fig. 1, PLAN §5.1)
COULEUR_FOND_RETENUES = "#f0efec"
# Date de l'annuaire de l'éducation affichée dans la source des figures
DATE_ANNUAIRE = "13/10/2026"
# Secteurs écrits en toutes lettres dans les légendes et les infobulles
LIBELLES_SECTEURS = {"public": "public", "prive": "privé sous contrat"}

# Fig. 3 : classes de distance au lycée privé le plus proche, par leurs bornes supérieures en km
# (incluses). Les rayons du §2.4 en sont les premières bornes : être à 5 km ou moins du plus
# proche, c'est avoir au moins un lycée privé dans le rayon de 5 km. Au-delà de 20 km, les
# communes les plus éloignées sont regroupées
BORNES_DISTANCE_KM = (*RAYONS_KM, 20)
# Palette ColorBrewer « Greens » à 5 classes, du plus proche (foncé) au plus loin (clair) : une
# seule teinte, ni bleu ni orange, réservés aux secteurs des lycées
COULEURS_DISTANCE = ("#006d2c", "#31a354", "#74c476", "#bae4b3", "#edf8e9")
# Tolérance de simplification des contours, pour l'affichage seulement : à peu près la racine
# carrée de l'aire des triangles retirés (algorithme de Visvalingam-Whyatt de shapely), soit
# des limites déplacées jusqu'à 150 m environ. Le GeoJSON des 8 aires passe de 14,5 à 7 Mo ;
# les calculs gardent les contours exacts
SIMPLIFICATION_CARTE_M = 50
# Fonds de carte sans clé d'accès, nommés comme dans xyzservices (folium les reconnaît) : le
# gris laisse lire les couleurs des communes, le plan IGN donne les noms de lieux. CARTO, le fond
# clair habituel, exige une clé depuis 2026 (constaté le 20/10)
FONDS_CARTE = {"Fond gris (Esri)": "Esri.WorldGrayCanvas", "Plan IGN": "GeoportailFrance.plan"}

# Carte IRIS (A18) : classes de la part de cadres parmi les actifs de 15 à 64 ans, en %, par
# leurs bornes (basse incluse), les mêmes pour 2011 et 2022 et fixées sans regarder les aires
# retenues ; palette ColorBrewer « Purples » à 6 classes, une seule teinte, ni bleu ni orange
# (secteurs) ni vert (Fig. 3). Les IRIS non comparables sont hachurés en gris
BORNES_PART_CADRES_IRIS = (10, 20, 30, 40, 50)
COULEURS_PART_CADRES_IRIS = ("#f2f0f7", "#dadaeb", "#bcbddc", "#9e9ac8", "#756bb1", "#54278f")
COULEUR_IRIS_NON_COMPARABLE = "#e3e2de"
# Demi-côté, en km, du carré de zoom sur la ville-centre, où les IRIS sont trop petits pour se
# lire à l'échelle de l'aire : 7 km couvrent la commune-centre des 3 aires (Lyon avec ses
# arrondissements et Villeurbanne)
ZOOM_IRIS_KM = 7
