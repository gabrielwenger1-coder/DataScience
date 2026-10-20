"""Figures du rapport : une fonction par figure, avec les mêmes couleurs de secteur."""

import html
import itertools

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from folium.plugins import TimeSliderChoropleth
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from cadres_lycees import config


def fig1(profil: pd.DataFrame, lycees: gpd.GeoDataFrame, titre: str) -> Figure:
    """Fig. 1 : pour chaque aire, la prévalence du privé sous contrat et la composition sociale.

    À gauche, la part du privé en nombre de lycées et en candidats au bac ; à droite, l'IPS de
    chaque lycée par secteur, avec la moyenne simple du secteur et l'écart privé moins public :
    les deux dimensions du critère (b) du choix des aires (PLAN §2.2, §5.1). `profil` vient de
    `analyse.profil_aires`, `lycees` de `nettoyage.lycees_geo` ; `titre` est le message de la
    figure, écrit par le groupe (PLAN §6). Les aires sont triées par écart d'IPS, le plus fort
    en haut.
    """
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
        f"{n_sans_ips} lycées sans IPS.\nSources : annuaire de l'éducation, DEPP (IPS, IVAL), "
        "Insee (aires d'attraction des villes 2020), IGN.",
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
        geometry=_contours_simplifies(communes),
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

    carte = _carte_vierge(affichage)
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

    classes = "".join(
        f"<div>{_pastille(couleur, rond=False)}{libelle}</div>"
        for couleur, libelle in zip(config.COULEURS_DISTANCE, _libelles_distance(), strict=True)
    )
    points = "".join(
        f"<div>{_pastille(config.COULEURS_SECTEURS[secteur], rond=True)}"
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
        "<b>Distance au lycée privé sous contrat le plus proche</b>"
        f"{classes}{points}"
        f"<p style='font-size:10px'>{note}</p><p style='font-size:10px'>{source}</p>"
    )
    _ajouter_titre_et_legende(carte, titre, legende)
    return carte


def carte_croissance_population(
    communes: gpd.GeoDataFrame, croissance: pd.DataFrame, titre: str
) -> folium.Map:
    """Carte à curseur : taux de variation annuel moyen de la population, période par période.

    `communes` vient de `pipeline.construire_base`, `croissance` de
    `nettoyage.croissance_population`. Le curseur parcourt les périodes entre deux recensements,
    de 1968-1975 à 2016-2022, et affiche l'année du recensement qui clôt la période. Au survol,
    une commune donne son taux pour toutes les périodes. `titre` est le message de la carte,
    écrit par le groupe (PLAN §6).
    """
    assert communes.crs == config.CRS_CALCUL, (
        f"Communes en {communes.crs} : EPSG:{config.CRS_CALCUL} attendu."
    )
    # L'index devient l'identifiant de chaque commune dans le GeoJSON, celui auquel le curseur
    # rattache les couleurs
    affichage = (
        gpd.GeoDataFrame(
            {
                "code_commune": communes["code_commune"],
                "nom_commune": communes["nom_commune"],
                "aire": communes["aire"],
            },
            geometry=_contours_simplifies(communes),
        )
        .set_index("code_commune")
        .to_crs(config.CRS_CARTES)
    )
    taux = croissance.loc[affichage.index]

    bornes = [float("-inf"), *config.BORNES_CROISSANCE, float("inf")]
    annees_fin = list(config.COLONNES_POPULATION)[1:]
    styles = {code: {} for code in affichage.index}
    for periode, fin in zip(taux.columns, annees_fin, strict=True):
        # Le 1er juillet, et non le 1er janvier : un navigateur à l'ouest de Greenwich afficherait
        # sinon l'année précédente
        horodatage = str(int(pd.Timestamp(year=fin, month=7, day=1).timestamp()))
        # Borne basse incluse : un taux de 0,2 % par an est une hausse, pas une stabilité
        classe = pd.cut(taux[periode], bornes, right=False, labels=False)
        assert classe.notna().all(), f"Taux hors des classes, période {periode}."
        for code, rang in classe.items():
            # Pour ce calque, "color" et "opacity" sont la couleur et l'opacité du remplissage
            styles[code][horodatage] = {
                "color": config.COULEURS_CROISSANCE[int(rang)],
                "opacity": 0.85,
            }
        # Deux décimales : à une seule, un taux de −0,23 s'afficherait « −0,2 » avec la couleur
        # de la classe des baisses
        affichage[periode] = taux[periode].map(
            lambda valeur: _a_la_francaise(f"{valeur:+.2f} % par an")
        )

    carte = _carte_vierge(affichage)
    # Le curseur doit être ajouté avant les autres calques tracés : à son ajout, le gabarit de
    # folium 0.20 redessine tous les tracés déjà présents (liseré blanc en pointillé,
    # remplissage transparent), ce qui effacerait les limites ajoutées avant lui
    curseur = TimeSliderChoropleth(
        affichage[["geometry"]].to_json(), styledict=styles, date_options="YYYY", control=False
    )
    curseur.add_to(carte)
    # Le curseur ne sait pas afficher d'infobulle : une copie transparente des communes, posée
    # au-dessus, donne les taux au survol. Ses limites grises, tracées par-dessus le liseré du
    # curseur, font aussi voir les communes stables, presque blanches, sur le fond de carte
    folium.GeoJson(
        affichage,
        style_function=lambda _: {
            "fillOpacity": 0,
            "color": config.COULEUR_LIAISON,
            "weight": 0.6,
        },
        highlight_function=lambda _: {"color": config.COULEUR_TEXTE, "weight": 2},
        tooltip=folium.GeoJsonTooltip(
            fields=["nom_commune", *taux.columns],
            aliases=["Commune", *[f"Taux annuel {periode}" for periode in taux.columns]],
        ),
        control=False,
    ).add_to(carte)
    folium.GeoJson(
        affichage[["aire", "geometry"]].dissolve("aire").reset_index(),
        style_function=lambda _: {"fill": False, "color": config.COULEUR_TEXTE, "weight": 2},
        control=False,
    ).add_to(carte)
    folium.LayerControl(collapsed=True).add_to(carte)

    # Le gabarit de folium 0.20 insère le curseur au-dessus de la carte, dans un bloc nommé
    # « slider_ » suivi du nom du calque : il est ramené en bas à droite, à l'opposé de la légende
    style_curseur = (
        f"<style>#slider_{curseur.get_name()}{{position:fixed;bottom:28px;right:12px;"
        "z-index:1000;background:white;padding:6px 10px;font:14px sans-serif;"
        f"color:{config.COULEUR_TEXTE}}}#slider_{curseur.get_name()} input{{width:220px}}</style>"
    )
    carte.get_root().header.add_child(folium.Element(style_curseur))
    classes = "".join(
        f"<div>{_pastille(couleur, rond=False)}{libelle}</div>"
        for couleur, libelle in zip(config.COULEURS_CROISSANCE, _libelles_croissance(), strict=True)
    )
    note = (
        "Taux de variation annuel moyen de la population entre deux recensements, calculé sur "
        "l'écart des millésimes ; borne basse de chaque classe incluse. L'année du curseur est "
        "celle du recensement qui clôt la période (1975 : de 1968 à 1975). Population sans "
        "doubles comptes jusqu'en 1999, municipale ensuite : 1999-2006 est la période la moins "
        f"comparable. Communes du COG {config.ANNEE_COG} (arrondissements à Lyon)."
    )
    source = "Source : Insee, séries historiques du recensement de la population (1968-2022)."
    legende = (
        "<b>Évolution de la population, en % par an</b>"
        f"{classes}<p style='font-size:10px'>{note}</p><p style='font-size:10px'>{source}</p>"
    )
    _ajouter_titre_et_legende(carte, titre, legende)
    return carte


def _libelles_croissance() -> list[str]:
    """Libellés des classes de `config.BORNES_CROISSANCE`, de la plus forte baisse à la hausse."""
    bornes = [_a_la_francaise(f"{taux:+g} %") for taux in config.BORNES_CROISSANCE]
    libelles = [f"moins de {bornes[0]}"]
    libelles += [f"{bas} à {haut}" for bas, haut in itertools.pairwise(bornes)]
    libelles.append(f"{bornes[-1]} ou plus")
    return libelles


def _a_la_francaise(nombre: str) -> str:
    """Remplace le point décimal par une virgule et le tiret par un vrai signe moins."""
    return nombre.replace(".", ",").replace("-", "−")


def _contours_simplifies(communes: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """Renvoie les contours des communes simplifiés pour l'affichage, sans trou entre voisines."""
    # La simplification ne garde les frontières partagées que si les contours, sans trou ni
    # chevauchement, forment une couverture valide
    assert communes.geometry.is_valid_coverage(), "Les contours ne forment pas une couverture."
    return communes.geometry.simplify_coverage(config.SIMPLIFICATION_CARTE_M)


def _carte_vierge(affichage: gpd.GeoDataFrame) -> folium.Map:
    """Renvoie une carte cadrée sur `affichage` (en WGS84), avec les fonds de `FONDS_CARTE`."""
    carte = folium.Map(tiles=None, control_scale=True)
    for rang, (nom, fournisseur) in enumerate(config.FONDS_CARTE.items()):
        # Le premier fond s'affiche, les autres se choisissent dans le sélecteur de couches
        folium.TileLayer(fournisseur, name=nom, show=(rang == 0)).add_to(carte)
    ouest, sud, est, nord = affichage.total_bounds
    carte.fit_bounds([[sud, ouest], [nord, est]])
    return carte


def _pastille(couleur: str, rond: bool) -> str:
    """Renvoie un petit carré, ou un disque, de la couleur donnée, pour une légende HTML."""
    arrondi = "50%" if rond else "0"
    return (
        '<span style="display:inline-block;width:10px;height:10px;margin-right:6px;'
        f"border:1px solid {config.COULEUR_LIAISON};border-radius:{arrondi};"
        f'background:{couleur}"></span>'
    )


def _ajouter_titre_et_legende(carte: folium.Map, titre: str, legende: str) -> None:
    """Fixe le titre en haut à gauche de la carte, et la légende (HTML) en bas à gauche."""
    # folium n'a pas de légende par classes : elle est écrite en HTML, fixée au-dessus du fond
    boite = (
        '<div style="position:fixed;bottom:28px;left:12px;z-index:1000;background:white;'
        f'padding:8px;font:11px sans-serif;color:{config.COULEUR_TEXTE};width:250px">'
        f"{legende}</div>"
    )
    carte.get_root().html.add_child(folium.Element(boite))
    # À droite des boutons de zoom
    entete = (
        '<div style="position:fixed;top:10px;left:56px;z-index:1000;background:white;'
        f'padding:6px 10px;font:bold 14px sans-serif;color:{config.COULEUR_TEXTE};max-width:60%">'
        f"{html.escape(titre)}</div>"
    )
    carte.get_root().html.add_child(folium.Element(entete))
