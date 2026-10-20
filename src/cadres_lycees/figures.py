"""Figures du rapport : une fonction par figure, avec les mêmes couleurs de secteur."""

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
