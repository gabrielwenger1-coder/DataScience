"""Géographie des communes : référentiel des aires, centroïdes et distances en Lambert 93."""

import geopandas as gpd
import pandas as pd

from cadres_lycees import collecte, config


def _referentiel_aire(nom: str, code_aav: str, aav: pd.DataFrame) -> gpd.GeoDataFrame:
    """Construit les lignes du référentiel pour une aire (voir `referentiel_communes`)."""
    communes_aav = aav[aav["AAV2020"] == code_aav]
    contours = collecte.contours_aire(code_aav).to_crs(config.CRS_CALCUL)

    # Les contours doivent couvrir exactement les communes de la table AAV : un arrondissement
    # compte pour sa commune parente (`INSEE_COM`), il y a donc plus d'unités que de communes
    # à Lyon seulement
    ecart = set(contours["INSEE_COM"]) ^ set(communes_aav["CODGEO"])
    assert not ecart, (
        f"Communes présentes dans les contours ou dans la table AAV seulement, aire {nom} : "
        f"{sorted(ecart)}"
    )
    assert contours["INSEE_COG"].is_unique, f"Codes d'unités en double pour l'aire {nom}."
    # L'égalité d'ensembles passe même si un arrondissement manque, et le centre de l'aire (union
    # des arrondissements de sa commune) serait alors faussé : on compte les unités par commune
    nb_unites = contours.groupby("INSEE_COM").size()
    nb_attendu = [config.NB_ARRONDISSEMENTS.get(parent, 1) for parent in nb_unites.index]
    assert nb_unites.tolist() == nb_attendu, f"Arrondissements manquants dans l'aire {nom}."

    unites = contours.rename(columns={"INSEE_COG": "code_commune", "INSEE_COM": "code_parent"})
    unites = unites[["code_commune", "code_parent", "geometry"]].copy()
    unites["aire"] = nom
    categorie = communes_aav.set_index("CODGEO")["CATEAAV2020"]
    unites["pole_couronne"] = unites["code_parent"].map(categorie).map(config.POLE_COURONNE_AAV)
    assert unites["pole_couronne"].notna().all(), f"Catégorie AAV non reconnue dans l'aire {nom}."

    # Le centre est la commune entière, y compris à Lyon : on réunit ses arrondissements
    # plutôt que de prendre le plus peuplé (Lyon 3e)
    centres = communes_aav.loc[
        communes_aav["CATEAAV2020"] == config.CATEGORIE_COMMUNE_CENTRE, "CODGEO"
    ]
    assert len(centres) == 1, f"{len(centres)} communes-centres dans l'aire {nom}, 1 attendue."
    contour_centre = unites.loc[unites["code_parent"] == centres.iloc[0], "geometry"].union_all()

    unites["centroide"] = unites.geometry.centroid
    unites["dist_centre_km"] = unites["centroide"].distance(contour_centre.centroid) / 1000
    return unites


def referentiel_communes(aires: dict[str, str]) -> gpd.GeoDataFrame:
    """Renvoie une ligne par commune des aires demandées, en Lambert 93.

    `aires` associe le nom de l'aire à son code AAV2020 (par exemple `config.AIRES_CANDIDATES`).
    Les arrondissements municipaux remplacent leur commune parente (PLAN §2.1) : `code_parent`
    donne la commune parente, celle des sources qui ignorent les arrondissements.

    Colonnes : `code_commune`, `code_parent`, `aire`, `pole_couronne`, `geometry` (contour),
    `centroide` (point de référence de la commune, PLAN §2.4) et `dist_centre_km`, la distance
    en kilomètres entre ce centroïde et celui de la commune-centre de l'aire.
    """
    aav = collecte.aav_2020()
    referentiel = pd.concat(
        [_referentiel_aire(nom, code, aav) for nom, code in aires.items()], ignore_index=True
    )

    assert referentiel["code_commune"].is_unique, "Une commune est dans deux aires."
    nb_communes_aav = aav["AAV2020"].isin(aires.values()).sum()
    assert referentiel["code_parent"].nunique() == nb_communes_aav, (
        "Le nombre de communes diffère de celui de la table AAV."
    )
    geometrie_vide = referentiel.geometry.isna() | referentiel.geometry.is_empty
    assert not geometrie_vide.any(), "Des communes n'ont pas de contour."
    return referentiel


def departements_aires(aires: dict[str, str]) -> list[str]:
    """Renvoie les départements des communes des aires (colonne `DEP` de l'AAV), sur 2 caractères.

    Sert à demander l'annuaire : une aire déborde souvent de son département (Toulouse en
    couvre six).
    """
    aav = collecte.aav_2020()
    return sorted(set(aav.loc[aav["AAV2020"].isin(aires.values()), "DEP"]))
