"""Test de `analyse.cellules_anneaux` sur des communes jouets (PLAN §5.2, amendement A6).

Les attendus sont calculés à la main avec les règles fixées par A6 : anneaux de départ
`config.ANNEAUX_KM` (0, 5, 10, 20, 30 km), au moins `config.EFFECTIF_MIN_GROUPE` (15) communes
exposées et 15 non exposées par cellule, écart des distances moyennes au centre d'au plus
`config.ECART_DIST_MAX_KM` (2 km).
"""

import math

import pandas as pd

from cadres_lycees import analyse, config

# Le rayon de 10 km et non 5 : une fonction qui lirait toujours la colonne à 5 km échouerait.
RAYON = 10
EXPOSITION = f"expose_lyc_prive_{RAYON}km"
COLONNES = [
    "aire",
    "bas_km",
    "haut_km",
    "n_exposees",
    "n_non_exposees",
    "dist_moy_exposees",
    "dist_moy_non_exposees",
    "estimable",
]


def groupe(aire: str, distance: float, exposees: int = 0, non_exposees: int = 0) -> pd.DataFrame:
    """Communes jouets d'une aire, toutes à `distance` km du centre."""
    return pd.DataFrame(
        {
            "aire": aire,
            "dist_centre_km": distance,
            EXPOSITION: [1] * exposees + [0] * non_exposees,
        }
    )


def test_fusion_des_anneaux_puis_equilibre() -> None:
    """Fusions dans l'ordre du plan, équilibre vérifié après fusion, aire non estimable.

    Aire A, anneaux de départ (exposées, non exposées ; total) :
    [0, 5) (15, 15 ; 30), [5, 10) (1, 0 ; 1), [10, 20) (25, 5 ; 30), [20, 30) (0, 5 ; 5),
    [30, inf) (15, 15 ; 30). En échec au départ : [5, 10), [10, 20) et [20, 30).
    1. [5, 10), la plus proche du centre : voisines à 30 et 30, égalité, donc la plus proche
       du centre, [0, 5). Résultat [0, 10) (16, 15 ; 31).
    2. [10, 20) : voisines [0, 10) (31) et [20, 30) (5), donc [20, 30). Résultat [10, 30)
       (25, 10 ; 35), encore en échec.
    3. [10, 30) : voisines [0, 10) (31) et [30, inf) (30), donc [30, inf). Résultat [10, inf)
       (40, 25 ; 65).
    Toujours fusionner vers le centre, toujours vers l'extérieur, départager l'égalité vers
    l'extérieur ou ne pas refusionner [10, 30) donnerait d'autres cellules.
    """
    seuil = config.EFFECTIF_MIN_GROUPE
    borne_5_km = config.ANNEAUX_KM[1]
    communes = pd.concat(
        [
            groupe("A", 1.0, exposees=seuil),
            # 1,25 km est la moyenne des 16 exposées de [0, 10) : écart de 2 km pile.
            groupe("A", 1.25 + config.ECART_DIST_MAX_KM, non_exposees=seuil),
            # Borne haute exclue : à 5 km pile, la commune est dans [5, 10). Comptée dans
            # [0, 5), elle romprait l'égalité 30 = 30 de l'étape 1.
            groupe("A", borne_5_km, exposees=1),
            groupe("A", 15.0, exposees=25, non_exposees=5),
            groupe("A", 25.0, non_exposees=5),
            groupe("A", 35.0, exposees=seuil, non_exposees=seuil),
            groupe("B", 2.0, exposees=10, non_exposees=5),
            groupe("B", 40.0, exposees=10, non_exposees=5),
        ],
        ignore_index=True,
    )

    cellules = analyse.cellules_anneaux(communes, RAYON)

    obtenu = cellules[COLONNES].sort_values(["aire", "bas_km"]).reset_index(drop=True)
    attendu = pd.DataFrame(
        [
            # (15 × 1 + 5) / 16 = 1,25 contre 3,25 : écart de 2 km, au plus 2, estimable.
            ("A", 0, 10, 16, 15, 1.25, 3.25, True),
            # 40 et 25 communes, mais (25 × 15 + 15 × 35) / 40 = 22,5 contre
            # (5 × 15 + 5 × 25 + 15 × 35) / 25 = 29 : écart de 6,5 km, non estimable,
            # sans nouvelle fusion avec [0, 10).
            ("A", 10, math.inf, 40, 25, 22.5, 29.0, False),
            # Toute l'aire ne compte que 10 non exposées : une seule ligne, non estimable,
            # même si l'écart est nul ((10 × 2 + 10 × 40) / 20 = (5 × 2 + 5 × 40) / 10 = 21).
            ("B", 0, math.inf, 20, 10, 21.0, 21.0, False),
        ],
        columns=COLONNES,
    )
    pd.testing.assert_frame_equal(obtenu, attendu, check_dtype=False)
