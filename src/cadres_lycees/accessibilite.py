"""Accessibilité des communes à des points (lycées, gares...) : comptes et distance minimale."""

import geopandas as gpd
import pandas as pd

from cadres_lycees import config


def indicateurs(
    communes: gpd.GeoDataFrame,
    points: gpd.GeoDataFrame,
    prefixe: str,
    rayons: tuple[int, ...] = config.RAYONS_KM,
) -> pd.DataFrame:
    """Renvoie, pour chaque commune, le nombre de points par rayon et la distance au plus proche.

    Distances à vol d'oiseau depuis le centroïde de la commune (PLAN §2.4), en Lambert 93.
    `n_<prefixe>_<r>km` compte les points à r km ou moins, bord compris. `dist_<prefixe>_min`
    est la distance en km au point le plus proche parmi tous les points : `points` doit couvrir
    bien au-delà des communes (toute la métropole pour les lycées), sinon les comptes et la
    distance des communes du bord seraient faussés.

    `communes` a les colonnes `code_commune` et `centroide` (sortie de
    `geo.referentiel_communes`) ; le résultat est indexé par `code_commune`.
    """
    centroides = communes.set_index("code_commune").set_geometry("centroide")[["centroide"]]
    assert centroides.crs == config.CRS_CALCUL and points.crs == config.CRS_CALCUL, (
        f"Communes en {centroides.crs}, points en {points.crs} : les distances demandent "
        f"EPSG:{config.CRS_CALCUL}."
    )
    assert centroides.index.is_unique, "Des codes communes sont en double."
    assert not points.empty, f"Aucun point pour {prefixe}."
    # Un point manquant ou vide serait ignoré par la jointure et la distance, sans erreur
    ponctuel = (points.geom_type == "Point") & ~points.geometry.is_empty
    assert ponctuel.all(), f"Géométries manquantes, vides ou non ponctuelles ({prefixe})."

    acces = pd.DataFrame(index=centroides.index)
    for rayon in rayons:
        # `dwithin` compare la distance exacte au rayon : une zone tampon n'est qu'un polygone
        # inscrit dans le cercle, et perdrait des points tout près du bord. Seule la géométrie
        # des points entre dans la jointure : leurs autres colonnes (le `code_commune` d'un
        # lycée) se mêleraient à celles des communes
        proches = gpd.sjoin(
            centroides, points[["geometry"]], predicate="dwithin", distance=rayon * 1000
        )
        nb_points = proches.groupby(level="code_commune").size()
        # Une commune sans point dans le rayon n'a aucune ligne dans la jointure : elle en a 0
        acces[f"n_{prefixe}_{rayon}km"] = nb_points.reindex(acces.index, fill_value=0)

    # La distance à un ensemble de points est celle du plus proche ; `sjoin_nearest` donnerait
    # plusieurs lignes pour une commune à égale distance de deux points
    tous_les_points = points.geometry.union_all()
    acces[f"dist_{prefixe}_min"] = centroides.distance(tous_les_points) / 1000
    return acces
