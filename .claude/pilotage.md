# Tableau de bord du pilotage

Tenu par l'agent pilote à chaque /pilotage. Les décisions elles-mêmes vont dans le journal de docs/PLAN.md (§13).

Dernier point de pilotage : 2026-10-20

## Note prévisionnelle du correcteur

| Date | Données /4 | Descriptif /4 | Démarche et repro /5 | Code /2 | Soutenance /5 | Total /20 |
|------|-----------|---------------|----------------------|---------|---------------|-----------|
| 13/10 état actuel | 0,5 | 0 | 1,5 | 0,6 | 1,2 | environ 4 (pas de notebook, donc pas de moyenne) |
| 13/10 plan exécuté avec A1 à A4 | 3,4 | 3,0 | 4,2 (3,2 si Git reste à un seul auteur) | 1,5 | 3,3 | environ 15,4 (fourchette 13,5 à 16,5) |
| 20/10 état actuel | 2,0 | 0,5 | 1,0 | 1,4 | 1,5 | environ 6,4, sans moyenne (le notebook plante sur un compte neuf : annuaire non gelé) |
| 20/10 plan exécuté avec A5 à A7 | 3,5 | 3,0 | 4,2 (3,0 si Git reste à un seul auteur) | 1,6 | 3,3 (2,3 si deux membres n'ont pas écrit de code) | environ 15,6 (fourchette 12,5 à 16,5 ; 15,0 sans A5 à A7) |
| 20/10 plan exécuté avec A5 à A7, A9, A10 | 3,45 | 3,4 | 4,4 (3,1 si Git reste à un seul auteur) | 1,7 | 3,3 | environ 16,3 (fourchette 13 à 16,5), estimé sans A8 : le correcteur donnait 16,4 avec A8, dont +0,05 en Données et +0,1 en Soutenance |

## Actions prioritaires

Suivi du 13/10 : Git à trois non fait (24 commits, un seul auteur, rien de fusionné) ; repli local fait, `curl` anonyme et test sur un autre compte non faits ; Fig. 1 et squelette faits, ni tableau de support, ni choix des aires, ni tag. A5 à A7 appliqués le 20/10 (journal §13). A8 rejeté par l'étudiant le 20/10 : la variable à expliquer reste celle des séries historiques, la question ACT5 pour Lyon reste ouverte au critère (f). A9 et A10 appliqués le 20/10, avec la mise en forme seule du §0, du §2.2 et du §12.1.

1. Aujourd'hui : geler l'annuaire du 13/10, l'IPS, l'IVAL et les contours (nom daté, `sha256` dans `config.py`, plus d'appel direct à l'API dans le chemin du rapport), les publier (`curl` anonyme, sinon release GitHub), rejouer le compte neuf.
2. D'ici au 22/10, Git à trois : branches poussées, PR vers `main` dans l'ordre, relues par un autre membre. PR de R2 (fusion, tableau de support, `tests/test_analyse.py`) ; PR de R3 (section IA du README), livrable daté du 22/10 suivi ici. Si R2 n'a pas ouvert sa PR le 22/10 : Giulio écrit la fusion, R2 la relit avec des commentaires visibles.
3. Choix des aires le 22/10 (tableau calculé une seule fois, coût de Lyon mesuré, PR, tag au plus tard le 24/10), listes d'UAI régénérées pour 3 aires, fiabilité de l'IVAL journalisée, estimateur et verdict de H3 fixés en `/pilotage` ; T5 du 23 au 25/10.

## Points ouverts

- A9 et A10 dans le code : `plotly` et `duckdb` retirés de `pyproject.toml`, `stockage.copie_controlee`, `lycees_geo` découpée, `pipeline.construire_base(aires)`, titres en argument obligatoire, README.
- Lyon : chemin ACT5 et dénominateur à mesurer avant le choix des aires (critère f), A8 ayant été rejeté.
- Estimateur et verdict de H3 (« anneau par anneau » impossible : 29 communes à Rennes et 31 à Nantes ont un lycée à 5 km).
- Fig. 1 : part du privé comparable dans l'Ouest, à Lyon et à Lille ; seul l'écart d'IPS distingue l'Ouest. H2 et le critère (b) se défendent par la sélectivité.
- Mise en forme Quarto encore cassée au §10 et au §12.2 ; « proposition A5 » de `docs/exploration_sources.md` §2 à renommer.
- Prénoms des membres au §9 ; sort de `CLAUDE.md` ; jeton GitHub du reflog à révoquer.

## Désaccords ouverts entre pilote et correcteur

Aucun. Réglés le 20/10 : §4 réduit aux signatures fausses (A5 c) ; T5 n'attend que le tag, la PR de R3 restant datée et suivie (A5 d). Condition du haut de fourchette selon le correcteur : PR relues et commits réels des deux autres membres d'ici au 22/10, puis exécution complète par un autre membre sur son compte, sans `BUCKET_S3`, depuis les copies gelées publiques, avant le 8/11.
