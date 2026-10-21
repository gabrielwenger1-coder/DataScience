---
name: verifier
description: "Contrôle complet de reproductibilité et d'hygiène du dépôt, tel que le correcteur l'exécutera — installation depuis uv.lock dans un environnement neuf, ruff, pytest, exécution de rapport.ipynb, notebooks sans sorties, absence de données et de secrets dans Git. Usage : /verifier, ou /verifier --rapide pour ne pas exécuter le notebook."
argument-hint: "[--rapide]"
disable-model-invocation: true
allowed-tools: Bash(bash .claude/scripts/verifier.sh *)
---

Lance `bash .claude/scripts/verifier.sh $ARGUMENTS` et lis le récapitulatif.

- Si tout passe, dis-le en une ligne, avec les étapes sautées et leur raison.
- Pour chaque échec, identifie la cause à partir de la sortie, puis propose la correction la plus simple. Ne corrige qu'après accord.
- Ne contourne jamais un échec : pas de `noqa`, pas de `skip`, pas de `try/except` autour d'une cellule qui plante, pas de donnée locale qui masquerait un téléchargement cassé.

Rappel : faire tourner `rapport.ipynb` de bout en bout sur un service neuf est la condition pour avoir la moyenne. Ce script s'en approche mais ne remplace pas le test sur un SSPCloud neuf prévu au calendrier (PLAN §9).
