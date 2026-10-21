"""Nettoyage et jointures des sources : lycées avec leur aire, leur IPS et leur IVAL, population."""

import geopandas as gpd
import numpy as np
import pandas as pd

from cadres_lycees import config


def lycees_geo(
    annuaire: gpd.GeoDataFrame,
    ips: pd.DataFrame,
    sessions_ival: pd.DataFrame,
    referentiel: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Renvoie les lycées de l'annuaire avec leur aire, leur secteur, leur IPS et leur IVAL.

    Une ligne par lycée, en Lambert 93, avec `uai`, `nom_lycee`, `code_commune`, `secteur`,
    `aire` (manquante hors des aires), `ips`, `ival`, `poids_ival` et `geometry`. `annuaire`,
    `ips` et `sessions_ival` viennent de `collecte`, `referentiel` de `geo.referentiel_communes`.
    """
    lycees = _un_lycee_par_uai(annuaire)
    lycees = _ajouter_aire(lycees, referentiel)
    lycees = _ajouter_ips(lycees, ips, referentiel)
    return _ajouter_ival(lycees, sessions_ival, referentiel)


def _un_lycee_par_uai(annuaire: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Renvoie une ligne par UAI de l'annuaire filtré, renommée, avec son secteur, en Lambert 93.

    La sélection des lycées est faite par `collecte.annuaire_education`. Un UAI multi-sites
    compte pour un lycée. Tous les lycées doivent avoir des coordonnées.
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
    return lycees


def _ajouter_aire(lycees: gpd.GeoDataFrame, referentiel: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Ajoute l'aire du lycée, d'après le code de sa commune.

    L'annuaire nomme les arrondissements de Lyon (693xx) comme le référentiel. Un lycée hors des
    aires garde une aire manquante : il compte quand même dans l'accessibilité des communes
    proches.
    """
    # On vérifie que la position dit la même chose que le code (code dans le référentiel si et
    # seulement si position dans une aire) : une commune fusionnée sous un nouveau code
    # laisserait sinon son lycée sans aire, sans bruit. La position des lycées hors des aires
    # n'est pas contrôlée
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
    return lycees


def _ajouter_ips(
    lycees: gpd.GeoDataFrame, ips: pd.DataFrame, referentiel: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Ajoute l'IPS de la rentrée et de la mesure choisies dans `config`.

    Il reste manquant pour un lycée sans IPS : une valeur manquante ne se remplace pas.
    """
    ips_rentree = ips[
        (ips["rentree_scolaire"] == config.RENTREE_IPS)
        & ips["type_de_lycee"].isin(config.TYPES_LYCEES_IPS)
    ].copy()
    assert not ips_rentree.empty, f"Pas d'IPS pour la rentrée {config.RENTREE_IPS}."
    ips_rentree["ips"] = pd.to_numeric(ips_rentree[config.COLONNE_IPS])
    ips_rentree["secteur_ips"] = ips_rentree["secteur"].map(config.SECTEURS_IPS)
    # Un UAI mal recopié dans la liste ne serait jamais attendu ci-dessous, donc jamais vu
    absents = sorted(set(config.UAI_IPS_NON_RETENUS) - set(ips_rentree["uai"]))
    assert not absents, f"UAI de config.UAI_IPS_NON_RETENUS absents de l'IPS : {absents}."

    # Des lycées de l'IPS situés dans les aires manquent aux lycées des aires, car l'annuaire les
    # filtre, les regroupe sous un autre UAI ou les place ailleurs : on exige que ce soient ceux
    # de `config` situés dans les aires étudiées
    dans_les_aires = ips_rentree["code_insee_de_la_commune"].isin(referentiel["code_commune"])
    uai_des_aires = set(ips_rentree.loc[dans_les_aires & ips_rentree["ips"].notna(), "uai"])
    non_retenus = sorted(uai_des_aires - set(lycees.loc[lycees["aire"].notna(), "uai"]))
    attendus = sorted(uai_des_aires & set(config.UAI_IPS_NON_RETENUS))
    assert non_retenus == attendus, (
        f"Lycées de l'IPS absents des lycées des aires : {non_retenus}, attendus : {attendus} "
        "(config.UAI_IPS_NON_RETENUS)."
    )

    lycees = lycees.merge(
        ips_rentree[["uai", "ips", "secteur_ips"]], on="uai", how="left", validate="many_to_one"
    )
    # Un secteur différent d'une source à l'autre attribuerait l'IPS au mauvais secteur
    secteur_different = lycees["secteur_ips"].notna() & (lycees["secteur"] != lycees["secteur_ips"])
    uai_differents = lycees.loc[secteur_different, "uai"].tolist()
    assert not uai_differents, f"Secteur différent dans l'annuaire et l'IPS : {uai_differents}."
    return lycees.drop(columns="secteur_ips")


def _ajouter_ival(
    lycees: gpd.GeoDataFrame, sessions_ival: pd.DataFrame, referentiel: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Ajoute `ival` et `poids_ival` (voir `ival_par_lycee`) ; manquants hors de la règle A1."""
    ival = ival_par_lycee(
        sessions_ival,
        config.PREMIERE_SESSION_IVAL,
        config.DERNIERE_SESSION_IVAL,
        config.NB_SESSIONS_MIN_IVAL,
    )
    # Un UAI mal recopié dans la liste ne serait jamais attendu ci-dessous, donc jamais vu
    absents = sorted(set(config.UAI_IVAL_NON_RETENUS) - set(ival.index))
    assert not absents, f"UAI de config.UAI_IVAL_NON_RETENUS absents de l'IVAL : {absents}."
    # Comme pour l'IPS : des lycées de l'IVAL situés dans les aires ne sont pas des lycées
    # retenus (nature, contrat, fermeture) ; on exige que ce soient ceux de `config` situés dans
    # les aires étudiées, pour qu'un lycée publié sous un autre UAI ne perde pas son IVAL sans
    # erreur
    dans_les_aires = sessions_ival["code_commune"].isin(referentiel["code_commune"])
    uai_des_aires = set(sessions_ival.loc[dans_les_aires, "uai"].replace(config.UAI_IVAL_RATTACHES))
    uai_avec_ival = uai_des_aires & set(ival.index)
    non_retenus = sorted(uai_avec_ival - set(lycees["uai"]))
    attendus = sorted(uai_avec_ival & set(config.UAI_IVAL_NON_RETENUS))
    assert non_retenus == attendus, (
        f"Lycées de l'IVAL absents des lycées retenus : {non_retenus}, attendus : {attendus} "
        "(config.UAI_IVAL_NON_RETENUS)."
    )
    return lycees.merge(ival, left_on="uai", right_index=True, how="left", validate="many_to_one")


def population(serie: pd.DataFrame, referentiel: gpd.GeoDataFrame) -> pd.DataFrame:
    """Renvoie la population 2022 et la densité des communes du référentiel, par `code_commune`.

    `serie` vient de `collecte.serie_historique_rp2022`. `densite` est en habitants par km², avec
    `SUPERF`, la superficie de l'Insee, et non la surface des contours : même source que la
    population (choix de l'étudiant du 20/10). `log_densite` est la forme sous laquelle la
    densité sert de contrôle (A7), tant sa distribution est asymétrique. Les communes sont celles
    du référentiel, au grain des arrondissements à Lyon : la commune parente 69123 n'est jamais
    lue, ce qui évite de compter Lyon deux fois. Le résultat se joint par `code_commune`.
    """
    serie = serie.set_index("CODGEO")
    manquantes = sorted(set(referentiel["code_commune"]) - set(serie.index))
    assert not manquantes, f"Communes absentes de la série historique : {manquantes}"
    pop_superficie = serie.loc[referentiel["code_commune"]]
    assert pop_superficie.notna().all().all(), "Population ou superficie manquante."
    assert (pop_superficie["SUPERF"] > 0).all(), "Superficie nulle ou négative."
    # Une commune sans habitant aurait une densité nulle, et un logarithme infini
    assert (pop_superficie["P22_POP"] > 0).all(), "Commune sans habitant."

    densite = pop_superficie["P22_POP"] / pop_superficie["SUPERF"]
    return pd.DataFrame(
        {"pop_2022": pop_superficie["P22_POP"], "densite": densite, "log_densite": np.log(densite)}
    ).rename_axis("code_commune")


def part_cadres_iris(
    activite_2011: pd.DataFrame, activite_2022: pd.DataFrame, passage: pd.DataFrame
) -> pd.DataFrame:
    """Renvoie la part de cadres parmi les actifs de 15 à 64 ans par IRIS, en 2011 et en 2022.

    Une ligne par IRIS de 2022 (index `iris`, codes de la géographie 2024). La part est le groupe
    3 sur la somme des 6 groupes, comme pour la commune (§2.3), mais sur les 15-64 ans, seule
    tranche que les bases IRIS croisent avec la CSP. Elle manque sans actif, et en 2011 si le code
    n'existait pas. `comparable` est vrai si l'IRIS a le même code aux deux dates, dans une
    commune qui n'en a absorbé aucune autre entre les géographies 2013 et 2024, et au moins
    `config.SEUIL_ACTIFS_IRIS` actifs aux deux dates (A18). Les arguments viennent de
    `collecte.activite_iris_2011`, `collecte.activite_iris_2022` et `collecte.passage_communes`.
    """
    parts = pd.DataFrame(index=pd.Index(activite_2022["IRIS"], name="iris"))
    annees = (
        (2011, activite_2011, config.ACTIFS_1564_IRIS_2011, config.CADRES_1564_IRIS_2011),
        (2022, activite_2022, config.ACTIFS_1564_IRIS_2022, config.CADRES_1564_IRIS_2022),
    )
    for annee, activite, groupes, cadres in annees:
        effectifs = activite.set_index("IRIS")[list(groupes)]
        actifs = effectifs.sum(axis=1)
        # Un IRIS d'activité ou de loisirs peut n'avoir aucun actif : sa part n'existe pas
        part = (effectifs[cadres] / actifs).where(actifs > 0)
        parts[f"actifs_1564_{annee}"] = actifs.reindex(parts.index)
        parts[f"part_cadres_1564_{annee}"] = part.reindex(parts.index)
    for annee in (2011, 2022):
        renseignee = parts[f"part_cadres_1564_{annee}"].dropna()
        assert renseignee.between(0, 1).all(), f"Part de cadres hors de [0, 1] en {annee}."

    # Une commune non découpée qui en absorbe une autre garde son code IRIS (commune + 0000),
    # mais pas son territoire : même code ne veut alors pas dire même IRIS
    filiations = passage.dropna().drop_duplicates()
    communes_2013 = filiations.groupby("CODGEO_2024")["CODGEO_2013"].nunique()
    fusionnees = communes_2013.index[communes_2013 > 1]
    commune = activite_2022.set_index("IRIS")["COM"]
    meme_code = pd.Series(parts.index.isin(activite_2011["IRIS"]), index=parts.index)
    commune_fusionnee = commune.reindex(parts.index).isin(fusionnees)
    actifs = parts[["actifs_1564_2011", "actifs_1564_2022"]]
    assez_d_actifs = (actifs >= config.SEUIL_ACTIFS_IRIS).all(axis=1)
    parts["comparable"] = meme_code & ~commune_fusionnee & assez_d_actifs
    return parts


def ival_par_lycee(
    sessions_ival: pd.DataFrame, premiere: int, derniere: int, nb_sessions_min: int
) -> pd.DataFrame:
    """Renvoie l'IVAL de chaque lycée sur les sessions `premiere` à `derniere`, indexée par `uai`.

    `ival` est la moyenne simple des `va_acces_2nde` de ces sessions, pour les lycées qui en ont
    au moins `nb_sessions_min` où la valeur ajoutée est renseignée ; `poids_ival` est la moyenne
    de `presents_total` sur ces sessions. Les autres lycées sont absents du résultat. La règle A1
    (PLAN §2.4) correspond aux valeurs de `config` ; le test de fiabilité (§3.2) l'applique à
    chaque moitié. Les sessions des UAI de
    `config.UAI_IVAL_RATTACHES` sont rattachées à l'UAI de l'annuaire : quand plusieurs sites
    publient la même session, elle vaut la valeur ajoutée moyenne des sites renseignés, pondérée
    par leurs présents, et ses présents sont ceux de ces sites additionnés.
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
    dans_la_periode = sessions["annee"].between(premiere, derniere)
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
    retenus = par_lycee[par_lycee["nb_sessions"] >= nb_sessions_min]
    return retenus[["ival", "poids_ival"]]
