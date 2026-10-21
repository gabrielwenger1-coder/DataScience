# Tableau de bord du pilotage

Tenu par l'agent pilote à chaque /pilotage. Les décisions elles-mêmes vont dans le journal de docs/PLAN.md (§13).

Dernier point de pilotage : 2026-10-21

## Note prévisionnelle du correcteur
| Date | Données /4 | Descriptif /4 | Démarche et repro /5 | Code /2 | Soutenance /5 | Total /20 |
|------|-----------|---------------|----------------------|---------|---------------|-----------|
| 13/10 état actuel | 0,5 | 0 | 1,5 | 0,6 | 1,2 | environ 4 (pas de notebook, donc pas de moyenne) |
| 13/10 plan exécuté avec A1 à A4 | 3,4 | 3,0 | 4,2 (3,2 si Git reste à un seul auteur) | 1,5 | 3,3 | environ 15,4 (fourchette 13,5 à 16,5) |
| 20/10 état actuel | 2,0 | 0,5 | 1,0 | 1,4 | 1,5 | environ 6,4, sans moyenne (le notebook plante sur un compte neuf : annuaire non gelé) |
| 20/10 plan exécuté avec A5 à A7 | 3,5 | 3,0 | 4,2 (3,0 si Git reste à un seul auteur) | 1,6 | 3,3 (2,3 si deux membres n'ont pas écrit de code) | environ 15,6 (fourchette 12,5 à 16,5 ; 15,0 sans A5 à A7) |
| 20/10 plan exécuté avec A5 à A7, A9, A10 | 3,45 | 3,4 | 4,4 (3,1 si Git reste à un seul auteur) | 1,7 | 3,3 | environ 16,3 (fourchette 13 à 16,5), estimé sans A8 : le correcteur donnait 16,4 avec A8, dont +0,05 en Données et +0,1 en Soutenance |
| 20/10 soir : état actuel → plan exécuté avec A13 à A15 | 2,0 → 3,4 | 0,5 → 3,1 | 1,0 → 4,2 (3,0 si Git reste à un seul auteur) | 1,4 → 1,7 | 1,5 → 3,2 (2,2 si deux membres n'ont rien écrit) | environ 6,4 sans la moyenne (compte neuf : `RuntimeError` dans `stockage._telecharger`, copies en 403 et 404) → environ 15,6 (fourchette 12,5 à 16,5) ; à part, risque de −1 à −3 pour usage abusif de l'IA (`CLAUDE.md` public) |
| 21/10 : état actuel → plan exécuté (avis du 20/10 soir sur A16 à A18) | 2,2 → 3,4 | 0,5 → 3,0 | 1,2 → 4,0 (3,0 si Git reste à un seul auteur) | 1,4 → 1,6 | 1,5 → 3,0 (2,2 si deux membres n'ont pas écrit de code) | environ 6,8 sans la moyenne (compte neuf : `collecte.ips_lycees()` en 403 et 404) → environ 15,0 (fourchette 12 à 16) ; à part, −1 à −3 pour usage abusif de l'IA (traces de l'assistant dans le code) |

## Actions prioritaires
Suivi au 21/10 : A1 à A18 appliqués (journal §13), A8 rejeté. A13 à A15 sont commités dans `392ca82` (la mention « non commités » du 20/10 était fausse) ; la fiabilité de l'IVAL (0,608, H3 testable), A16 à A18 et la ligne de T5 sont appliqués le 21/10 sur `feat/tableau-support`, non commités. Non faits : copies publiques (403 et 404), PR (0, `gh` non authentifié), tag, Git à trois (46 commits d'un seul auteur), section IA du README.
1. Avant le 22/10, 1 h : copies gelées lisibles anonymement (S3 `raw/` public ou release `donnees-20261020` avec les 12 fichiers de `data/gel_20261020`), puis compte neuf sans `BUCKET_S3`. Condition de la moyenne.
2. Aujourd'hui, après la poussée du commit de ce point : PR « socle » (relue par R3) et « choix » (relue par R2), au besoin par l'interface web ; fusion `--no-ff` ; tag `plan-fige` poussé au plus tard le 24/10.
3. Transparence IA : section « Usage de l'IA générative » du README par R3 (PR du 22/10) ; Giulio tranche la règle anti-Co-Authored-By de `CLAUDE.md` ; traces de l'assistant retirées du code (« choix de l'étudiant du 20/10 » à `nettoyage.py` l.154 et `config.py` l.69-70, « bucket de Giulio »).
4. T5 (ligne du 21/10) : `feat/tableau-support` fusionnée dans `feat/site-quarto`, T5 adapté à A17 commité par l'agent principal, relu par R2 dans la PR avant toute exécution ; exécution après le tag, au plus tard le 24/10 (le 25/10 si le tag manque ; R3 relit si R2 manque le 26/10).
5. R3 écrit le §1, le §3.1 et le titre-message de la Fig. 1 avant le 1/11.
6. Carte IRIS (A18, choix de Giulio) : après le tag, sans prendre sur 1 à 5 ni sur H1 à H4 ; fusionnée au plus tard le 19/11, sinon abandonnée.

## Points ouverts
- Avant d'exécuter T5, sans cadres : listes d'UAI des 3 aires (A10), `assert` des comptes du tableau (§4 D) ; dénominateur 2011 (`C11_POP2554` − `CS7` − `CS8`) : noms et égalité à vérifier dans l'en-tête du fichier.
- Verdict de H4 à fixer au point du 8/11, avant toute estimation de H4. Fig. 4 : panneau des anneaux presque vide (6 cellules), à revoir en S4. Soutenance : convergence entre communes, sans contrôle par `part_cadres_2011` (A16).
- Code : commentaires défensifs très denses, `config.py` de 271 lignes (correcteur du 20/10), à alléger au fil des tickets et en S6.
- Mise en forme Quarto encore cassée au §10 et au §12.2 ; « proposition A5 » de `docs/exploration_sources.md` §2 à renommer ; prénoms des membres au §9 ; jeton GitHub du reflog à révoquer ; `docs/prompt_evaluation_independante.md` hors de l'arborescence du §7.

## Désaccords ouverts entre pilote et correcteur
- A16 (e), mineur : le correcteur lit la variation de l'IVAL dans l'anneau 0-5 km entre aires (écart-type 0,71 contre 0,76 à 1,15) ; le pilote la lit à l'intérieur de chaque cellule aire × anneau (0,11 à 0,16 contre 0,41 à 1,29), seule à identifier β_q avec l'effet fixe. Le journal donne les chiffres par cellule.
- Gel de la méthode après A16 et A17 jusqu'au 8/11, proposé par le correcteur et appuyé par le pilote : refusé par Giulio. Toute modification de méthode reste soumise au §5.8 et au journal.
- Carte IRIS : pilote et correcteur la voulaient après le deuxième test complet ; Giulio l'a placée après le tag (A18).
- Réglés le 21/10 : T5 exécuté après le tag (variante du correcteur) ; A17 tel quel ; MIGCOM en piste sans code, INDCVI écarté. Condition du haut de fourchette : PR relues et commits réels des deux autres membres, puis exécution complète par un autre membre sur son compte, sans `BUCKET_S3`, depuis les copies publiques, avant le 8/11.
