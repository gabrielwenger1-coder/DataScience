# Lycées et géographie des cadres : guide de l'équipe

Projet du cours « Python pour la data science » (ENSAE). La question : dans les aires urbaines de Nantes, Lyon et Strasbourg, les communes proches d'un lycée privé, ou d'un lycée qui fait mieux réussir ses élèves, ont-elles plus de cadres que leurs voisines ?

Ce guide sert à se mettre en route : installer le projet, obtenir les données, savoir où est quoi et comment travailler à plusieurs. Un README pour le correcteur le remplacera avant le rendu.

## Où est le travail

`main` est encore presque vide : tout le travail est dans trois pull requests, chacune construite sur la précédente. On les fusionne dans cet ordre.

| PR | Branche | Contenu | Relue par |
|---|---|---|---|
| [#2](https://github.com/gabrielwenger1-coder/DataScience/pull/2) | `feat/tableau-support` | Les données, le calcul de l'accès aux lycées, les paires de communes voisines, le choix des trois aires, le plan | R2 et R3 |
| [#5](https://github.com/gabrielwenger1-coder/DataScience/pull/5) | `feat/site-quarto` | Tout #2, plus le site du rapport, les figures 1 et 3, la carte des cadres par quartier, la méthode en une page | R3 |
| [#6](https://github.com/gabrielwenger1-coder/DataScience/pull/6) | `feat/h1-paires` | Tout #5, plus le calcul de la part de cadres et celui de la première hypothèse | R2 |

Pour travailler sur la version la plus complète **sans données sur les cadres**, prenez `feat/site-quarto`.

## Mettre en place le projet

Sur le SSPCloud, ouvrez un service VSCode-python ou Jupyter-python. `uv` (gestionnaire de paquets) et `quarto` (site du rapport) y sont déjà installés ; ailleurs, installez `uv` avec `curl -LsSf https://astral.sh/uv/install.sh | sh`.

```bash
git clone https://github.com/gabrielwenger1-coder/DataScience.git
cd DataScience
git switch feat/site-quarto       # ou la branche de la PR que vous relisez
uv sync                           # installe Python 3.13 et les paquets figés dans uv.lock
uv run pre-commit install         # nettoie les notebooks et vérifie le code à chaque commit
uv run pytest                     # les tests doivent passer
```

Lancez toujours Python avec `uv run` (par exemple `uv run python`) : c'est l'environnement du projet, où le paquet `cadres_lycees` est installé. Pour ouvrir les notebooks dans Jupyter, enregistrez une fois ce noyau avec `uv run python -m ipykernel install --user --name cadres-lycees`, puis choisissez « cadres-lycees » dans le notebook. Dans VSCode, choisissez l'interpréteur `.venv/bin/python`.

## Obtenir les données

Il n'y a rien à télécharger à la main. Au premier lancement, le code récupère chaque fichier, vérifie son empreinte (sha256) et le garde dans le dossier `data/`, ignoré par Git :

- les fichiers de l'Insee (aires urbaines, recensement) sont pris sur le site de l'Insee ;
- les sources qui changent d'un jour à l'autre (annuaire des lycées, indice social, valeur ajoutée des lycées, contours des communes) sont prises dans des copies datées : d'abord le dossier public du projet sur le S3, puis, s'il ne répond pas, la [release `donnees-20261020`](https://github.com/gabrielwenger1-coder/DataScience/releases/tag/donnees-20261020). Un avertissement signale ce repli : c'est normal.

Pour construire la base communale (une ligne par commune des trois aires), environ 30 secondes la première fois :

```bash
uv run python -c "from cadres_lycees import config, pipeline; pipeline.construire_base(config.AIRES_RETENUES)"
```

Elle s'écrit dans `data/final/base_communale.parquet` et `data/final/paires.parquet`. Les variables sont décrites dans `docs/dictionnaire_variables.md`.

Un avertissement « Variables d'environnement manquantes : BUCKET_S3 » est normal : les données restent dans `data/`. Pour les ranger dans votre propre espace S3 du SSPCloud, faites `export BUCKET_S3=<votre identifiant SSPCloud>` avant de lancer Python.

Pour voir le site du rapport : `uv run quarto render`, puis ouvrez `_site/index.html`.

## Une règle à respecter : pas de chiffres sur les cadres pour l'instant

Le plan veut que toutes les règles de calcul soient écrites avant de regarder la part de cadres, pour ne pas choisir après coup la méthode qui donne le résultat attendu. Elles seront figées par l'étiquette Git `plan-fige`, posée juste après la fusion de la PR #2. D'ici là, sur la branche `feat/h1-paires`, ne lancez ni la construction de la base, ni `rapport.ipynb`, ni `quarto render` : c'est là que se calcule la part de cadres. Les tests (`uv run pytest`) n'utilisent que des données inventées et peuvent tourner.

## Où est quoi

| Chemin | Contenu |
|---|---|
| `src/cadres_lycees/` | Le code, un module par étape : `collecte` (téléchargements), `nettoyage`, `geo` (communes, distances, voisines), `accessibilite` (accès aux lycées), `analyse` (comparaisons), `figures`, `pipeline` (enchaîne tout), `config` (toutes les constantes, URL et chemins), `stockage` (lecture et écriture des fichiers) |
| `rapport.ipynb` | Le rapport : il n'appelle que des fonctions de `src/` |
| `tests/` | Les tests des calculs qui pourraient être faux sans le dire (accès aux lycées, communes voisines, analyse) |
| `docs/PLAN.md` | Le plan complet : questions, règles de calcul, calendrier, et le journal daté de chaque décision (§13) |
| `docs/tableau_support.md` | Les chiffres qui ont servi à choisir les trois aires |
| `docs/exploration_sources.md` | Ce qu'on sait de chaque source : adresses, colonnes, pièges |
| `notebooks/exploration/` | Brouillons personnels, nommés avec vos initiales, jamais rendus |

## Comment travailler

1. Partez de la branche sur laquelle votre travail s'appuie, et créez la vôtre : `git switch -c feat/<sujet>`.
2. Commitez souvent, avec des messages courts à l'impératif (« Ajoute la comparaison par anneaux »).
3. Ouvrez une pull request ; un autre membre la relit et laisse des commentaires.
4. Fusionnez avec « Create a merge commit » (ni squash, ni rebase : le plan cite des numéros de commit).
5. Personne ne pousse directement sur `main`.

Toutes les constantes vont dans `src/cadres_lycees/config.py`. Les notebooks sont commités sans leurs sorties, ce que le pre-commit fait tout seul. Chacun commite le code qu'il devra expliquer à l'oral.

Le dossier `.claude/` règle l'assistant de code utilisé pour une partie du projet (consignes, agents de relecture, garde-fous). Vous n'en avez pas besoin pour travailler.

Une question, un blocage : écrivez à Giulio.
