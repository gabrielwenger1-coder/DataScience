# Lycées et géographie des cadres dans trois aires urbaines de province

Projet du cours « Python pour la data science » (ENSAE), rendu le 24 novembre 2026.

## Question

Dans des aires urbaines de province aux traditions scolaires contrastées, les communes offrant un meilleur accès à des lycées privés ou à forte valeur ajoutée concentrent-elles davantage de cadres que leurs voisines, et ce lien résiste-t-il face aux autres infrastructures ?

Le plan complet est dans [`docs/PLAN.md`](docs/PLAN.md).

## Résultats clés

À compléter par le groupe une fois l'analyse terminée.

## Reproduire le projet

Python 3.13 et [uv](https://docs.astral.sh/uv/) sont nécessaires.

```bash
uv sync                          # installe les dépendances figées dans uv.lock
uv run pre-commit install        # active nb-clean et ruff avant chaque commit
uv run pytest                    # lance les tests
```

Le rapport est `rapport.ipynb` (pour l'instant la Fig. 1 et la Fig. 3), qui sera publié avec Quarto. Sur un compte neuf, les données sont téléchargées depuis les copies gelées publiques décrites ci-dessous, puis gardées dans `data/`.

### Stockage des données

Les données ne sont pas dans Git. `stockage.py` les lit et les écrit :

- sur le S3 du SSPCloud si `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (définies sur un service SSPCloud) et `BUCKET_S3` sont définies. Le nom du bucket dépend du compte : `export BUCKET_S3=<nom du bucket>` (un `export` fait dans un terminal n'est pas vu par un noyau Jupyter déjà lancé). Les fichiers sont dans `s3://<bucket>/projet-cadres-lycees/`, et l'adresse du serveur est lue par s3fs dans `AWS_ENDPOINT_URL`, que le SSPCloud définit aussi ;
- sinon dans le dossier local `data/`, avec un avertissement (c'est le cas d'un compte qui n'a pas défini `BUCKET_S3`).

### Copies gelées des données

Les sources qui changent sans prévenir sont lues dans une copie datée, jamais directement à leur API. Chaque copie est cherchée dans le dossier public `https://minio.lab.sspcloud.fr/gfogato/projet-cadres-lycees/raw/`, puis, si elle y manque ou diffère, dans la release GitHub [`donnees-20261020`](https://github.com/gabrielwenger1-coder/DataScience/releases/tag/donnees-20261020) du dépôt, avec un avertissement. Le code échoue si aucune des deux ne fournit un fichier au `sha256` attendu, et il recontrôle le `sha256` à chaque lecture d'une copie déjà téléchargée.

| Copie | Date | Origine | `sha256` |
|---|---|---|---|
| `annuaire_education_20261013.parquet` | 13/10/2026 | https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/exports/parquet | `2c493f152bc8fc682aa8b1f063392015941bcff36bae2ae59a4d1a1e6334e94a` |
| `ips_lycees_20261013.csv` | 13/10/2026 | https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-lycees-ap2023/exports/csv | `31b2aafd8fb4597608c55f8f78f7144444a350df795111a651fb5222ee9c8aa7` |
| `ival_lycees_gt_20261020.csv` | 20/10/2026 | https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-indicateurs-de-resultat-des-lycees-gt_v2/exports/csv | `6ab77b391e3405f5157bb942d4548d5f1cfbacd94e76dd52b93db9b370de8658` |
| `contours_aav_<code>_20261013.parquet` | 13/10/2026 | `cartiflette==0.4.0`, contours des communes et arrondissements par aire, COG 2025, sans simplification | `002` : `5fc255ef5f92c540c5037f793c15c24007642c7cdce256a1e4f47d516176f231`<br>`004` : `6ff1e4bc0675ab567b7af3eb506774c0740ab855c5f333c66ee6b8fe1eb89982`<br>`005` : `c42afd4910a9a6907c54e2f8d476b8a4b6db3630bf9ffdff7b41cedf8a3b2c6e`<br>`006` : `6e0cb9a94a69887fd123a2d57c49068aa25b207da9541813652c00f1b2930c28`<br>`008` : `54665ed725b9ae364166d6dc76cd09b71b8e42397916e6fe564d8f0308786e59`<br>`010` : `454d27768198bb48be5882987f3aa36f88902add34bf443dff0cd37cc8be7790`<br>`013` : `c846f8d895d3121435037f5c04054a9e2275bb95e2de1791cae61498550b4cec`<br>`014` : `a1d13c20cc9565de3e2b3bb78b8d020076bae7c2a94ac2648d7aa96aa0699357` |

Les fichiers de l'Insee (zonage en aires d'attraction, série historique du recensement 2022) sont permanents : ils sont lus à leur URL d'origine, avec le même contrôle du `sha256` (voir `src/cadres_lycees/config.py`).

**Refaire un gel** (seulement si le groupe décide de changer de copie, à journaliser au plan) :

```python
from cadres_lycees import collecte

collecte.geler_annuaire("raw/annuaire_education_AAAAMMJJ.parquet")  # renvoie le sha256
collecte.geler_contours("013", "raw/contours_aav_013_AAAAMMJJ.parquet")
```

Les deux fonctions refusent d'écraser un chemin existant. Il faut ensuite reporter le chemin et le `sha256` dans `config.py`, publier le fichier aux deux adresses ci-dessus et mettre à jour ce tableau.

## Organisation

- `src/cadres_lycees/` : le code du pipeline, un module par étape (voir PLAN §7).
- `tests/` : les tests des calculs critiques (accessibilité et paires de communes contiguës).
- `notebooks/exploration/` : brouillons individuels, jamais rendus.
- `docs/` : le plan, les notes sur les sources de données et le [dictionnaire des variables](docs/dictionnaire_variables.md) de la base communale (`pipeline.construire_base`).
