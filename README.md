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

Le rapport est `rapport.ipynb`, publié avec Quarto.

### Stockage des données

Les données ne sont pas dans Git. `stockage.py` les lit et les écrit :

- sur le S3 du SSPCloud si `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY` sont définies (c'est le cas sur un service SSPCloud). Il faut alors définir le nom du bucket : `export BUCKET_S3=<nom du bucket>`. Les fichiers sont dans `s3://<bucket>/projet-cadres-lycees/`, et l'adresse du serveur est lue par s3fs dans `AWS_ENDPOINT_URL`, que le SSPCloud définit aussi ;
- sinon dans le dossier local `data/`.

## Organisation

- `src/cadres_lycees/` : le code du pipeline, un module par étape (voir PLAN §7).
- `tests/` : les tests des calculs critiques.
- `notebooks/exploration/` : brouillons individuels, jamais rendus.
- `docs/` : le plan, les notes sur les sources de données et le dictionnaire des variables.
