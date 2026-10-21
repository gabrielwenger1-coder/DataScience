"""Figures du rapport : une fonction par figure, avec les mêmes couleurs de secteur."""

import html
import itertools
from collections.abc import Collection

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from shapely import Point

from cadres_lycees import config


def fig1(
    profil: pd.DataFrame, lycees: gpd.GeoDataFrame, titre: str, aires_retenues: Collection[str]
) -> Figure:
    """Fig. 1 : pour chaque aire, la prévalence du privé sous contrat et la composition sociale.

    À gauche, la part du privé en nombre de lycées et en candidats au bac ; à droite, l'IPS de
    chaque lycée par secteur, avec la moyenne simple du secteur et l'écart privé moins public :
    les deux dimensions du critère (b) du choix des aires (PLAN §2.2, §5.1). `profil` vient de
    `analyse.profil_aires`, `lycees` de `nettoyage.lycees_geo` ; `titre` est le message de la
    figure, écrit par le groupe (PLAN §6). Les aires sont triées par écart d'IPS, le plus fort
    en haut ; celles de `aires_retenues` sont mises en avant, nom en gras sur une bande grise.
    """
    inconnues = sorted(set(aires_retenues) - set(profil.index))
    assert not inconnues, f"Aires retenues absentes du profil : {inconnues}."
    profil = profil.sort_values("ecart_ips")
    texte = config.COULEUR_TEXTE
    fig, (ax_part, ax_ips) = plt.subplots(
        1, 2, figsize=(14, 6.2), sharey=True, gridspec_kw={"width_ratios": [1, 1.5]}
    )
    _panneau_prevalence(ax_part, profil)
    _panneau_ips(ax_ips, profil, lycees)
    for ax in (ax_part, ax_ips):
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=texte)
        ax.grid(axis="x", color=config.COULEUR_GRILLE, linewidth=0.8)
        ax.set_axisbelow(True)
    # Les aires occupent les positions 0, 1, 2... dans l'ordre du profil trié, sur les deux
    # panneaux. Une demi-hauteur un peu sous 0,5 laisse un liseré blanc entre deux aires retenues
    # voisines. La bande passe sous tout le reste (zorder 0) : tracée après les points, elle les
    # cacherait
    demi_hauteur_bande = 0.45
    for position, aire in enumerate(profil.index):
        if aire in aires_retenues:
            for ax in (ax_part, ax_ips):
                ax.axhspan(
                    position - demi_hauteur_bande,
                    position + demi_hauteur_bande,
                    color=config.COULEUR_FOND_RETENUES,
                    zorder=0,
                )
            ax_part.get_yticklabels()[position].set_fontweight("bold")

    fig.suptitle(titre, fontsize=13, x=0.01, ha="left")
    n_lycees = profil["n_lycees"].sum()
    n_sans_ips = n_lycees - profil[["n_ips_public", "n_ips_prive"]].sum().sum()
    fig.text(
        0.01,
        0.01,
        "Lycées généraux, technologiques et polyvalents, publics et privés sous contrat, des "
        f"communes de l'aire (annuaire du {config.DATE_ANNUAIRE}). Part en lycées : tous les "
        f"lycées ; part en candidats : présents au bac général et technologique, moyenne "
        f"2012-2022,\npour les {profil['n_avec_candidats'].sum()} lycées sur {n_lycees} qui ont "
        "une IVAL (ce n'est pas une part d'élèves au sens de la DEPP). IPS : voie générale et "
        f"technologique, rentrée {config.RENTREE_IPS}, moyenne simple des lycées, "
        f"{n_sans_ips} lycées sans IPS. En gras sur fond gris : les aires retenues.\n"
        "Sources : annuaire de l'éducation, DEPP (IPS, IVAL), Insee (aires d'attraction des "
        "villes 2020), IGN.",
        fontsize=8,
        color=texte,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    # Fermée, la figure n'est affichée qu'une fois par un notebook, avec sa valeur de retour
    plt.close(fig)
    return fig


def _panneau_prevalence(ax: plt.Axes, profil: pd.DataFrame) -> None:
    """Fig. 1, gauche : part du privé en lycées et en candidats au bac, une ligne par aire."""
    positions = range(len(profil))
    couleur_prive = config.COULEURS_SECTEURS["prive"]
    en_lycees = profil["part_prive"] * 100
    en_candidats = profil["part_prive_candidats"] * 100
    ax.hlines(positions, en_lycees, en_candidats, color=config.COULEUR_LIAISON, zorder=1)
    ax.scatter(
        en_lycees,
        positions,
        s=55,
        color=couleur_prive,
        edgecolor="white",
        zorder=2,
        label="en nombre de lycées",
    )
    ax.scatter(
        en_candidats,
        positions,
        s=55,
        marker="D",
        facecolor="white",
        edgecolor=couleur_prive,
        linewidth=1.5,
        zorder=2,
        label="en candidats au bac",
    )
    ax.set_xlim(0, max(en_lycees.max(), en_candidats.max()) + 8)
    ax.set_xlabel("Part du privé sous contrat (%)", color=config.COULEUR_TEXTE)
    ax.set_title("Prévalence du privé", loc="left", fontsize=11)
    ax.set_yticks(positions)
    ax.set_yticklabels(
        [
            f"{aire}\n{ligne.n_lycees} lycées, {ligne.n_avec_candidats} avec IVAL"
            for aire, ligne in zip(profil.index, profil.itertuples(), strict=True)
        ],
        color=config.COULEUR_TEXTE,
        fontsize=9,
    )
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False)


def _panneau_ips(ax: plt.Axes, profil: pd.DataFrame, lycees: gpd.GeoDataFrame) -> None:
    """Fig. 1, droite : IPS de chaque lycée par secteur, moyenne du secteur et écart, par aire."""
    rang = {aire: position for position, aire in enumerate(profil.index)}
    avec_ips = lycees[lycees["aire"].notna() & lycees["ips"].notna()]
    assert set(avec_ips["aire"]) == set(profil.index), (
        "Les lycées et le profil n'ont pas les mêmes aires."
    )
    # Chaque secteur sur sa propre bande, de part et d'autre de la ligne de l'aire. Dans une
    # bande, les points sont décalés selon le rang de leur IPS, sur quelques niveaux : des lycées
    # d'IPS proches se recouvrent moins, et la figure est la même à chaque exécution. La hauteur
    # d'un point dans sa bande n'a pas de sens
    ecart_bande, nb_niveaux, pas_niveau = 0.17, 5, 0.03
    for secteur, bande in (("public", ecart_bande), ("prive", -ecart_bande)):
        du_secteur = avec_ips[avec_ips["secteur"] == secteur]
        niveau = du_secteur.groupby("aire")["ips"].rank(method="first") % nb_niveaux
        hauteur = du_secteur["aire"].map(rang) + bande + (niveau - nb_niveaux // 2) * pas_niveau
        couleur = config.COULEURS_SECTEURS[secteur]
        ax.scatter(
            du_secteur["ips"],
            hauteur,
            s=14,
            color=couleur,
            alpha=0.55,
            linewidth=0,
            label=f"Lycée, secteur {config.LIBELLES_SECTEURS[secteur]}",
        )
        # La moyenne tracée est celle du profil, d'où vient aussi l'écart écrit à droite
        ax.scatter(
            profil[f"ips_{secteur}"],
            [rang[aire] + bande for aire in profil.index],
            marker="|",
            s=260,
            linewidth=2.5,
            color=couleur,
            zorder=3,
        )

    bord = avec_ips["ips"].max() + 10
    for aire, ligne in zip(profil.index, profil.itertuples(), strict=True):
        ax.text(
            bord,
            rang[aire] + 0.1,
            f"{ligne.ecart_ips:+.0f}",
            ha="right",
            fontsize=10,
            color=config.COULEUR_TEXTE,
            fontweight="bold",
        )
        ax.text(
            bord,
            rang[aire] - 0.1,
            f"{ligne.n_ips_prive} / {ligne.n_ips_public}",
            ha="right",
            va="top",
            fontsize=7,
            color=config.COULEUR_TEXTE,
        )
    ax.text(
        bord,
        len(profil) - 0.45,
        "écart privé − public\nlycées privés / publics",
        ha="right",
        va="bottom",
        fontsize=8,
        color=config.COULEUR_TEXTE,
    )
    ax.set_xlim(avec_ips["ips"].min() - 3, bord + 1)
    ax.set_xlabel(
        f"IPS de chaque lycée, voie générale et technologique, rentrée {config.RENTREE_IPS}",
        color=config.COULEUR_TEXTE,
    )
    ax.set_title("Composition sociale des lycées", loc="left", fontsize=11)
    trait_moyenne = Line2D(
        [],
        [],
        color=config.COULEUR_TEXTE,
        marker="|",
        linestyle="",
        markersize=12,
        markeredgewidth=2.5,
        label="moyenne simple du secteur",
    )
    points, libelles = ax.get_legend_handles_labels()
    ax.legend(
        [*points, trait_moyenne],
        [*libelles, trait_moyenne.get_label()],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=2,
        frameon=False,
    )


def _libelles_distance() -> list[str]:
    """Libellés des classes de `config.BORNES_DISTANCE_KM`, du plus proche au plus loin."""
    bornes = config.BORNES_DISTANCE_KM
    libelles = [f"{bornes[0]} km ou moins"]
    libelles += [f"{bas} à {haut} km" for bas, haut in itertools.pairwise(bornes)]
    libelles.append(f"plus de {bornes[-1]} km")
    return libelles


def fig3(communes: gpd.GeoDataFrame, lycees: gpd.GeoDataFrame, titre: str) -> folium.Map:
    """Fig. 3 : carte interactive de la distance au lycée privé sous contrat le plus proche.

    `communes` et `lycees` sont la base et les lycées de `pipeline.construire_base`. Les communes
    sont colorées par classe de distance, les lycées sont des points colorés par secteur. Les
    contours sont simplifiés pour l'affichage seulement. `titre` est le message de la carte,
    écrit par le groupe (PLAN §6) ; la légende en décrit le contenu.
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
        "<b>Distance au lycée privé sous contrat le plus proche</b>"
        f"{classes}{points}"
        f"<p style='font-size:10px'>{note}</p><p style='font-size:10px'>{source}</p></div>"
    )
    carte.get_root().html.add_child(folium.Element(legende))
    # À droite des boutons de zoom, en haut à gauche de la carte
    entete = (
        '<div style="position:fixed;top:10px;left:56px;z-index:1000;background:white;'
        f'padding:6px 10px;font:bold 14px sans-serif;color:{config.COULEUR_TEXTE};max-width:60%">'
        f"{html.escape(titre)}</div>"
    )
    carte.get_root().html.add_child(folium.Element(entete))
    return carte


def carte_iris(
    contours: gpd.GeoDataFrame, parts: pd.DataFrame, centre: Point, titre: str
) -> Figure:
    """Carte statique de la part de cadres par IRIS d'une aire, en 2011 puis en 2022 (A18).

    `contours` vient de `collecte.contours_iris`, `parts` de `nettoyage.part_cadres_iris`. En haut,
    l'aire entière ; en bas, un zoom sur un carré de `config.ZOOM_IRIS_KM` km de demi-côté autour
    de `centre` (un point en Lambert 93), où les IRIS de la ville-centre deviennent lisibles. Les
    quatre panneaux ont les mêmes classes ; les IRIS non comparables (code ou territoire changé,
    trop peu d'actifs à une date) sont hachurés en gris. C'est une exploration (§5.8) : ni lycées
    ni test. `titre` est le message de la carte, écrit par le groupe (PLAN §6).
    """
    codes = contours["CODE_IRIS"].replace(config.IRIS_RECODES_2025_2024)
    absents = sorted(set(codes) - set(parts.index))
    assert not absents, f"IRIS des contours absents des données de 2022 : {absents}"
    carte = contours.to_crs(config.CRS_CALCUL).assign(iris=codes.to_numpy())
    carte = carte.join(parts, on="iris", validate="one_to_one")
    comparables = carte[carte["comparable"]]
    autres = carte[~carte["comparable"]]

    bornes = [0, *config.BORNES_PART_CADRES_IRIS, 100]
    demi_cote = config.ZOOM_IRIS_KM * 1000
    ouest, sud = centre.x - demi_cote, centre.y - demi_cote
    fig, axes = plt.subplots(2, 2, figsize=(13, 13))
    for colonne, annee in enumerate((2011, 2022)):
        # Borne basse incluse, comme dans la légende
        classe = pd.cut(
            comparables[f"part_cadres_1564_{annee}"] * 100, bornes, right=False, labels=False
        )
        assert classe.notna().all(), f"Part hors des classes en {annee}."
        couleurs = [config.COULEURS_PART_CADRES_IRIS[int(rang)] for rang in classe]
        aire, zoom = axes[0, colonne], axes[1, colonne]
        for ax, epaisseur in ((aire, 0.2), (zoom, 0.6)):
            autres.plot(
                ax=ax,
                color=config.COULEUR_IRIS_NON_COMPARABLE,
                hatch="////",
                edgecolor=config.COULEUR_LIAISON,
                linewidth=epaisseur,
            )
            comparables.plot(ax=ax, color=couleurs, edgecolor="white", linewidth=epaisseur)
            ax.set_axis_off()
        aire.add_patch(
            Rectangle(
                (ouest, sud),
                2 * demi_cote,
                2 * demi_cote,
                fill=False,
                edgecolor=config.COULEUR_TEXTE,
                linewidth=1,
            )
        )
        zoom.set_xlim(ouest, ouest + 2 * demi_cote)
        zoom.set_ylim(sud, sud + 2 * demi_cote)
        aire.set_title(f"{annee}, aire entière", loc="left", fontsize=11)
        zoom.set_title(
            f"{annee}, ville-centre ({2 * config.ZOOM_IRIS_KM} km de côté)", loc="left", fontsize=11
        )

    libelles = [f"moins de {bornes[1]} %"]
    libelles += [f"{bas} à {haut} %" for bas, haut in itertools.pairwise(bornes[1:-1])]
    libelles.append(f"{bornes[-2]} % ou plus")
    poignees = [
        Patch(facecolor=couleur, edgecolor="white", label=libelle)
        for couleur, libelle in zip(config.COULEURS_PART_CADRES_IRIS, libelles, strict=True)
    ]
    poignees.append(
        Patch(
            facecolor=config.COULEUR_IRIS_NON_COMPARABLE,
            hatch="////",
            edgecolor=config.COULEUR_LIAISON,
            label="IRIS non comparable",
        )
    )
    fig.legend(handles=poignees, loc="center right", frameon=False, fontsize=9)
    fig.suptitle(titre, fontsize=13, x=0.01, ha="left")
    fig.text(
        0.01,
        0.01,
        "Part des cadres et professions intellectuelles supérieures parmi les actifs de 15 à 64 "
        "ans (occupés et chômeurs ayant déjà travaillé), et non de 25 à 54 ans comme dans le reste "
        "du rapport : les bases IRIS ne croisent pas\ncette tranche avec la catégorie "
        "socioprofessionnelle. Non comparable : code IRIS absent en 2011, commune qui en a absorbé "
        f"une autre depuis 2013, ou moins de {config.SEUIL_ACTIFS_IRIS} actifs à une date. "
        "Exploitation complémentaire (échantillon).\nSources : Insee, recensements 2011 et 2022, "
        "bases infracommunales « Activité des résidents » ; contours IRIS de l'IGN (cartiflette, "
        f"COG {config.ANNEE_COG}).",
        fontsize=8,
        color=config.COULEUR_TEXTE,
    )
    fig.tight_layout(rect=(0, 0.05, 0.85, 0.97))
    # Fermée, la figure n'est affichée qu'une fois par un notebook, avec sa valeur de retour
    plt.close(fig)
    return fig
