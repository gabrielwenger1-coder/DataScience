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
| 20/10 soir : état actuel → plan exécuté avec A13 à A15 | 2,0 → 3,4 | 0,5 → 3,1 | 1,0 → 4,2 (3,0 si Git reste à un seul auteur) | 1,4 → 1,7 | 1,5 → 3,2 (2,2 si deux membres n'ont rien écrit) | environ 6,4 sans la moyenne (compte neuf : `RuntimeError` dans `stockage._telecharger`, copies en 403 et 404) → environ 15,6 (fourchette 12,5 à 16,5) ; à part, risque de −1 à −3 pour usage abusif de l'IA (`CLAUDE.md` public) |

## Actions prioritaires

Suivi au 20/10 soir : A1 à A12 appliqués (journal §13), A8 rejeté. Choix Nantes, Lyon, Strasbourg journalisé (`731e4f2`, tableau `0583839`), réexaminé et maintenu le 20/10 avec la règle de sacrifice (§10, étape 4 : Strasbourg). A13 à A15 appliqués le 20/10 soir sur `feat/tableau-support`, non commités. Non faits : copies publiques (`curl` anonyme du 20/10 : 403 et 404), PR (0), Git à trois (39 commits d'un seul auteur), tag ; poussées : `main`, `chore/harness-claude`, `feat/carte-croissance` seulement.

1. Avant le 22/10 : copies gelées lisibles par un tiers (S3 public ou release `donnees-20261020`), puis compte neuf rejoué sans `BUCKET_S3`.
2. Deux PR empilées : « socle », jusqu'à `feat/nettoyage-code`, relue par R3 en la reproduisant sur son compte ; « choix », `feat/tableau-support` (avec A13 à A15 et `.claude/hooks/budget_tests.py` commités), relue par R2 avec des commentaires visibles. Fusion par merge commit seulement (hash du journal). Tag annoté `plan-fige` sur la fusion du choix, poussé, au plus tard le 24/10. Repli le 23/10 si R3 n'a pas relu : une seule PR, relue par R2.
3. Transparence IA : section du README par R3 (PR datée du 22/10) ; reformulation de `CLAUDE.md` par Giulio (titre « code qui ne ressemble pas à du code généré », règle anti-Co-Authored-By retirée ou justifiée).
4. Début du rapport écrit par R3 : §1, §2 courts, §3.1 avec la Fig. 1 à titre-message et les 3 aires mises en avant. Commentaires d'une ligne dans `pyproject.toml` pour les dépendances non importées (A14).
5. T5 écrit par R2 ; si sa PR n'est pas ouverte le 26/10, Giulio l'écrit et R2 la relit. Code de T5 préparé hors dépôt par l'agent principal, testé sur une table jouet, ni exécuté sur les vraies données ni commité avant le tag. Avant d'exécuter T5 : estimateur et verdict de H3 en `/pilotage`, puis fiabilité de l'IVAL calculée après le tag et journalisée. Branche T5 depuis `plan-fige`, jamais depuis `feat/carte-croissance` (A15).

## Points ouverts

- Avant T5, sans cadres : listes d'UAI des 3 aires (A10), `assert` des comptes du tableau (§4 D) ; `rapport.ipynb` appelle `construire_base(AIRES_CANDIDATES)` et écrase `final/` avec les 8 aires : séparer la base des 3 aires de la Fig. 1.
- Estimateur et verdict de H3 (« anneau par anneau » impossible : 31 communes à Nantes ont un lycée à 5 km) ; verdict de H4 à fixer avant S5. Fig. 4 : panneau des anneaux presque vide (6 cellules), à revoir en S4.
- T5 : articuler le code préparé par l'agent principal et l'écriture par R2, qui doit pouvoir défendre chaque ligne en soutenance.
- Code : commentaires défensifs très denses (correcteur du 20/10), à alléger au fil des tickets et en S6.
- Mise en forme Quarto encore cassée au §10 et au §12.2 ; « proposition A5 » de `docs/exploration_sources.md` §2 à renommer ; prénoms des membres au §9 ; jeton GitHub du reflog à révoquer ; `docs/prompt_evaluation_independante.md` hors de l'arborescence du §7.

## Désaccords ouverts entre pilote et correcteur

Aucun. Réglés le 20/10 : §4 réduit aux signatures fausses (A5 c) ; T5 n'attend que le tag, la PR de R3 restant datée et suivie (A5 d) ; A13 dans la version du correcteur (toute cellule estimable peut contredire) ; A15 avec les deux rôles de la croissance et sans réexamen de la carte ; Strasbourg maintenue ; deux PR avant le tag, repli à une seule le 23/10. Condition du haut de fourchette selon le correcteur : PR relues et commits réels des deux autres membres d'ici au 22/10, puis exécution complète par un autre membre sur son compte, sans `BUCKET_S3`, depuis les copies gelées publiques, avant le 8/11.
