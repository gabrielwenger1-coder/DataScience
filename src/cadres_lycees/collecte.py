"""Téléchargement des sources de données, avec une copie brute dans raw/ (idempotent)."""

import hashlib
import io
import zipfile

import geopandas as gpd
import pandas as pd
import requests
from cartiflette import carti_download

from cadres_lycees import config, stockage


def annuaire_education(departements: list[str]) -> gpd.GeoDataFrame:
    """Renvoie les lycées de l'annuaire de l'éducation dans les départements demandés.

    Lycées généraux, technologiques et polyvalents, publics ou privés sous contrat (PLAN §2.4),
    repérés par `code_nature` car les `voie_*` de l'annuaire sont trop souvent vides. Une ligne
    par site : un UAI multi-sites apparaît plusieurs fois (dédoublonné au nettoyage).
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

    # L'annuaire écrit les départements sur trois caractères ("035", "02A")
    codes = [departement.zfill(3) for departement in departements]
    # Le type "Lycée" isole la partie lycée d'une cité scolaire, dont la partie collège
    # (type "Collège") porte le même UAI
    est_lycee = annuaire["type_etablissement"] == "Lycée"
    nature_retenue = annuaire["code_nature"].isin(config.NATURES_LYCEES)
    # `lycee_agricole` est parfois vide : on exclut aussi sur la tutelle
    pas_agricole = (annuaire["ministere_tutelle"] != "AGRICULTURE") & (
        annuaire["lycee_agricole"] != "1"
    )
    dans_les_departements = annuaire["code_departement"].isin(codes)
    candidats = est_lycee & nature_retenue & pas_agricole & dans_les_departements

    # Un statut vide fait échouer les deux comparaisons plus bas : sans ce contrôle, le
    # lycée serait écarté sans bruit
    statut_vide = candidats & annuaire["statut_public_prive"].isna()
    uai_sans_statut = annuaire.loc[statut_vide, "identifiant_de_l_etablissement"].tolist()
    assert not uai_sans_statut, f"Lycées sans statut public ou privé : {uai_sans_statut}"

    est_public = annuaire["statut_public_prive"] == "Public"
    est_prive = annuaire["statut_public_prive"] == "Privé"
    contrat_retenu = annuaire["code_type_contrat_prive"].isin(config.CONTRATS_PRIVE_RETENUS)
    lycees = annuaire[candidats & (est_public | (est_prive & contrat_retenu))]

    sans_lycee = set(codes) - set(lycees["code_departement"])
    assert not sans_lycee, f"Aucun lycée trouvé dans les départements {sorted(sans_lycee)}"
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
