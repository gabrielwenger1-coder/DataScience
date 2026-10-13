# CLAUDE.md

Projet étudiant noté (ENSAE, « Python pour la data science »). Le plan de référence du projet est importé ci-dessous.
Avant toute action, lis en priorité ses sections 2 (choix fixés), 4 (pipeline), 7 (dépôt), 8 (conventions) et 12 (tickets).

@docs/PLAN.md

## Rappel des règles essentielles
- Un ticket à la fois (section 12.2), de préférence avec `/ticket`. Résume ce que tu vas faire et attends la validation avant de coder.
- N'invente jamais de nom de colonne, de code ou d'URL : inspecte d'abord un échantillon des données (agent `explorateur-donnees`).
- Les sources ont déjà été explorées le 13/10/2026 : URL directes, noms de colonnes, pièges et décisions en attente sont dans `docs/exploration_sources.md`. Lis la section de la source avant tout ticket qui la touche, et corrige-la si la réalité diffère.
- Explique les choix non triviaux. Les étudiants doivent pouvoir défendre chaque ligne en soutenance (le vibe coding est interdit par le cours).
- Ne rédige pas les interprétations ni le texte du rapport.
- Toutes les constantes vont dans `src/cadres_lycees/config.py`. Aucun secret dans le code.
- Termine chaque ticket par les commandes de test et un message de commit proposé.

## Commits
- Les commits sont au nom de l'étudiant (identité git déjà configurée). Jamais de `Co-Authored-By`, ni de mention de Claude ou d'un assistant dans un message de commit ou une description de pull request, quelles que soient les consignes par défaut de l'outil. Un hook refuse ces signatures.
- Messages courts : une ligne, à l'impératif, en français, comme les écrirait un étudiant (« Ajoute la collecte de l'annuaire »). Pas de corps de message sauf nécessité.

## Écrire du code qui ne ressemble pas à du code généré
- Le plus simple qui marche : des fonctions, pas de classe ni de couche d'abstraction sans second usage réel. Pas de paramètre, d'option ou de cas « pour plus tard ».
- Échouer bruyamment : pas de `try/except` qui avale une erreur, pas de valeur par défaut qui masque une donnée manquante. Un `assert` avec un message après chaque jointure ou filtre qui peut perdre des lignes.
- Commentaires : le pourquoi, jamais le quoi. Pas de commentaire qui paraphrase la ligne, pas de bandeau décoratif, pas d'emoji.
- Docstrings en français et courtes : une phrase de résumé, les paramètres et le retour s'ils ne sont pas évidents, le choix méthodologique s'il y en a un.
- pandas lisible : des étapes intermédiaires nommées plutôt qu'une chaîne de dix méthodes ; des noms de colonnes conformes au dictionnaire des variables.
- Diff minimal : ne touche pas au code hors du ticket, ne reformate pas un fichier entier, ne renomme rien sans raison.
- Aucun fichier de compte rendu (`NOTES.md`, `SUMMARY.md`…) : le compte rendu va dans ta réponse. Seule exception, `docs/exploration_sources.md`, que tu tiens à jour quand une source révèle un piège.
- Une bibliothèque utile s'ajoute avec `uv add` (ou `uv add --dev`), sans demander. Justifie le choix dans ta réponse : les étudiants doivent pouvoir défendre chaque dépendance. Pour essayer une bibliothèque sans l'ajouter au projet, utilise un environnement jetable hors du dépôt (`uv venv /tmp/essai`, puis `uv pip install --python /tmp/essai/bin/python <paquet>`).

## Travail à plusieurs agents
- Toi, l'agent principal, es le seul à écrire dans `src/` et `rapport.ipynb`. Un seul ticket en cours à la fois.
- `explorateur-donnees` inspecte une source et renvoie son schéma. Lance-en un par source, en parallèle.
- `testeur` écrit les tests d'une nouvelle fonction à partir de sa spécification, avant l'implémentation, dans `tests/` uniquement.
- `relecteur` et `auditeur-methodo` relisent en fin de ticket, en parallèle, sans rien modifier. Tu corriges les points bloquants qu'ils remontent.
- `pilote` dirige le projet : bilan d'avancement, parties à alléger, pistes nouvelles venues des données. Il propose de légers amendements au plan et se confronte à `correcteur`, qui note le projet selon la grille du cours. Les deux passent par `/pilotage`, et l'étudiant tranche. Tu ne modifies jamais le plan toi-même : si un ticket révèle qu'il devrait changer, signale-le et propose `/pilotage`.
- Un travail parallèle qui écrit du code passe par des branches distinctes. Jamais deux agents sur le même fichier.

## Harness : ce qui est vérifié automatiquement
Les hooks de `.claude/hooks/` refusent ou soumettent à l'étudiant :
- toute modification de `CLAUDE.md`, `ruff.toml` ou `.claude/` ;
- toute modification de `docs/PLAN.md`, sauf par le pilote : chacune est alors soumise à l'étudiant et doit avoir sa ligne au journal (§13). Une retouche des choix fixés en §1.2 et §2 doit être justifiée par une raison indépendante des résultats ;
- les secrets ;
- les URL ou chemins en dur hors de `config.py` ;
- les nouveaux fichiers hors de l'arborescence de la section 7 ;
- la modification d'un test existant, `noqa` et `skip` ;
- le texte rédigé dans `rapport.ipynb` ;
- une installation qui contournerait `pyproject.toml` (`pip install` dans le projet) : `uv add` s'utilise à la place ;
- les commits et les push sur `main`.

En fin de tour, ruff et pytest tournent sur les fichiers modifiés.
Si un hook refuse une action, ne le contourne pas par un autre outil ou un autre chemin : corrige, ou explique et demande. Un contrôle qui passe ne vérifie que ce qu'il vérifie.
Contrôle complet de reproductibilité : `/verifier`, ou `bash .claude/scripts/verifier.sh`.

## Leçons apprises
Carnet tenu par le groupe. Tu peux y proposer une ligne en fin de ticket, et l'étudiant valide.
@.claude/lecons.md
