"""Nettoyage et jointures des sources : lycées avec leur aire, leur IPS et leur IVAL, population."""

import geopandas as gpd
import pandas as pd

from cadres_lycees import config


def lycees_geo(
    annuaire: gpd.GeoDataFrame,
    ips: pd.DataFrame,
    sessions_ival: pd.DataFrame,
    referentiel: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Renvoie les lycées de l'annuaire avec leur aire, leur secteur, leur IPS et leur IVAL.

    Un lycée est rattaché à une aire par le code de sa commune dans l'annuaire, qui nomme les
    arrondissements de Lyon (693xx) comme le référentiel. `aire` est manquante pour un lycée
    situé hors des aires : il compte quand même dans l'accessibilité des communes proches.
    L'IPS est celui de la rentrée et de la mesure choisies dans `config` ; il reste manquant pour
    un lycée sans IPS, une valeur manquante ne se remplace pas. `sessions_ival` vient de
    `collecte.ival_lycees` ; `ival` et `poids_ival` (voir `ival_par_lycee`) manquent pour un
    lycée qui ne remplit pas la règle A1. Un UAI multi-sites compte pour un lycée.
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
    lycees = lycees.drop(columns="secteur_ips")

    # Comme pour l'IPS : des lycées de l'IVAL situés dans les aires ne sont pas des lycées
    # retenus (nature, contrat, fermeture) ; on exige que la liste soit celle de `config`, pour
    # qu'un lycée publié sous un autre UAI ne perde pas son IVAL sans erreur
    ival = ival_par_lycee(sessions_ival)
    dans_les_aires = sessions_ival["code_commune"].isin(referentiel["code_commune"])
    uai_des_aires = set(sessions_ival.loc[dans_les_aires, "uai"].replace(config.UAI_IVAL_RATTACHES))
    non_retenus = sorted((uai_des_aires & set(ival.index)) - set(lycees["uai"]))
    assert non_retenus == sorted(config.UAI_IVAL_NON_RETENUS), (
        f"Lycées de l'IVAL absents de la liste : {non_retenus}, attendus : "
        f"{sorted(config.UAI_IVAL_NON_RETENUS)} (config.UAI_IVAL_NON_RETENUS)."
    )
    return lycees.merge(ival, left_on="uai", right_index=True, how="left", validate="many_to_one")


def population(serie: pd.DataFrame, referentiel: gpd.GeoDataFrame) -> pd.DataFrame:
    """Renvoie la population 2022 et la densité des communes du référentiel, par `code_commune`.

    `serie` vient de `collecte.serie_historique_rp2022`. `densite` est en habitants par km², avec
    `SUPERF`, la superficie de l'Insee, et non la surface des contours : même source que la
    population (choix de l'étudiant du 20/10). Les communes sont celles du référentiel, au grain
    des arrondissements à Lyon : la commune parente 69123 n'est jamais lue, ce qui évite de
    compter Lyon deux fois. Le résultat se joint par `code_commune`, pas par position.
    """
    serie = serie.set_index("CODGEO")
    manquantes = sorted(set(referentiel["code_commune"]) - set(serie.index))
    assert not manquantes, f"Communes absentes de la série historique : {manquantes}"
    pop_superficie = serie.loc[referentiel["code_commune"]]
    assert pop_superficie.notna().all().all(), "Population ou superficie manquante."
    assert (pop_superficie["SUPERF"] > 0).all(), "Superficie nulle ou négative."

    return pd.DataFrame(
        {
            "pop_2022": pop_superficie["P22_POP"],
            "densite": pop_superficie["P22_POP"] / pop_superficie["SUPERF"],
        }
    ).rename_axis("code_commune")


def ival_par_lycee(sessions_ival: pd.DataFrame) -> pd.DataFrame:
    """Renvoie l'IVAL de chaque lycée selon la règle A1 (PLAN §2.4), indexée par `uai`.

    `ival` est la moyenne simple des `va_acces_2nde` des sessions 2012 à 2022, pour les lycées
    qui en ont au moins 5 où la valeur ajoutée est renseignée ; `poids_ival` est la moyenne de
    `presents_total` sur ces sessions. Les autres lycées sont absents du résultat. Les sessions
    des UAI de `config.UAI_IVAL_RATTACHES` sont rattachées à l'UAI de l'annuaire : quand
    plusieurs sites publient la même session, elle vaut la valeur ajoutée moyenne des sites
    renseignés, pondérée par leurs présents, et ses présents sont ceux de ces sites additionnés.
    """
    rattaches = config.UAI_IVAL_RATTACHES
    assert set(rattaches) <= set(sessions_ival["uai"]), "Un UAI rattaché manque à l'IVAL."

    sessions = pd.DataFrame(
        {
            "uai": sessions_ival["uai"].replace(rattaches),
            "annee": sessions_ival["annee"].astype(int),
            "va_acces_2nde": pd.to_numeric(sessions_ival["va_acces_2nde"]),
            "presents_total": pd.to_numeric(sessions_ival["presents_total"]),
        }
    )
    dans_la_periode = sessions["annee"].between(
        config.PREMIERE_SESSION_IVAL, config.DERNIERE_SESSION_IVAL
    )
    valides = sessions[dans_la_periode & sessions["va_acces_2nde"].notna()].copy()
    assert (valides["presents_total"] > 0).all(), "Session valide sans présents."

    # Pour un lycée d'un seul site, la moyenne pondérée d'une session est sa valeur ajoutée
    valides["va_x_presents"] = valides["va_acces_2nde"] * valides["presents_total"]
    par_session = valides.groupby(["uai", "annee"])[["va_x_presents", "presents_total"]].sum()
    par_session["va"] = par_session["va_x_presents"] / par_session["presents_total"]

    par_lycee = par_session.groupby("uai").agg(
        ival=("va", "mean"),
        poids_ival=("presents_total", "mean"),
        nb_sessions=("va", "size"),
    )
    retenus = par_lycee[par_lycee["nb_sessions"] >= config.NB_SESSIONS_MIN_IVAL]
    return retenus[["ival", "poids_ival"]]
