"""Constantes du projet : les choix fixés par le plan (§2) et les paramètres des sources."""

from pathlib import Path

# Lambert 93 (mètres) pour tous les calculs de distance, WGS84 pour les cartes interactives
CRS_CALCUL = 2154
CRS_CARTES = 4326

# Rayons d'accessibilité en km : 5 est le rayon principal, 3 et 10 servent en robustesse
RAYONS_KM = (3, 5, 10)

# Les lycées jusqu'à 10 km au-delà de la limite de l'aire comptent, sinon les communes du bord
# paraîtraient mal desservies
MARGE_KM = 10

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

# Codes du filtre des lycées (PLAN §2.4) ; les libellés de la source ("Lycée", "Public"...)
# restent dans collecte.py. `code_nature` : 300 général et technologique, 301 technologique,
# 302 général, 306 polyvalent
NATURES_LYCEES = (300, 301, 302, 306)
# `code_type_contrat_prive` du privé sous contrat : 30 association (toutes classes), 31 (partie)
CONTRATS_PRIVE_RETENUS = ("30", "31")

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
