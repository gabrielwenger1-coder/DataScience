"""Collecte des sources de données : copies brutes dans raw/, contrôlées par leur sha256."""

import hashlib
import io
import zipfile

import geopandas as gpd
import pandas as pd
import requests
from cartiflette import carti_download

from cadres_lycees import config, stockage


def _copies_publiques(chemin: str) -> list[str]:
    """Renvoie les URL publiques d'une copie gelée : le bucket du projet, puis la release."""
    return [config.URL_COPIES_S3 + chemin, config.URL_COPIES_RELEASE + chemin.removeprefix("raw/")]


def geler_annuaire(chemin: str) -> str:
    """Écrit à `chemin` l'export complet de l'annuaire par l'API et renvoie son sha256.

    Produit une copie gelée : celle du 13/10/2026 vient de là. Le rapport ne l'appelle pas, il
    lit la copie gelée (`annuaire_education`). Mode d'emploi dans le README.
    """
    # Un chemin daté déjà pris est une copie gelée, peut-être publique : on ne l'écrase jamais
    assert not stockage.existe(chemin), f"{chemin} existe déjà : choisir un autre chemin daté."
    reponse = requests.get(config.URL_ANNUAIRE, timeout=config.DELAI_TELECHARGEMENT_S)
    reponse.raise_for_status()
    # Une réponse 200 peut être tronquée ; "PAR1" ouvre et ferme tout fichier Parquet
    assert reponse.content.startswith(b"PAR1") and reponse.content.endswith(b"PAR1"), (
        "L'export de l'annuaire n'est pas un fichier Parquet complet : rien n'a été enregistré."
    )
    stockage.ecrire_octets(reponse.content, chemin)
    return hashlib.sha256(reponse.content).hexdigest()


def annuaire_education() -> gpd.GeoDataFrame:
    """Renvoie les lycées de France métropolitaine de l'annuaire de l'éducation.

    Lycées généraux, technologiques et polyvalents, publics ou privés sous contrat (PLAN §2.4),
    repérés par `code_nature` car les `voie_*` de l'annuaire sont trop souvent vides. Toute la
    métropole est gardée, pas seulement les aires et une marge autour : le lycée le plus proche
    d'une commune du bord peut être bien au-delà de l'aire. Une ligne par site : un UAI
    multi-sites apparaît plusieurs fois (dédoublonné au nettoyage). Lu dans la copie gelée du
    13/10/2026, jamais dans l'API, qui change chaque jour.
    """
    contenu = stockage.copie_controlee(
        _copies_publiques(config.CHEMIN_RAW_ANNUAIRE),
        config.CHEMIN_RAW_ANNUAIRE,
        config.SHA256_ANNUAIRE,
    )
    annuaire = gpd.read_parquet(io.BytesIO(contenu))

    # L'annuaire écrit les départements sur trois caractères : de "001" à "095", "02A" et "02B"
    # en métropole, à partir de "971" outre-mer
    metropole = annuaire["code_departement"].str.startswith("0")
    # Le type "Lycée" isole la partie lycée d'une cité scolaire, dont la partie collège
    # (type "Collège") porte le même UAI
    est_lycee = annuaire["type_etablissement"] == "Lycée"
    nature_retenue = annuaire["code_nature"].isin(config.NATURES_LYCEES)
    # `lycee_agricole` est parfois vide : on exclut aussi sur la tutelle
    pas_agricole = (annuaire["ministere_tutelle"] != "AGRICULTURE") & (
        annuaire["lycee_agricole"] != "1"
    )
    candidats = metropole & est_lycee & nature_retenue & pas_agricole

    # Un statut vide fait échouer les deux comparaisons plus bas : sans ce contrôle, le
    # lycée serait écarté sans bruit. Seuls les cas connus de `config` sont écartés
    statut_vide = candidats & annuaire["statut_public_prive"].isna()
    uai_sans_statut = sorted(annuaire.loc[statut_vide, "identifiant_de_l_etablissement"])
    assert uai_sans_statut == sorted(config.UAI_SANS_STATUT), (
        f"Lycées sans statut public ou privé : {uai_sans_statut}, attendus : "
        f"{sorted(config.UAI_SANS_STATUT)} (config.UAI_SANS_STATUT)."
    )

    est_public = annuaire["statut_public_prive"] == "Public"
    est_prive = annuaire["statut_public_prive"] == "Privé"
    contrat_retenu = annuaire["code_type_contrat_prive"].isin(config.CONTRATS_PRIVE_RETENUS)
    lycees = annuaire[candidats & (est_public | (est_prive & contrat_retenu))]
    return lycees.reset_index(drop=True)


def aav_2020() -> pd.DataFrame:
    """Renvoie la composition communale du zonage en aires d'attraction des villes 2020.

    Une ligne par commune du COG 2025, avec `AAV2020` (code de l'aire, "000" hors aire) et
    `CATEAAV2020` (commune-centre, pôle ou couronne). Tout est lu en chaîne : "013" perdrait son
    zéro en entier. Lyon, Marseille et Paris n'y figurent que par leur commune parente, pas par
    leurs arrondissements. Le zip de l'Insee est permanent : il est lu à son URL d'origine.
    """
    contenu = stockage.copie_controlee([config.URL_AAV], config.CHEMIN_RAW_AAV, config.SHA256_AAV)
    with zipfile.ZipFile(io.BytesIO(contenu)) as archive:
        classeur = io.BytesIO(archive.read(config.XLSX_AAV))
    aav = pd.read_excel(
        classeur,
        sheet_name=config.FEUILLE_AAV,
        header=config.ENTETE_AAV,
        dtype=str,
        engine="calamine",
    )

    assert len(aav) == config.NB_COMMUNES_AAV, (
        f"{len(aav)} communes dans l'AAV, {config.NB_COMMUNES_AAV} attendues (COG 2025)."
    )
    assert aav["CODGEO"].is_unique, "Des codes communes sont en double dans l'AAV."
    categories_inconnues = set(aav["CATEAAV2020"]) - set(config.CATEGORIES_AAV)
    assert not categories_inconnues, f"Catégories AAV inconnues : {sorted(categories_inconnues)}"
    return aav


def serie_historique_rp2022() -> pd.DataFrame:
    """Renvoie la population et la superficie du recensement 2022, par commune ou arrondissement.

    Colonnes `CODGEO`, `P22_POP` et `SUPERF` (km²), en COG 2025. Les arrondissements de Lyon,
    Marseille et Paris y figurent avec leur commune parente : sommer tout le fichier compterait
    ces villes deux fois. Le zip de l'Insee est permanent : il est lu à son URL d'origine.
    """
    contenu = stockage.copie_controlee(
        [config.URL_SERIE_RP2022], config.CHEMIN_RAW_SERIE_RP2022, config.SHA256_SERIE_RP2022
    )
    with zipfile.ZipFile(io.BytesIO(contenu)) as archive:
        csv = io.BytesIO(archive.read(config.CSV_SERIE_RP2022))
    # Lu en nombre, "01001" deviendrait 1001 ; une colonne disparue fait échouer la lecture
    serie = pd.read_csv(
        csv, sep=";", usecols=["CODGEO", "P22_POP", "SUPERF"], dtype={"CODGEO": str}
    )

    assert len(serie) == config.NB_LIGNES_SERIE_RP2022, (
        f"{len(serie)} lignes dans la série historique, {config.NB_LIGNES_SERIE_RP2022} attendues."
    )
    assert serie["CODGEO"].is_unique, "Des codes communes sont en double dans la série historique."
    return serie


def ival_lycees() -> pd.DataFrame:
    """Renvoie les indicateurs de valeur ajoutée des lycées GT : une ligne par lycée et session.

    Lu dans la copie gelée du 20/10/2026 de l'export de l'API (`config.URL_IVAL`). Tout est lu en
    chaîne, pour garder les codes communes tels quels (« 2A004 », zéros
    en tête) : la conversion des valeurs se fait au nettoyage.
    """
    contenu = stockage.copie_controlee(
        _copies_publiques(config.CHEMIN_RAW_IVAL), config.CHEMIN_RAW_IVAL, config.SHA256_IVAL
    )
    ival = pd.read_csv(io.BytesIO(contenu), sep=";", encoding="utf-8-sig", dtype=str)

    assert len(ival) == config.NB_LIGNES_IVAL, (
        f"{len(ival)} lignes dans l'IVAL, {config.NB_LIGNES_IVAL} attendues."
    )
    assert not ival.duplicated(["uai", "annee"]).any(), "Lycée en double dans l'IVAL."
    return ival


def geler_contours(chemin: str, valeur: str, maille: str, filtre: str) -> str:
    """Écrit à `chemin` des contours téléchargés par cartiflette et renvoie leur sha256.

    `valeur`, `maille` et `filtre` sont les arguments `values`, `borders` et `filter_by` de
    `carti_download` : un code d'aire, "COMMUNE_ARRONDISSEMENT" et "AIRE_ATTRACTION_VILLES" pour
    les contours d'une aire ; "France", "DEPARTEMENT" et "FRANCE_ENTIERE" pour les départements ;
    un code d'aire, "IRIS" et "AIRE_ATTRACTION_VILLES" pour les IRIS d'une aire (carte A18).
    Produit une copie gelée : celles des 13, 20 et 21/10/2026 viennent de là. Le rapport ne
    l'appelle pas, il lit la copie gelée. Le sha256 fige une sérialisation (versions de geopandas
    et de pyarrow comprises), pas seulement des données. Mode d'emploi dans le README.
    """
    assert not stockage.existe(chemin), f"{chemin} existe déjà : choisir un autre chemin daté."
    contours = carti_download(
        values=valeur,
        borders=maille,
        filter_by=filtre,
        year=config.ANNEE_COG,
        simplification=config.SIMPLIFICATION_CONTOURS,
    )
    stockage.ecrire_parquet(contours, chemin)
    return hashlib.sha256(stockage.lire_octets(chemin)).hexdigest()


def contours_aire(code_aav: str) -> gpd.GeoDataFrame:
    """Renvoie les contours des communes d'une aire d'attraction, en WGS84 (COG 2025).

    Les arrondissements municipaux remplacent leur commune parente (Lyon 69123 devient 69381 à
    69389) ; `INSEE_COM` garde le code de la commune parente et `INSEE_COG` celui de l'unité. Lu
    dans la copie gelée du 13/10/2026.
    """
    chemin = config.CHEMIN_RAW_CONTOURS.format(aav=code_aav)
    contenu = stockage.copie_controlee(
        _copies_publiques(chemin), chemin, config.SHA256_CONTOURS[code_aav]
    )
    return gpd.read_parquet(io.BytesIO(contenu))


def contours_iris(code_aav: str) -> gpd.GeoDataFrame:
    """Renvoie les contours des IRIS d'une aire d'attraction, en WGS84 (COG 2025).

    `CODE_IRIS` identifie l'IRIS ; à Lyon, `INSEE_COM` vaut 69123 et `INSEE_COG` l'arrondissement.
    Lu dans la copie gelée du 21/10/2026.
    """
    chemin = config.CHEMIN_RAW_CONTOURS_IRIS.format(aav=code_aav)
    contenu = stockage.copie_controlee(
        _copies_publiques(chemin), chemin, config.SHA256_CONTOURS_IRIS[code_aav]
    )
    return gpd.read_parquet(io.BytesIO(contenu))


def activite_iris_2022() -> pd.DataFrame:
    """Renvoie les actifs de 15 à 64 ans par groupe socioprofessionnel et par IRIS, en 2022.

    Colonnes `IRIS`, `COM` et celles de `config.ACTIFS_1564_IRIS_2022`, en IRIS et COG 2024.
    Effectifs décimaux (exploitation complémentaire). À Lyon, `COM` donne l'arrondissement.
    """
    contenu = stockage.copie_controlee(
        [config.URL_ACTIVITE_IRIS_2022],
        config.CHEMIN_RAW_ACTIVITE_IRIS_2022,
        config.SHA256_ACTIVITE_IRIS_2022,
    )
    with zipfile.ZipFile(io.BytesIO(contenu)) as archive:
        csv = io.BytesIO(archive.read(config.CSV_ACTIVITE_IRIS_2022))
    colonnes = ["IRIS", "COM", *config.ACTIFS_1564_IRIS_2022]
    # Lus en nombre, les codes perdraient leur zéro initial
    activite = pd.read_csv(csv, sep=";", usecols=colonnes, dtype={"IRIS": str, "COM": str})
    assert len(activite) == config.NB_LIGNES_ACTIVITE_IRIS_2022, (
        f"{len(activite)} IRIS en 2022, {config.NB_LIGNES_ACTIVITE_IRIS_2022} attendus."
    )
    assert activite["IRIS"].is_unique, "Codes IRIS en double en 2022."
    return activite


def activite_iris_2011() -> pd.DataFrame:
    """Renvoie les actifs de 15 à 64 ans par groupe socioprofessionnel et par IRIS, en 2011.

    Colonnes `IRIS` et celles de `config.ACTIFS_1564_IRIS_2011`, en géographie 2013. Le fichier
    n'existe qu'en xls : il est lu avec calamine, tout en texte pour garder les zéros initiaux des
    codes, puis les effectifs sont convertis en nombres.
    """
    contenu = stockage.copie_controlee(
        [config.URL_ACTIVITE_IRIS_2011],
        config.CHEMIN_RAW_ACTIVITE_IRIS_2011,
        config.SHA256_ACTIVITE_IRIS_2011,
    )
    with zipfile.ZipFile(io.BytesIO(contenu)) as archive:
        xls = io.BytesIO(archive.read(config.XLS_ACTIVITE_IRIS_2011))
    feuille = pd.read_excel(
        xls,
        sheet_name=config.FEUILLE_ACTIVITE_IRIS_2011,
        header=config.ENTETE_ACTIVITE_IRIS_2011,
        dtype=str,
        engine="calamine",
    )
    activite = feuille[["IRIS", *config.ACTIFS_1564_IRIS_2011]].copy()
    groupes = list(config.ACTIFS_1564_IRIS_2011)
    # Une valeur non numérique fait échouer la conversion
    activite[groupes] = activite[groupes].astype(float)
    assert len(activite) == config.NB_LIGNES_ACTIVITE_IRIS_2011, (
        f"{len(activite)} IRIS en 2011, {config.NB_LIGNES_ACTIVITE_IRIS_2011} attendus."
    )
    assert activite["IRIS"].is_unique, "Codes IRIS en double en 2011."
    return activite


def passage_communes() -> pd.DataFrame:
    """Renvoie la table de passage annuelle des codes communes 2025 : une ligne par filiation.

    Colonnes `CODGEO_2013` et `CODGEO_2024` (une case vide : la commune n'existait pas). Une
    commune peut avoir plusieurs lignes : réduire aux paires uniques avant de compter.
    """
    contenu = stockage.copie_controlee(
        [config.URL_PASSAGE_COG], config.CHEMIN_RAW_PASSAGE_COG, config.SHA256_PASSAGE_COG
    )
    with zipfile.ZipFile(io.BytesIO(contenu)) as archive:
        xlsx = io.BytesIO(archive.read(config.XLSX_PASSAGE_COG))
    table = pd.read_excel(
        xlsx,
        sheet_name=config.FEUILLE_PASSAGE_COG,
        header=config.ENTETE_PASSAGE_COG,
        dtype=str,
        engine="calamine",
    )
    assert len(table) == config.NB_LIGNES_PASSAGE_COG, (
        f"{len(table)} lignes dans la table de passage, {config.NB_LIGNES_PASSAGE_COG} attendues."
    )
    return table[["CODGEO_2013", "CODGEO_2024"]]


def contours_departements() -> gpd.GeoDataFrame:
    """Renvoie les contours des départements, DOM compris, en WGS84 (COG 2025).

    Leur union donne le contour de la France métropolitaine (`geo.distance_contour_national_km`).
    Lu dans la copie gelée du 20/10/2026.
    """
    contenu = stockage.copie_controlee(
        _copies_publiques(config.CHEMIN_RAW_DEPARTEMENTS),
        config.CHEMIN_RAW_DEPARTEMENTS,
        config.SHA256_DEPARTEMENTS,
    )
    return gpd.read_parquet(io.BytesIO(contenu))


def ips_lycees() -> pd.DataFrame:
    """Renvoie l'IPS des lycées : une ligne par lycée et par rentrée, de 2023-2024 à 2025-2026.

    Lu dans la copie gelée du 13/10/2026 de l'export de l'API (`config.URL_IPS`). Tout est lu en
    chaîne, la conversion en nombres se fait au nettoyage.
    """
    contenu = stockage.copie_controlee(
        _copies_publiques(config.CHEMIN_RAW_IPS), config.CHEMIN_RAW_IPS, config.SHA256_IPS
    )
    ips = pd.read_csv(io.BytesIO(contenu), sep=";", encoding="utf-8-sig", dtype=str)

    assert len(ips) == config.NB_LIGNES_IPS, (
        f"{len(ips)} lignes dans l'IPS, {config.NB_LIGNES_IPS} attendues."
    )
    assert not ips.duplicated(["uai", "rentree_scolaire"]).any(), "Lycée en double dans l'IPS."
    return ips
