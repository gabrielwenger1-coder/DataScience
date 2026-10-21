Python pour la data science · ENSAE

# Projet cadres et lycées au 21 octobre

Ce qui est fait, ce qu'il reste à faire, et ce que chacun doit faire maintenant. Lecture : 5 minutes.

## En une minute

- **La question** : dans les régions urbaines de Nantes, Lyon et Strasbourg, les communes proches d'un lycée privé, ou d'un lycée qui fait mieux réussir ses élèves, ont-elles plus de cadres que leurs voisines ?
- **Comment on y répond** : on compare des communes qui se touchent, à distance égale du centre-ville et à densité égale. Le résumé d'une page est dans le [README](https://github.com/gabrielwenger1-coder/DataScience/blob/feat/site-quarto/README.md#méthode-en-bref).
- **Où on en est** : les données et le code de la première question sont prêts. On n'a encore regardé aucun chiffre sur les cadres, et c'est voulu : toutes les règles de calcul doivent être écrites avant, pour ne pas choisir après coup la méthode qui donne le résultat attendu.
- **Le plus urgent** : relire les PR, puis que chacun écrive et commite sa partie. Aujourd'hui, tout le code est sous un seul nom, et la grille de notation le pénalise.

## Les quatre questions du projet

Le plan les appelle H1 à H4.

H1 · principale

Entre deux communes voisines, celle qui est plus proche d'un lycée privé a-t-elle plus de cadres ?

H2

Ce lien est-il plus faible à Nantes, où le privé est plus courant ?

H3

Est-ce la qualité des lycées proches, plus que leur nombre, qui va avec la hausse des cadres entre 2011 et 2022 ?

H4

Les lycées comptent-ils plus que les gares ou les médecins ?

| Mot | Ce que ça veut dire |
| --- | --- |
| Aire | Une ville et les communes autour dont les habitants y travaillent (découpage de l'Insee). |
| IRIS | Un quartier au sens de l'Insee, environ 2 000 habitants. C'est la plus petite échelle publiée sur les cadres. |
| IPS | Indice de position sociale des élèves d'un lycée : plus il est haut, plus les familles sont favorisées. |
| IVAL | Valeur ajoutée d'un lycée : ce qu'il fait réussir de plus (ou de moins) que prévu, vu ses élèves. |
| Figer le plan | Poser l'étiquette Git `plan-fige` juste après la fusion de la PR #2. On ne regarde les chiffres sur les cadres qu'après. |

## Ce qui est fait

| Élément | État | Où le voir |
| --- | --- | --- |
| Les données : lycées et leur statut public ou privé, IPS, IVAL, population, contours des communes, distance de chaque commune aux lycées, paires de communes voisines | fait | PR #2 |
| N'importe qui peut relancer le projet : les copies des données sont publiées, la base se reconstruit en 24 secondes sur un compte neuf | fait | release GitHub `donnees-20261020` |
| Le choix des trois aires, fait avant de regarder les cadres | fait | `docs/tableau_support.md` |
| Les règles de calcul et la façon de conclure, écrites à l'avance | fait | `docs/PLAN.md` |
| La mesure de la qualité des lycées est assez fiable pour H3 (0,61, pour un seuil fixé à 0,5) | fait | journal du plan |
| Le site du rapport, avec deux figures : le poids du privé dans chaque aire, et des cartes de l'accès aux lycées | fait | PR #5 |
| La carte des cadres par quartier en 2011 et en 2022 | code prêt | PR #5, essayée sur Rennes |
| Le calcul de la part de cadres en 2011 et en 2022 | code prêt, pas lancé | PR #6 |
| Le calcul principal de H1, sur les communes voisines | code prêt, pas lancé | PR #6 |

## Ce qui reste à faire

1. Fusionner les PR, figer le plan, puis lancer le calcul de la part de cadres : ce seront nos premiers chiffres.
2. H1 : la seconde comparaison, par anneaux de distance au centre-ville, puis la règle qui dit si l'hypothèse est confirmée ou non.
3. H3 : le calcul du lien entre la qualité des lycées et la hausse des cadres.
4. H4 : la distance aux gares et l'accès aux médecins.
5. Les figures qui manquent (cinq sur sept) et un tableau qui vérifie que les résultats tiennent quand on change un réglage.
6. Tout le texte du rapport : aucune phrase n'est encore écrite, et c'est à nous de l'écrire.
7. Une section du README qui explique honnêtement comment on a utilisé l'assistant de code.

### Une décision à prendre avant de figer le plan

La méthode prévue pour calculer les marges d'erreur de H1 les rend trop larges. Une simulation sur nos vraies communes les trouve 1,3 à 1,7 fois trop grandes, ce qui rend un résultat net plus difficile à montrer. Soit on la garde en le disant, soit on prend une méthode plus juste. Giulio ouvre la discussion, et l'avis de R2 compte.

## Les trois PR à relire

Ordre de fusion : #2, puis on fige le plan, puis #5, puis #6. Fusionner toujours avec « Create a merge commit » : ni squash ni rebase, car le plan cite des numéros de commit.

PR #2

### [Socle et choix des aires](https://github.com/gabrielwenger1-coder/DataScience/pull/2)

Relue par R2 et R3

- R3 : relancer le projet sur ton compte, en suivant seulement le README.
- R2 : vérifier le tableau qui a servi à choisir les aires et la règle qui regroupe les anneaux trop petits.
- Commenter, puis approuver.

PR #5

### [Site, figures, carte par quartier](https://github.com/gabrielwenger1-coder/DataScience/pull/5)

Relue par R3

- Construire le site et vérifier les figures.
- Relire la méthode en une page du README.
- Ajouter la section sur l'usage de l'assistant de code.

PR #6

### [Part de cadres et H1](https://github.com/gabrielwenger1-coder/DataScience/pull/6)

Relue par R2, avant tout lancement

- Relire le calcul de la part de cadres et celui des communes voisines, puis lancer les tests.
- Ne rien lancer sur les vraies données avant que le plan soit figé.
- Ensuite, ajouter sur cette branche la comparaison par anneaux.

## Les tâches de chacun

### R2 analyse

1. Relire la PR #2.
2. Relire la PR #6 avant le premier lancement du calcul des cadres.
3. Écrire la comparaison par anneaux de H1 et la règle pour conclure.
4. Écrire le calcul de H3.
5. Savoir expliquer à l'oral le calcul des distances aux lycées et des paires de communes.

### R3 figures et rapport

1. Relancer le projet sur ton compte et commenter la PR #2.
2. Relire la PR #5 et y écrire la section sur l'assistant de code.
3. Écrire le début du rapport (introduction, données, choix des aires) et le titre de la figure 1.
4. Faire les figures 2, 4, 5 et 6.

### Giulio données et coordination

1. Rendre publiques les copies de données sur le S3.
2. Décider de la règle de `CLAUDE.md` sur les co-auteurs des commits.
3. Fusionner après relecture et figer le plan.
4. Lancer le calcul de la part de cadres.
5. Réunir les données de H4 : gares et médecins.

## Règles du jeu

- Une branche par tâche, une PR relue par un autre membre, fusion avec « Create a merge commit ». Personne ne pousse directement sur `main`.
- Aucun chiffre sur les cadres avant que le plan soit figé : ne lancez ni `rapport.ipynb` ni `quarto render` sur la branche de la PR #6.
- Les règles de calcul sont dans le plan. Si l'une doit changer, on l'écrit, datée, dans son journal.
- Chacun commite le code qu'il devra expliquer à l'oral. L'assistant aide et relit ; il n'écrit ni le texte ni les interprétations.
- Commandes utiles : `uv sync` (installer), `uv run pytest` (tests), `uv run quarto render` (construire le site dans `_site/`).

Dépôt : [gabrielwenger1-coder/DataScience](https://github.com/gabrielwenger1-coder/DataScience) · plan complet : `docs/PLAN.md`