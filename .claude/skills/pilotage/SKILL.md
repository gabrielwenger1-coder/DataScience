---
name: pilotage
description: "Point de pilotage : le pilote fait le bilan et propose de légers amendements au plan, le correcteur note le projet et ces amendements, les deux confrontent leurs avis, puis l'étudiant tranche. À lancer à chaque jalon (fin de semaine, exploration qui révèle une piste, point de décision du 8 novembre). Usage : /pilotage, ou /pilotage suivi d'une idée ou d'une question à examiner."
argument-hint: "[idée ou question]"
disable-model-invocation: true
---

Idée ou question de l'étudiant (facultative) : $ARGUMENTS

Aucun code n'est écrit pendant un point de pilotage. Attends le résultat de chaque agent avant de passer à l'étape suivante.

1. **Bilan et propositions.** Lance l'agent `pilote` (nomme-le `pilote` si l'outil le permet) avec l'idée ou la question éventuelle. Il renvoie un bilan et au plus trois amendements.
2. **Évaluation indépendante.** Lance l'agent `correcteur`. Donne-lui les amendements tels que formulés, mais pas le bilan ni le raisonnement du pilote, pour qu'il juge le dépôt par lui-même. Il renvoie la note prévisionnelle, son avis sur chaque amendement et les corrections au meilleur gain.
3. **Confrontation.** Transmets l'avis complet du correcteur au pilote (SendMessage à son nom ou à son identifiant, pour qu'il garde son contexte). Il répond point par point : retenu, modifié ou rejeté. S'il modifie un amendement en profondeur ou en ajoute un, soumets la nouvelle version au correcteur. Deux rondes au plus.
4. **Arbitrage.** Présente à l'étudiant, sans rien appliquer, en phrases claires et avec les termes techniques définis (méthode de `.claude/skills/expliquer/SKILL.md`) :
   - la note prévisionnelle par critère (état actuel, puis si le plan est exécuté) ;
   - chaque amendement final, avec l'avis du correcteur et la réponse du pilote ;
   - les désaccords restants, en exposant les deux positions sans trancher ;
   - les trois actions prioritaires qui en découlent.

   Attends sa décision, amendement par amendement.
5. **Application.** Pour les seuls amendements validés, demande au pilote de modifier `docs/PLAN.md`, d'ajouter les lignes du journal (§13) et de mettre à jour `.claude/pilotage.md`. Chaque modification du plan est soumise à l'étudiant. Montre ensuite `git diff docs/PLAN.md`. Si le pilote signale des « choix figés modifiés », répète sa justification à l'étudiant. Propose enfin de commiter le plan, pour que le prochain point parte d'un état propre.
6. **Suite.** Propose le prochain ticket (`/ticket`) qui découle des actions prioritaires.
