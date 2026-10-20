"""Construction de la base communale et des paires de communes contiguës (PLAN §4, étape G)."""

import geopandas as gpd
import pandas as pd

from cadres_lycees import accessibilite, collecte, config, geo, nettoyage, stockage


def construire_base(
    aires: dict[str, str],
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, pd.DataFrame]:
    """Construit la base communale, les lycées et les paires de communes contiguës des aires.

    `aires` associe le nom de l'aire à son code AAV2020 (par exemple `config.AIRES_CANDIDATES`).
    La base a une ligne par commune du référentiel (arrondissements à Lyon) : accès aux lycées
    privés et publics (§2.4), nombre de lycées et IVAL moyenne dans chaque rayon, population,
    densité et exposition 0/1. Les sources sont lues dans leurs copies contrôlées (§7). Écrit
    `config.CHEMIN_BASE` et `config.CHEMIN_PAIRES`, décrits dans `docs/dictionnaire_variables.md`,
    et renvoie (base, lycées, paires).
    """
    referentiel = geo.referentiel_communes(aires)
    lycees = nettoyage.lycees_geo(
        collecte.annuaire_education(), collecte.ips_lycees(), collecte.ival_lycees(), referentiel
    )
    acces_tous_lycees = accessibilite.indicateurs(
        referentiel, lycees, "lyc", attribut="ival", poids="poids_ival"
    )
    blocs = [
        accessibilite.indicateurs(referentiel, lycees[lycees["secteur"] == "prive"], "lyc_prive"),
        accessibilite.indicateurs(referentiel, lycees[lycees["secteur"] == "public"], "lyc_public"),
        # Tous secteurs : le nombre de lycées et l'IVAL moyenne servent à H3 (§5.5) ; la distance
        # au plus proche, tous secteurs confondus, n'entre dans aucune analyse du plan
        acces_tous_lycees.drop(columns="dist_lyc_min"),
        nettoyage.population(collecte.serie_historique_rp2022(), referentiel),
    ]
    base = referentiel
    for bloc in blocs:
        base = base.merge(
            bloc, left_on="code_commune", right_index=True, how="left", validate="one_to_one"
        )
    # Une commune absente d'un bloc y aurait des valeurs manquantes. Seule l'IVAL moyenne peut
    # manquer : une commune sans lycée avec IVAL dans le rayon
    colonnes_obligatoires = [col for col in base.columns if not col.startswith("ival_moy_")]
    incompletes = [col for col in colonnes_obligatoires if base[col].isna().any()]
    assert not incompletes, f"Valeurs manquantes dans {incompletes}."

    for rayon in config.RAYONS_KM:
        # Exposition 0/1, pour compter les paires de statut différent (§5.2, A6). En entier :
        # pandas refuse la différence de deux booléens, que calcule `geo.paires_contigues`
        expose = base[f"n_lyc_prive_{rayon}km"] > 0
        base[f"expose_lyc_prive_{rayon}km"] = expose.astype(int)

    paires = geo.paires_contigues(base, list(config.VARIABLES_PAIRES))
    stockage.ecrire_parquet(base, config.CHEMIN_BASE)
    stockage.ecrire_parquet(paires, config.CHEMIN_PAIRES)
    return base, lycees, paires
