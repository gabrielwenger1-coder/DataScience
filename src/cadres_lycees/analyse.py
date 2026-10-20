"""Statistiques descriptives et comparaisons sur la base communale et les lycées."""

import geopandas as gpd
import pandas as pd


def profil_aires(lycees: gpd.GeoDataFrame) -> pd.DataFrame:
    """Renvoie une ligne par aire : lycées, part de privé sous contrat et IPS moyen par secteur.

    L'IPS moyen est une moyenne simple des lycées qui ont un IPS, car la source ne donne pas
    d'effectifs. `ecart_ips` est l'IPS moyen du privé moins celui du public, en points d'IPS ;
    `n_ips_public` et `n_ips_prive` sont les nombres de lycées sur lesquels reposent ces moyennes.
    Seuls les lycées situés dans les communes de l'aire comptent.
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

    ips = lycees.groupby(["aire", "secteur"])["ips"].agg(["mean", "count"]).unstack("secteur")
    profil["ips_public"] = ips[("mean", "public")]
    profil["ips_prive"] = ips[("mean", "prive")]
    profil["ecart_ips"] = profil["ips_prive"] - profil["ips_public"]
    profil["n_ips_public"] = ips[("count", "public")]
    profil["n_ips_prive"] = ips[("count", "prive")]

    manquants = profil[["n_prive", "ips_public", "ips_prive"]].isna().any(axis=1)
    assert not manquants.any(), (
        f"Pas de lycée privé ou d'IPS dans un secteur pour {profil.index[manquants].tolist()}."
    )
    return profil
