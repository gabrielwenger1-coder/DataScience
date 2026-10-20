"""Statistiques descriptives et comparaisons sur la base communale et les lycées."""

import geopandas as gpd
import pandas as pd

from cadres_lycees import accessibilite, config, nettoyage


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


def fiabilite_ival(
    base: gpd.GeoDataFrame, lycees: gpd.GeoDataFrame, sessions_ival: pd.DataFrame
) -> pd.DataFrame:
    """Renvoie la fiabilité de `ival_moy_5km` (PLAN §3.2, A7), toutes aires ensemble puis par aire.

    `base` et `lycees` viennent de `pipeline.construire_base`, sur les 3 aires retenues. Pour
    chaque moitié de `config.MOITIES_IVAL`, `ival_moy_5km` est recalculée avec les lycées de la
    règle A1 qui ont assez de sessions dans les deux moitiés, et leurs poids A1. Colonnes : `r`
    (Pearson, après centrage par aire), `r_spearman_brown` (manquante si `r` est négatif),
    `n_communes_h3` (population de H3), `n_communes` (renseignées dans les deux moitiés) et
    `n_lycees` (lycées distincts à 5 km de ces communes). Seule la ligne « ensemble » tranche H3.
    """
    rayon = config.RAYON_PRINCIPAL_KM
    communes = base.set_index("code_commune")
    moities = [f"moitie_{rang}" for rang in range(1, len(config.MOITIES_IVAL) + 1)]

    retenus = lycees[lycees["ival"].notna()].copy()
    for moitie, (premiere, derniere) in zip(moities, config.MOITIES_IVAL, strict=True):
        ival = nettoyage.ival_par_lycee(
            sessions_ival, premiere, derniere, config.NB_SESSIONS_MIN_MOITIE
        )
        retenus[moitie] = retenus["uai"].map(ival["ival"])
    retenus = retenus.dropna(subset=moities)

    population_h3 = communes[communes[f"n_lyc_{rayon}km"] > 0]
    par_commune = population_h3[["aire"]].copy()
    for moitie in moities:
        acces = accessibilite.indicateurs(
            base, retenus, "lyc", rayons=(rayon,), attribut=moitie, poids="poids_ival"
        )
        par_commune[moitie] = acces[f"{moitie}_moy_{rayon}km"]
    # Une commune sort si aucun de ses lycées à 5 km n'a assez de sessions dans chaque moitié :
    # elle reste comptée dans `n_communes_h3`, pour que la perte se voie
    renseignees = par_commune.dropna(subset=moities)

    # Centrage par aire : H3 se lit dans chaque aire, les écarts entre aires ne doivent pas faire
    # la corrélation
    centrees = renseignees[moities] - renseignees.groupby("aire")[moities].transform("mean")
    centrees["aire"] = renseignees["aire"]
    # `indicateurs` ne dit pas quels lycées entrent dans chaque rayon : on refait la jointure
    # pour compter les lycées distincts
    centroides = communes.set_geometry("centroide")[["centroide"]]
    proches = gpd.sjoin(
        centroides.loc[centrees.index],
        retenus[["uai", "geometry"]],
        predicate="dwithin",
        distance=rayon * 1000,
    )

    groupes = {"ensemble": centrees}
    for aire, groupe in centrees.groupby("aire"):
        groupes[aire] = groupe
    lignes = {}
    for nom, groupe in groupes.items():
        assert len(groupe) >= 3, f"Trop peu de communes pour une corrélation ({nom})."
        r = groupe[moities[0]].corr(groupe[moities[1]])
        h3 = population_h3 if nom == "ensemble" else population_h3[population_h3["aire"] == nom]
        lignes[nom] = {
            "r": r,
            # La formule suppose une fiabilité positive : pour r < 0, elle n'a pas de sens
            "r_spearman_brown": 2 * r / (1 + r) if r >= 0 else float("nan"),
            "n_communes_h3": len(h3),
            "n_communes": len(groupe),
            "n_lycees": proches.loc[groupe.index, "uai"].nunique(),
        }
    return pd.DataFrame.from_dict(lignes, orient="index")
