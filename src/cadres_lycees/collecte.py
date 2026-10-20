"""Téléchargement des sources de données, avec une copie brute dans raw/ (idempotent)."""

import hashlib
import io
import zipfile

import geopandas as gpd
import pandas as pd
import requests
from cartiflette import carti_download

from cadres_lycees import config, stockage


def annuaire_education() -> gpd.GeoDataFrame:
    """Renvoie les lycées de France métropolitaine de l'annuaire de l'éducation.

    Lycées généraux, technologiques et polyvalents, publics ou privés sous contrat (PLAN §2.4),
    repérés par `code_nature` car les `voie_*` de l'annuaire sont trop souvent vides. Toute la
    métropole est gardée, pas seulement les aires et une marge autour : le lycée le plus proche
    d'une commune du bord peut être bien au-delà de l'aire. Une ligne par site : un UAI
    multi-sites apparaît plusieurs fois (dédoublonné au nettoyage).
    """
    if not stockage.existe(config.CHEMIN_RAW_ANNUAIRE):
        # Copie brute de l'export complet : l'annuaire change chaque jour, et les variantes de
        # robustesse (PLAN §5.6) refont le filtre sans retélécharger
        reponse = requests.get(config.URL_ANNUAIRE, timeout=config.DELAI_TELECHARGEMENT_S)
        reponse.raise_for_status()
        # Une réponse 200 tronquée resterait dans raw/ et existe() ne la retélécharge plus.
        # "PAR1" ouvre et ferme tout fichier Parquet.
        assert reponse.content.startswith(b"PAR1") and reponse.content.endswith(b"PAR1"), (
            "L'export de l'annuaire n'est pas un fichier Parquet complet : rien n'a été enregistré."
        )
        stockage.ecrire_octets(reponse.content, config.CHEMIN_RAW_ANNUAIRE)
    annuaire = stockage.lire_parquet(config.CHEMIN_RAW_ANNUAIRE)

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
    leurs arrondissements.
    """
    if not stockage.existe(config.CHEMIN_RAW_AAV):
        reponse = requests.get(config.URL_AAV, timeout=config.DELAI_TELECHARGEMENT_S)
        reponse.raise_for_status()
        # Contrôle avant d'écrire : une copie abîmée resterait dans raw/ et existe() ne la
        # retélécharge plus
        sha256 = hashlib.sha256(reponse.content).hexdigest()
        assert sha256 == config.SHA256_AAV, (
            f"Le zip de l'AAV a le sha256 {sha256}, {config.SHA256_AAV} attendu : "
            "rien n'a été enregistré."
        )
        stockage.ecrire_octets(reponse.content, config.CHEMIN_RAW_AAV)

    with zipfile.ZipFile(io.BytesIO(stockage.lire_octets(config.CHEMIN_RAW_AAV))) as archive:
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
    ces villes deux fois.
    """
    if not stockage.existe(config.CHEMIN_RAW_SERIE_RP2022):
        reponse = requests.get(config.URL_SERIE_RP2022, timeout=config.DELAI_TELECHARGEMENT_S)
        reponse.raise_for_status()
        # Contrôle avant d'écrire : un téléchargement tronqué sans erreur a déjà été vu sur un zip
        # de l'Insee, et existe() ne le retéléchargerait plus
        sha256 = hashlib.sha256(reponse.content).hexdigest()
        assert sha256 == config.SHA256_SERIE_RP2022, (
            f"Le zip de la série historique a le sha256 {sha256}, "
            f"{config.SHA256_SERIE_RP2022} attendu : rien n'a été enregistré."
        )
        stockage.ecrire_octets(reponse.content, config.CHEMIN_RAW_SERIE_RP2022)

    contenu = stockage.lire_octets(config.CHEMIN_RAW_SERIE_RP2022)
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

    Copie du 20/10/2026, contrôlée par sha256 comme l'IPS : le code échoue si la source a
    changé depuis, au lieu de lire des données différentes. Tout est lu en chaîne, pour garder
    les codes communes tels quels (« 2A004 », zéros en tête) : la conversion des valeurs se fait
    au nettoyage.
    """
    if not stockage.existe(config.CHEMIN_RAW_IVAL):
        reponse = requests.get(config.URL_IVAL, timeout=config.DELAI_TELECHARGEMENT_S)
        reponse.raise_for_status()
        sha256 = hashlib.sha256(reponse.content).hexdigest()
        assert sha256 == config.SHA256_IVAL, (
            f"L'export de l'IVAL a le sha256 {sha256}, {config.SHA256_IVAL} attendu : la source "
            "a changé depuis le 20/10/2026, rien n'a été enregistré."
        )
        stockage.ecrire_octets(reponse.content, config.CHEMIN_RAW_IVAL)

    csv = io.BytesIO(stockage.lire_octets(config.CHEMIN_RAW_IVAL))
    ival = pd.read_csv(csv, sep=";", encoding="utf-8-sig", dtype=str)

    assert len(ival) == config.NB_LIGNES_IVAL, (
        f"{len(ival)} lignes dans l'IVAL, {config.NB_LIGNES_IVAL} attendues."
    )
    assert not ival.duplicated(["uai", "annee"]).any(), "Lycée en double dans l'IVAL."
    return ival


def contours_aire(code_aav: str) -> gpd.GeoDataFrame:
    """Renvoie les contours des communes d'une aire d'attraction, en WGS84 (COG 2025).

    Les arrondissements municipaux remplacent leur commune parente (Lyon 69123 devient 69381 à
    69389) ; `INSEE_COM` garde le code de la commune parente et `INSEE_COG` celui de l'unité.
    """
    chemin = config.CHEMIN_RAW_CONTOURS.format(aav=code_aav)
    if not stockage.existe(chemin):
        contours = carti_download(
            values=code_aav,
            borders="COMMUNE_ARRONDISSEMENT",
            filter_by="AIRE_ATTRACTION_VILLES",
            year=config.ANNEE_COG,
            simplification=config.SIMPLIFICATION_CONTOURS,
        )
        stockage.ecrire_parquet(contours, chemin)
    return stockage.lire_parquet(chemin)


def ips_lycees() -> pd.DataFrame:
    """Renvoie l'IPS des lycées : une ligne par lycée et par rentrée, de 2023-2024 à 2025-2026.

    Copie du 13/10/2026 : comme pour l'AAV, le sha256 est contrôlé avant l'écriture dans raw/, et
    le code échoue si la source a changé depuis au lieu de lire des données différentes.
    Tout est lu en chaîne, la conversion en nombres se fait au nettoyage.
    """
    if not stockage.existe(config.CHEMIN_RAW_IPS):
        reponse = requests.get(config.URL_IPS, timeout=config.DELAI_TELECHARGEMENT_S)
        reponse.raise_for_status()
        sha256 = hashlib.sha256(reponse.content).hexdigest()
        assert sha256 == config.SHA256_IPS, (
            f"L'export de l'IPS a le sha256 {sha256}, {config.SHA256_IPS} attendu : la source a "
            "changé depuis le 13/10/2026, rien n'a été enregistré."
        )
        stockage.ecrire_octets(reponse.content, config.CHEMIN_RAW_IPS)

    csv = io.BytesIO(stockage.lire_octets(config.CHEMIN_RAW_IPS))
    # Séparateur ";" et BOM UTF-8 en tête du fichier
    ips = pd.read_csv(csv, sep=";", encoding="utf-8-sig", dtype=str)

    assert len(ips) == config.NB_LIGNES_IPS, (
        f"{len(ips)} lignes dans l'IPS, {config.NB_LIGNES_IPS} attendues."
    )
    assert not ips.duplicated(["uai", "rentree_scolaire"]).any(), "Lycée en double dans l'IPS."
    return ips
