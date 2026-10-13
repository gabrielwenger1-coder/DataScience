---
name: ticket
description: "Dérouler un ticket du projet de bout en bout (exploration, plan validé, tests, implémentation, revue, rendu). Usage : /ticket T2, ou /ticket suivi d'une description courte."
argument-hint: <T0…T6 | description>
disable-model-invocation: true
---

Ticket demandé : $ARGUMENTS

1. **Cadrer.** Retrouve le ticket (PLAN.md §12.2, ou la description donnée) et son critère « Fait quand ». Si tu es sur `main` ou sur `chore/harness-claude`, propose un nom de branche (`feat/…`, `fix/…`, `docs/…`) et crée-la après accord, à partir de la branche courante si le harness n'est pas encore sur `main`.
2. **Explorer.** Si le ticket touche une source de données que tu n'as pas encore inspectée, délègue à l'agent `explorateur-donnees`, avec un agent par source, lancés en parallèle. Les noms de colonnes, codes et URL viennent de ses rapports ou de PLAN.md, nulle part ailleurs.
3. **Plan.** En cinq lignes au plus : ce que tu vas faire, les fichiers touchés, ce qui reste hors périmètre, les choix à trancher. **Attends la validation.**
4. **Tests d'abord.** Pour une fonction de calcul, délègue l'écriture des tests à l'agent `testeur`. Donne-lui la spécification (signature, règles du plan), pas ton implémentation. Lance les tests : ils doivent échouer.
5. **Implémenter.** Le minimum qui satisfait le ticket et les tests, une fonction à la fois. Ne modifie pas un test pour le faire passer : si un test te semble faux, dis-le.
6. **Vérifier.** Lance `uv run pytest -q` et `uv run ruff check`. Exécute ensuite le code sur de vraies données et montre la sortie (comptes, schéma, valeurs extrêmes) : un test vert ne prouve pas que les données sont bonnes.
7. **Revue.** Lance en parallèle l'agent `relecteur` et, si le diff touche la construction des variables ou l'analyse, l'agent `auditeur-methodo`. Corrige les points bloquants. Liste les autres sans les corriger d'office.
8. **Rendre.** Termine par :
   - **Fait** : 3 à 5 puces.
   - **Pour tester** : les commandes exactes.
   - **Commit proposé** : une ligne courte, à l'impératif, en français, comme l'écrirait l'étudiant. Ni mention de Claude, ni `Co-Authored-By`. Ajoute `Closes #n` seulement s'il y a une issue.
   - **À comprendre avant la soutenance** : 2 ou 3 questions sur les choix de ce ticket.
   - **Écarts au plan** : ce qui, dans ce ticket, s'écarte du plan ou suggère de le changer (donnée absente, piste nouvelle, partie peu informative). S'il y en a, propose `/pilotage` ; sinon, écris « aucun ».
   - **Leçon** : si une erreur de ce ticket risque de se reproduire, une ligne à ajouter à `.claude/lecons.md` ; sinon rien.
