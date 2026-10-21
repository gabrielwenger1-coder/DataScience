---
name: revue
description: "Relecture indépendante du travail en cours (code et méthode) par deux agents en parallèle, sans rien modifier. Usage : /revue, ou /revue suivi d'un fichier ou d'une branche."
argument-hint: "[fichier | branche]"
disable-model-invocation: true
---

Cible : $ARGUMENTS (par défaut, le diff de la branche courante par rapport à `main` et les modifications non commitées).

1. Lance **en parallèle** l'agent `relecteur` et l'agent `auditeur-methodo` sur cette cible. L'auditeur n'est utile que si la cible touche `geo.py`, `accessibilite.py`, `nettoyage.py`, `analyse.py` ou une figure de résultats ; sinon, lance le relecteur seul.
2. Fusionne leurs rapports : supprime les doublons, garde l'ordre de gravité, conserve les références fichier:ligne.
3. Pour chaque point bloquant, vérifie toi-même qu'il est fondé avant de le présenter. Écarte les faux positifs en disant pourquoi.
4. Ne corrige rien sans accord. Termine par la liste des corrections que tu proposes, dans l'ordre où tu les ferais.
