"""Nettoyage et jointures des sources : les lycées avec leur aire et leur IPS."""

import geopandas as gpd
import pandas as pd

from cadres_lycees import config


def lycees_geo(
    annuaire: gpd.GeoDataFrame, ips: pd.DataFrame, referentiel: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Renvoie les lycées des communes du référentiel, avec leur aire, leur secteur et leur IPS.

    Un lycée est rattaché à une aire par le code de sa commune dans l'annuaire, qui nomme les
    arrondissements de Lyon (693xx) comme le référentiel. Les lycées hors des aires sont écartés.
    L'IPS est celui de la rentrée et de la mesure choisies dans `config` ; il reste manquant pour
    un lycée sans IPS, une valeur manquante ne se remplace pas. Un UAI multi-sites compte pour un
    lycée.
    """
    # Un UAI multi-sites occupe plusieurs lignes, avec la même commune et les mêmes coordonnées
    nb_communes = annuaire.groupby("identifiant_de_l_etablissement")["code_commune"].nunique()
    assert (nb_communes == 1).all(), "Un UAI a plusieurs communes dans l'annuaire."
    lycees = annuaire.drop_duplicates("identifiant_de_l_etablissement")
    # L'annuaire nomme `position` sa colonne de coordonnées, le reste du code attend `geometry`
    lycees = lycees.rename_geometry("geometry").rename(
        columns={"identifiant_de_l_etablissement": "uai"}
    )

    lycees["secteur"] = lycees["statut_public_prive"].map(config.SECTEURS)
    lycees = lycees[["uai", "code_commune", "secteur", "geometry"]].to_crs(config.CRS_CALCUL)

    geolocalise = ~(lycees.geometry.isna() | lycees.geometry.is_empty)
    assert geolocalise.mean() > 0.98, "Plus de 2 % des lycées n'ont pas de coordonnées."

    # L'aire vient du code commune. On vérifie que la position dit la même chose : une commune
    # fusionnée sous un nouveau code ferait disparaître son lycée de la jointure sans bruit
    zone = referentiel.geometry.union_all()
    commune_connue = lycees["code_commune"].isin(referentiel["code_commune"])
    dans_une_aire = lycees.geometry.within(zone)
    desaccord = geolocalise & (commune_connue != dans_une_aire)
    assert not desaccord.any(), (
        f"Code commune et position en désaccord pour {lycees.loc[desaccord, 'uai'].tolist()}."
    )
    lycees = lycees.merge(referentiel[["code_commune", "aire"]], on="code_commune", how="inner")
    assert set(lycees["aire"]) == set(referentiel["aire"]), "Une aire n'a aucun lycée."
    # Les 2 % tolérés plus haut portent sur tous les lycées demandés : un lycée d'une aire sans
    # coordonnées resterait sans position et fausserait les distances
    sans_position = lycees["geometry"].isna() | lycees["geometry"].is_empty
    assert not sans_position.any(), (
        f"Lycées d'une aire sans coordonnées : {lycees.loc[sans_position, 'uai'].tolist()}."
    )

    ips_rentree = ips[
        (ips["rentree_scolaire"] == config.RENTREE_IPS)
        & ips["type_de_lycee"].isin(config.TYPES_LYCEES_IPS)
    ].copy()
    assert not ips_rentree.empty, f"Pas d'IPS pour la rentrée {config.RENTREE_IPS}."
    ips_rentree["ips"] = pd.to_numeric(ips_rentree[config.COLONNE_IPS])
    ips_rentree["secteur_ips"] = ips_rentree["secteur"].map(config.SECTEURS_IPS)

    # Des lycées de l'IPS situés dans les aires manquent à notre liste, car l'annuaire les filtre
    # ou les regroupe sous un autre UAI : on exige que la liste soit celle de `config`
    ips_des_aires = ips_rentree[
        ips_rentree["code_insee_de_la_commune"].isin(referentiel["code_commune"])
        & ips_rentree["ips"].notna()
    ]
    non_retenus = sorted(set(ips_des_aires["uai"]) - set(lycees["uai"]))
    assert non_retenus == sorted(config.UAI_IPS_NON_RETENUS), (
        f"Lycées de l'IPS absents de la liste : {non_retenus}, attendus : "
        f"{sorted(config.UAI_IPS_NON_RETENUS)} (config.UAI_IPS_NON_RETENUS)."
    )

    nb_lycees = len(lycees)
    lycees = lycees.merge(ips_rentree[["uai", "ips", "secteur_ips"]], on="uai", how="left")
    assert len(lycees) == nb_lycees, "La jointure avec l'IPS a changé le nombre de lycées."
    # Un secteur différent d'une source à l'autre attribuerait l'IPS au mauvais secteur
    secteur_different = lycees["secteur_ips"].notna() & (lycees["secteur"] != lycees["secteur_ips"])
    uai_differents = lycees.loc[secteur_different, "uai"].tolist()
    assert not uai_differents, f"Secteur différent dans l'annuaire et l'IPS : {uai_differents}."
    return lycees.drop(columns="secteur_ips")
