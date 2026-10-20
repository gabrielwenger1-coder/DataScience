"""Nettoyage et jointures des sources : lycées avec leur aire, leur IPS et leur IVAL, population."""

import itertools

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
    pop_superficie = _lignes_du_referentiel(serie, referentiel, ["P22_POP", "SUPERF"])
    assert pop_superficie.notna().all().all(), "Population ou superficie manquante."
    assert (pop_superficie["SUPERF"] > 0).all(), "Superficie nulle ou négative."
    # Une commune sans habitant aurait une densité nulle, et un logarithme infini
    assert (pop_superficie["P22_POP"] > 0).all(), "Commune sans habitant."

    densite = pop_superficie["P22_POP"] / pop_superficie["SUPERF"]
    return pd.DataFrame(
        {"pop_2022": pop_superficie["P22_POP"], "densite": densite, "log_densite": np.log(densite)}
    )


def croissance_population(serie: pd.DataFrame, referentiel: gpd.GeoDataFrame) -> pd.DataFrame:
    """Renvoie le taux de variation annuel moyen de la population entre deux recensements, en %.

    Une ligne par commune du référentiel (`code_commune`), une colonne par période entre deux
    recensements successifs de `config.COLONNES_POPULATION`, nommée par exemple « 1968-1975 ».
    Le taux vaut (P_fin / P_début) ^ (1 / n) − 1, où n est l'écart entre les deux millésimes en
    années. C'est une approximation, les recensements n'ayant pas lieu à date fixe : elle pèse
    surtout sur 1999-2006 (6,8 ans entre le recensement de mars 1999 et la date de référence du
    1er janvier 2006), dont les taux bougent d'au plus 0,23 point dans les 3 aires retenues.
    `serie` vient de `collecte.serie_historique_rp2022`. Lyon y est lue au grain de ses
    arrondissements, comme dans `population`.
    """
    colonnes = list(config.COLONNES_POPULATION.values())
    populations = _lignes_du_referentiel(serie, referentiel, colonnes)
    # Une population nulle ou manquante donnerait un taux infini ou manquant, sans erreur
    assert (populations > 0).all().all(), "Population nulle ou manquante à un recensement."

    croissance = pd.DataFrame(index=populations.index)
    recensements = config.COLONNES_POPULATION.items()
    for (debut, colonne_debut), (fin, colonne_fin) in itertools.pairwise(recensements):
        ratio = populations[colonne_fin] / populations[colonne_debut]
        croissance[f"{debut}-{fin}"] = (ratio ** (1 / (fin - debut)) - 1) * 100
    return croissance


def _lignes_du_referentiel(
    serie: pd.DataFrame, referentiel: gpd.GeoDataFrame, colonnes: list[str]
) -> pd.DataFrame:
    """Renvoie `colonnes` de la série historique pour les communes du référentiel.

    Le résultat est indexé par `code_commune`. Une commune absente de la série fait échouer.
    """
    serie = serie.set_index("CODGEO")
    manquantes = sorted(set(referentiel["code_commune"]) - set(serie.index))
    assert not manquantes, f"Communes absentes de la série historique : {manquantes}"
    return serie.loc[referentiel["code_commune"], colonnes].rename_axis("code_commune")


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
