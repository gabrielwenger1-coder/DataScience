"""Téléchargement des sources de données, avec une copie brute dans raw/ (idempotent)."""

import geopandas as gpd
import requests

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
