"""Constantes du projet : les choix fixés par le plan (§2) et les paramètres des sources."""

from pathlib import Path

# Lambert 93 (mètres) pour tous les calculs de distance, WGS84 pour les cartes interactives
CRS_CALCUL = 2154
CRS_CARTES = 4326

# Rayons d'accessibilité en km : 5 est le rayon principal, 3 et 10 servent en robustesse
RAYONS_KM = (3, 5, 10)
RAYON_PRINCIPAL_KM = 5

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

# Stockage (PLAN §7) : le S3 du SSPCloud si les identifiants AWS et le nom du bucket sont dans
# l'environnement, sinon le dossier data/ à la racine du dépôt (ignoré par git), avec un
# avertissement
VARIABLES_AWS = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
# Le nom du bucket dépend du compte : chacun le définit dans cette variable d'environnement
VARIABLE_BUCKET_S3 = "BUCKET_S3"
PREFIXE_S3 = "projet-cadres-lycees"
DOSSIER_LOCAL = Path(__file__).parents[2] / "data"

# Annuaire de l'éducation (source 3)
URL_ANNUAIRE = (
    "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "fr-en-annuaire-education/exports/parquet"
)
CHEMIN_RAW_ANNUAIRE = "raw/annuaire_education.parquet"
# Délai d'attente de `requests` par lecture, pas durée totale (le téléchargement dure ~12 s)
DELAI_TELECHARGEMENT_S = 120
# Zonage en aires d'attraction des villes 2020 (source 8), géographie au 01/01/2025. Le zip de
# l'Insee est permanent : on contrôle son sha256 au téléchargement
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
# pas ; P22_POP y est identique dans les 8 aires. Le zip de l'Insee est permanent : on contrôle
# son sha256 au téléchargement (observé le 20/10)
URL_SERIE_RP2022 = (
    "https://www.insee.fr/fr/statistiques/fichier/8582555/base-cc-serie-historique-2022_csv.zip"
)
SHA256_SERIE_RP2022 = "ff0187ec6bb77fd2e5da639c08159368ff152cad0682ee0908358a829830c273"
CHEMIN_RAW_SERIE_RP2022 = "raw/base-cc-serie-historique-2022_csv.zip"
CSV_SERIE_RP2022 = "base-cc-serie-historique-2022.CSV"
# Communes et arrondissements du COG 2025, Mayotte exceptée
NB_LIGNES_SERIE_RP2022 = 34903

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
# Une copie brute par aire d'attraction, pour ne retélécharger que l'aire ajoutée
CHEMIN_RAW_CONTOURS = "raw/contours_aav_{aav}.parquet"
# Pôle ou couronne d'après `CATEAAV2020`. Les codes 13 (pôle secondaire, aucun dans les 8 aires
# candidates) et 30 (hors aire) n'y sont pas : ils feraient échouer `geo.referentiel_communes`
POLE_COURONNE_AAV = {"11": "pole", "12": "pole", "20": "couronne"}
# Communes à arrondissements municipaux des aires candidates (Paris et Marseille n'en font pas
# partie) : Lyon en a 9, de 69381 à 69389. Toute autre commune est une seule unité
NB_ARRONDISSEMENTS = {"69123": 9}
# La commune-centre de l'aire (la plus peuplée du pôle, PLAN §2.5)
CATEGORIE_COMMUNE_CENTRE = "11"

# IPS des lycées (source 5), copie du 13/10/2026 : l'export est identique d'un téléchargement à
# l'autre, et le sha256 fait échouer le code si la source a changé depuis
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
# Lycées de l'IPS situés dans les communes des 8 aires candidates mais absents de `lycees_geo`
# (annuaire du 13/10/2026, pour la rentrée et la mesure ci-dessus : en changer impose de revoir
# cette liste) : trois privés de Saint-Sébastien-sur-Loire fusionnés dans l'annuaire
# sous l'UAI 0443088T, Averroès (hors contrat dans l'annuaire, sous contrat dans l'IPS), un lycée
# agricole privé (Genech), un lycée climatique (nature 310) et une section agricole publique
UAI_IPS_NON_RETENUS = (
    "0352867B",
    "0380097Z",
    "0440256P",
    "0440279P",
    "0441653H",
    "0596281G",
    "0596681S",
)

# IVAL des lycées généraux et technologiques (source 6), copie du 20/10/2026 : l'export est
# identique d'un téléchargement à l'autre (4 essais), et le sha256 fait échouer le code si la
# source a changé depuis
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
# l'annuaire. En changer d'aires ou de règle impose de revoir cette liste
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
