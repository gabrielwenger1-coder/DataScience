"""Figures du rapport : une fonction par figure, avec les mêmes couleurs de secteur."""

import html
import itertools

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from cadres_lycees import config


def fig1(profil: pd.DataFrame) -> Figure:
    """Fig. 1 : pour chaque aire, la part de lycées privés sous contrat et l'IPS moyen par secteur.

    `profil` vient de `analyse.profil_aires`. Les aires sont triées par part de privé, la plus
    forte en haut. Le titre décrit la figure : le message est rédigé par le groupe.
    """
    profil = profil.sort_values("part_prive")
    positions = list(range(len(profil)))
    couleur_public = config.COULEURS_SECTEURS["public"]
    couleur_prive = config.COULEURS_SECTEURS["prive"]
    texte = config.COULEUR_TEXTE

    fig, (ax_part, ax_ips) = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    ax_part.barh(positions, profil["part_prive"] * 100, height=0.5, color=couleur_prive)
    for position, ligne in enumerate(profil.itertuples()):
        ax_part.text(
            ligne.part_prive * 100 + 1,
            position,
            f"{ligne.part_prive:.0%} ({ligne.n_prive} sur {ligne.n_lycees})",
            va="center",
            fontsize=9,
            color=texte,
        )
    ax_part.set_xlim(0, 100)
    ax_part.set_xlabel("Part de lycées privés sous contrat (%)", color=texte)
    ax_part.set_title("Poids du privé", loc="left", fontsize=11)
    ax_part.set_yticks(positions)
    ax_part.set_yticklabels(profil.index, color=texte)

    for position, ligne in enumerate(profil.itertuples()):
        ax_ips.plot(
            [ligne.ips_public, ligne.ips_prive],
            [position, position],
            color=config.COULEUR_LIAISON,
            zorder=1,
        )
        ax_ips.text(
            max(ligne.ips_public, ligne.ips_prive) + 1.5,
            position,
            f"{ligne.ecart_ips:+.0f}  ({ligne.n_ips_prive} privés, {ligne.n_ips_public} publics)",
            va="center",
            fontsize=9,
            color=texte,
        )
    ax_ips.scatter(
        profil["ips_public"],
        positions,
        s=60,
        color=couleur_public,
        edgecolor="white",
        zorder=2,
        label="Lycées publics",
    )
    ax_ips.scatter(
        profil["ips_prive"],
        positions,
        s=60,
        color=couleur_prive,
        edgecolor="white",
        zorder=2,
        label="Lycées privés sous contrat",
    )
    bas = profil[["ips_public", "ips_prive"]].min().min()
    haut = profil[["ips_public", "ips_prive"]].max().max()
    ax_ips.set_xlim(bas - 3, haut + 32)
    ax_ips.set_xlabel(
        f"IPS moyen, voie générale et technologique, rentrée {config.RENTREE_IPS}", color=texte
    )
    ax_ips.set_title("IPS moyen par secteur et écart privé moins public", loc="left", fontsize=11)
    ax_ips.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)

    for ax in (ax_part, ax_ips):
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=texte)

    fig.suptitle(
        f"Les {len(profil)} aires candidates : part de lycées privés et IPS par secteur",
        fontsize=13,
    )
    n_lycees = profil["n_lycees"].sum()
    n_sans_ips = n_lycees - profil[["n_ips_public", "n_ips_prive"]].sum().sum()
    fig.text(
        0.01,
        0.01,
        "Lycées généraux, technologiques et polyvalents, publics et privés sous contrat, situés "
        "dans les communes de l'aire.\n"
        f"IPS : moyenne simple des lycées qui en ont un ({n_sans_ips} lycées sur {n_lycees} n'en "
        "ont pas).\n"
        f"Sources : annuaire de l'éducation ({config.DATE_ANNUAIRE}), DEPP (IPS), Insee (aires "
        "d'attraction des villes 2020), IGN.",
        fontsize=8,
        color=texte,
    )
    fig.tight_layout(rect=(0, 0.1, 1, 0.95))
    # Fermée, la figure n'est affichée qu'une fois par un notebook, avec sa valeur de retour
    plt.close(fig)
    return fig


def _libelles_distance() -> list[str]:
    """Libellés des classes de `config.BORNES_DISTANCE_KM`, du plus proche au plus loin."""
    bornes = config.BORNES_DISTANCE_KM
    libelles = [f"{bornes[0]} km ou moins"]
    libelles += [f"{bas} à {haut} km" for bas, haut in itertools.pairwise(bornes)]
    libelles.append(f"plus de {bornes[-1]} km")
    return libelles


def fig3(communes: gpd.GeoDataFrame, lycees: gpd.GeoDataFrame) -> folium.Map:
    """Fig. 3 : carte interactive de la distance au lycée privé sous contrat le plus proche.

    `communes` vient de `geo.referentiel_communes`, complété par `accessibilite.indicateurs`
    pour les lycées privés ; `lycees` vient de `nettoyage.lycees_geo`. Les communes sont colorées
    par classe de distance, les lycées sont des points colorés par secteur. Les contours sont
    simplifiés pour l'affichage seulement. Le titre décrit la carte : le message est rédigé par
    le groupe.
    """
    assert communes.crs == config.CRS_CALCUL and lycees.crs == config.CRS_CALCUL, (
        f"Communes en {communes.crs}, lycées en {lycees.crs} : EPSG:{config.CRS_CALCUL} attendu."
    )
    # La simplification ne garde les frontières partagées que si les contours, sans trou ni
    # chevauchement, forment une couverture valide
    assert communes.geometry.is_valid_coverage(), "Les contours ne forment pas une couverture."

    bornes = [0, *config.BORNES_DISTANCE_KM, float("inf")]
    # Bornes supérieures incluses, comme dans les indicateurs : « 5 km ou moins » équivaut à
    # au moins un lycée privé dans le rayon de 5 km
    classe = pd.cut(communes["dist_lyc_prive_min"], bornes, labels=False, include_lowest=True)
    assert classe.notna().all(), "Distance hors des classes de la Fig. 3."
    # Seules les colonnes affichées partent dans la page : la seconde géométrie (`centroide`)
    # ferait échouer l'export GeoJSON, et les autres colonnes l'alourdiraient
    affichage = gpd.GeoDataFrame(
        {
            "nom_commune": communes["nom_commune"],
            "aire": communes["aire"],
            "dist_lyc_prive_min": communes["dist_lyc_prive_min"].map(
                lambda km: f"{km:.1f} km".replace(".", ",")
            ),
            "n_lyc_prive_5km": communes["n_lyc_prive_5km"],
            "n_lyc_prive_10km": communes["n_lyc_prive_10km"],
            "couleur": [config.COULEURS_DISTANCE[rang] for rang in classe],
        },
        geometry=communes.geometry.simplify_coverage(config.SIMPLIFICATION_CARTE_M),
    ).to_crs(config.CRS_CARTES)
    limites = affichage[["aire", "geometry"]].dissolve("aire").reset_index()

    # Lycées affichés : ceux à 10 km ou moins du contour d'une commune, donc tous ceux que
    # comptent les `n_lyc_*`, et le lycée privé le plus proche de chaque commune, qui donne sa
    # couleur à la commune même quand il est plus loin
    zone = communes.geometry.union_all()
    dans_la_zone = lycees.distance(zone) <= max(config.RAYONS_KM) * 1000
    centroides = communes.set_geometry("centroide")[["centroide"]]
    prives = lycees.loc[lycees["secteur"] == "prive", ["geometry"]]
    plus_proches = gpd.sjoin_nearest(centroides, prives)["index_right"]
    affiches = lycees[dans_la_zone | lycees.index.isin(plus_proches)].to_crs(config.CRS_CARTES)

    carte = folium.Map(tiles=None, control_scale=True)
    for rang, (nom, fournisseur) in enumerate(config.FONDS_CARTE.items()):
        # Le premier fond s'affiche, les autres se choisissent dans le sélecteur de couches
        folium.TileLayer(fournisseur, name=nom, show=(rang == 0)).add_to(carte)
    ouest, sud, est, nord = affichage.total_bounds
    carte.fit_bounds([[sud, ouest], [nord, est]])
    folium.GeoJson(
        affichage,
        name="Distance au lycée privé sous contrat le plus proche",
        style_function=lambda commune: {
            "fillColor": commune["properties"]["couleur"],
            "fillOpacity": 0.8,
            "color": "white",
            "weight": 0.5,
        },
        highlight_function=lambda _: {"color": config.COULEUR_TEXTE, "weight": 2},
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "nom_commune",
                "aire",
                "dist_lyc_prive_min",
                "n_lyc_prive_5km",
                "n_lyc_prive_10km",
            ],
            aliases=[
                "Commune",
                "Aire",
                "Lycée privé sous contrat le plus proche",
                "Lycées privés sous contrat à 5 km",
                "Lycées privés sous contrat à 10 km",
            ],
        ),
    ).add_to(carte)
    folium.GeoJson(
        limites,
        name="Limites des aires",
        style_function=lambda _: {"fill": False, "color": config.COULEUR_TEXTE, "weight": 2},
    ).add_to(carte)

    # Les privés en dernier, pour qu'ils restent visibles au-dessus des publics
    for secteur in ("public", "prive"):
        du_secteur = affiches[affiches["secteur"] == secteur]
        libelle = f"secteur {config.LIBELLES_SECTEURS[secteur]}"
        groupe = folium.FeatureGroup(name=f"Lycées, {libelle} ({len(du_secteur)})")
        for lycee in du_secteur.itertuples():
            if pd.isna(lycee.ips):
                ips = "IPS non publié"
            else:
                ips = f"IPS {lycee.ips:.0f} (voie GT, {config.RENTREE_IPS})"
            folium.CircleMarker(
                location=[lycee.geometry.y, lycee.geometry.x],
                radius=5,
                color="white",
                weight=1,
                fill=True,
                fill_color=config.COULEURS_SECTEURS[secteur],
                fill_opacity=1,
                tooltip=f"<b>{html.escape(lycee.nom_lycee)}</b><br>{libelle.capitalize()}<br>{ips}",
            ).add_to(groupe)
        groupe.add_to(carte)
    folium.LayerControl(collapsed=False).add_to(carte)

    # folium n'a pas de légende par classes : elle est écrite en HTML, fixée au-dessus du fond
    pastille = (
        '<span style="display:inline-block;width:10px;height:10px;margin-right:6px;'
        f"border:1px solid {config.COULEUR_LIAISON};border-radius:{{arrondi}};"
        'background:{couleur}"></span>'
    )
    classes = "".join(
        f"<div>{pastille.format(arrondi=0, couleur=couleur)}{libelle}</div>"
        for couleur, libelle in zip(config.COULEURS_DISTANCE, _libelles_distance(), strict=True)
    )
    points = "".join(
        f"<div>{pastille.format(arrondi='50%', couleur=config.COULEURS_SECTEURS[secteur])}"
        f"Lycée, secteur {config.LIBELLES_SECTEURS[secteur]}</div>"
        for secteur in ("prive", "public")
    )
    aires = ", ".join(sorted(communes["aire"].unique()))
    note = (
        f"{config.RAYON_PRINCIPAL_KM} km ou moins : au moins un lycée privé sous contrat dans "
        "le rayon principal. Distance à vol d'oiseau depuis le centroïde de la commune, "
        "calculée sur les lycées de France métropolitaine (les lycées étrangers sont absents). "
        "Points : lycées généraux, technologiques et polyvalents à "
        f"{max(config.RAYONS_KM)} km ou moins d'une commune, y compris hors des aires, et "
        "lycée privé le plus proche de chaque commune."
    )
    source = (
        f"Sources : annuaire de l'éducation ({config.DATE_ANNUAIRE}), DEPP (IPS, rentrée "
        f"{config.RENTREE_IPS}), Insee (aires d'attraction des villes 2020), IGN (ADMIN EXPRESS, "
        f"COG {config.ANNEE_COG})."
    )
    legende = (
        '<div style="position:fixed;bottom:28px;left:12px;z-index:1000;background:white;'
        f'padding:8px;font:11px sans-serif;color:{config.COULEUR_TEXTE};width:250px">'
        f"<b>{aires} : distance au lycée privé sous contrat le plus proche</b>"
        f"{classes}{points}"
        f"<p style='font-size:10px'>{note}</p><p style='font-size:10px'>{source}</p></div>"
    )
    carte.get_root().html.add_child(folium.Element(legende))
    return carte
