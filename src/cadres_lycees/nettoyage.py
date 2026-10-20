"""Nettoyage et jointures des sources : les lycées avec leur aire et leur IPS."""

import geopandas as gpd
import pandas as pd

from cadres_lycees import config


def lycees_geo(
    annuaire: gpd.GeoDataFrame, ips: pd.DataFrame, referentiel: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Renvoie les lycées de l'annuaire avec leur aire, leur secteur et leur IPS.

    Un lycée est rattaché à une aire par le code de sa commune dans l'annuaire, qui nomme les
    arrondissements de Lyon (693xx) comme le référentiel. `aire` est manquante pour un lycée
    situé hors des aires : il compte quand même dans l'accessibilité des communes proches.
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
        columns={"identifiant_de_l_etablissement": "uai", "nom_etablissement": "nom_lycee"}
    )

    lycees["secteur"] = lycees["statut_public_prive"].map(config.SECTEURS)
    colonnes = ["uai", "nom_lycee", "code_commune", "secteur", "geometry"]
    lycees = lycees[colonnes].to_crs(config.CRS_CALCUL)

    # Tous les lycées servent aux distances : un lycée sans position les fausserait sans bruit
    sans_position = lycees.geometry.isna() | lycees.geometry.is_empty
    assert not sans_position.any(), (
        f"Lycées sans coordonnées : {lycees.loc[sans_position, 'uai'].tolist()}."
    )

    # L'aire vient du code commune. On vérifie que la position dit la même chose (code dans le
    # référentiel si et seulement si position dans une aire) : une commune fusionnée sous un
    # nouveau code laisserait sinon son lycée sans aire, sans bruit. La position des lycées hors
    # des aires n'est pas contrôlée
    zone = referentiel.geometry.union_all()
    commune_connue = lycees["code_commune"].isin(referentiel["code_commune"])
    dans_une_aire = lycees.geometry.within(zone)
    desaccord = commune_connue != dans_une_aire
    assert not desaccord.any(), (
        f"Code commune et position en désaccord pour {lycees.loc[desaccord, 'uai'].tolist()}."
    )
    lycees = lycees.merge(
        referentiel[["code_commune", "aire"]], on="code_commune", how="left", validate="many_to_one"
    )
    assert set(lycees["aire"].dropna()) == set(referentiel["aire"]), "Une aire n'a aucun lycée."

    ips_rentree = ips[
        (ips["rentree_scolaire"] == config.RENTREE_IPS)
        & ips["type_de_lycee"].isin(config.TYPES_LYCEES_IPS)
    ].copy()
    assert not ips_rentree.empty, f"Pas d'IPS pour la rentrée {config.RENTREE_IPS}."
    ips_rentree["ips"] = pd.to_numeric(ips_rentree[config.COLONNE_IPS])
    ips_rentree["secteur_ips"] = ips_rentree["secteur"].map(config.SECTEURS_IPS)

    # Des lycées de l'IPS situés dans les aires manquent aux lycées des aires, car l'annuaire les
    # filtre, les regroupe sous un autre UAI ou les place ailleurs : on exige que la liste soit
    # celle de `config`
    ips_des_aires = ips_rentree[
        ips_rentree["code_insee_de_la_commune"].isin(referentiel["code_commune"])
        & ips_rentree["ips"].notna()
    ]
    lycees_des_aires = set(lycees.loc[lycees["aire"].notna(), "uai"])
    non_retenus = sorted(set(ips_des_aires["uai"]) - lycees_des_aires)
    assert non_retenus == sorted(config.UAI_IPS_NON_RETENUS), (
        f"Lycées de l'IPS absents de la liste : {non_retenus}, attendus : "
        f"{sorted(config.UAI_IPS_NON_RETENUS)} (config.UAI_IPS_NON_RETENUS)."
    )

    lycees = lycees.merge(
        ips_rentree[["uai", "ips", "secteur_ips"]], on="uai", how="left", validate="many_to_one"
    )
    # Un secteur différent d'une source à l'autre attribuerait l'IPS au mauvais secteur
    secteur_different = lycees["secteur_ips"].notna() & (lycees["secteur"] != lycees["secteur_ips"])
    uai_differents = lycees.loc[secteur_different, "uai"].tolist()
    assert not uai_differents, f"Secteur différent dans l'annuaire et l'IPS : {uai_differents}."
    return lycees.drop(columns="secteur_ips")
