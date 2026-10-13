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
# Codes du filtre des lycées (PLAN §2.4) ; les libellés de la source ("Lycée", "Public"...)
# restent dans collecte.py. `code_nature` : 300 général et technologique, 301 technologique,
# 302 général, 306 polyvalent
NATURES_LYCEES = (300, 301, 302, 306)
# `code_type_contrat_prive` du privé sous contrat : 30 association (toutes classes), 31 (partie)
CONTRATS_PRIVE_RETENUS = ("30", "31")
