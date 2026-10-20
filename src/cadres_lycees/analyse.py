"""Statistiques descriptives et comparaisons sur la base communale et les lycées."""

import geopandas as gpd
import pandas as pd


def profil_aires(lycees: gpd.GeoDataFrame) -> pd.DataFrame:
    """Renvoie une ligne par aire : lycées, part de privé sous contrat et IPS moyen par secteur.

    `part_prive` compte les lycées ; `part_prive_candidats` pondère chaque lycée par ses candidats
    au bac (`poids_ival`, moyenne des présents au bac général et technologique 2012-2022), sur
    les `n_avec_candidats` lycées qui ont une IVAL : plus proche d'une part d'élèves, sans en être
    une au sens de la DEPP. L'IPS moyen est une moyenne simple des lycées qui ont un IPS, car la
    source ne donne pas d'effectifs. `ecart_ips` est l'IPS moyen du privé moins celui du public,
    en points d'IPS ; `n_ips_public` et `n_ips_prive` sont les nombres de lycées sur lesquels
    reposent ces moyennes. Seuls les lycées situés dans les communes de l'aire comptent ; une
    aire sans lycée privé, sans IPS dans un secteur ou sans IVAL dans un secteur fait échouer.
    """
    lycees = lycees[lycees["aire"].notna()]
    prives = lycees[lycees["secteur"] == "prive"]
    profil = pd.DataFrame(
        {
            "n_lycees": lycees.groupby("aire").size(),
            "n_prive": prives.groupby("aire").size(),
        }
    )
    profil["part_prive"] = profil["n_prive"] / profil["n_lycees"]

    avec_candidats = lycees[lycees["poids_ival"].notna()]
    par_secteur = avec_candidats.groupby(["aire", "secteur"])["poids_ival"].sum()
    candidats_par_secteur = par_secteur.unstack("secteur")
    profil["part_prive_candidats"] = candidats_par_secteur["prive"] / (
        candidats_par_secteur["prive"] + candidats_par_secteur["public"]
    )
    profil["n_avec_candidats"] = avec_candidats.groupby("aire").size()

    ips = lycees.groupby(["aire", "secteur"])["ips"].agg(["mean", "count"]).unstack("secteur")
    profil["ips_public"] = ips[("mean", "public")]
    profil["ips_prive"] = ips[("mean", "prive")]
    profil["ecart_ips"] = profil["ips_prive"] - profil["ips_public"]
    profil["n_ips_public"] = ips[("count", "public")]
    profil["n_ips_prive"] = ips[("count", "prive")]

    colonnes = ["n_prive", "part_prive_candidats", "ips_public", "ips_prive"]
    manquants = profil[colonnes].isna().any(axis=1)
    assert not manquants.any(), (
        f"Pas de lycée privé, d'IVAL ou d'IPS dans un secteur : {profil.index[manquants].tolist()}."
    )
    return profil
