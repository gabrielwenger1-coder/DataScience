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
- Le nom d'un commit est celui de la personne qui a avancé le travail, jamais celui d'un coéquipier qui doit le relire. Pour dire qu'un coéquipier relit ou reprend un ticket, on assigne l'issue et on lui demande la relecture de la pull request : `/passation <ticket> <prénom>` prépare les textes. Aucun commit ne se fait avec `--author` ou une autre identité que celle configurée.

## Écrire du code qui ne ressemble pas à du code généré
- Le plus simple qui marche : des fonctions, pas de classe ni de couche d'abstraction sans second usage réel. Pas de paramètre, d'option ou de cas « pour plus tard ».
- Échouer bruyamment : pas de `try/except` qui avale une erreur, pas de valeur par défaut qui masque une donnée manquante. Un `assert` avec un message après chaque jointure ou filtre qui peut perdre des lignes.
- Commentaires : le pourquoi, jamais le quoi. Pas de commentaire qui paraphrase la ligne, pas de bandeau décoratif, pas d'emoji.
- Docstrings en français et courtes : une phrase de résumé, les paramètres et le retour s'ils ne sont pas évidents, le choix méthodologique s'il y en a un.
- pandas lisible : des étapes intermédiaires nommées plutôt qu'une chaîne de dix méthodes ; des noms de colonnes conformes au dictionnaire des variables.
- Diff minimal : ne touche pas au code hors du ticket, ne reformate pas un fichier entier, ne renomme rien sans raison.
- Aucun fichier de compte rendu (`NOTES.md`, `SUMMARY.md`…) : le compte rendu va dans ta réponse. Seule exception, `docs/exploration_sources.md`, que tu tiens à jour quand une source révèle un piège.
- Une bibliothèque utile s'ajoute avec `uv add` (ou `uv add --dev`), sans demander. Justifie le choix dans ta réponse : les étudiants doivent pouvoir défendre chaque dépendance. Pour essayer une bibliothèque sans l'ajouter au projet, utilise un environnement jetable hors du dépôt (`uv venv /tmp/essai`, puis `uv pip install --python /tmp/essai/bin/python <paquet>`).

## Tests : peu, et seulement les importants
Beaucoup de tests, c'est du code généré que personne ne relit : un correcteur le voit, et les étudiants doivent pouvoir défendre chaque ligne.
- Pour vérifier ton code, écris autant de tests ou de scripts jetables que tu veux **hors du dépôt**, dans le dossier temporaire de la session (par défaut `/tmp/essais/`) : `uv run pytest /tmp/essais/`. Lance-les, puis laisse-les là. Ils ne sont jamais commités.
- Dans `tests/`, seulement les tests qui protègent un calcul critique, dont une erreur fausserait les résultats sans aucun signal : `accessibilite.indicateurs` (`tests/test_accessibilite.py`), `geo.paires_contigues` et le passage de géographie (`tests/test_geo.py`), ce que le plan prévoit. Si un autre calcul le mérite (anneaux, bootstrap par commune…), propose-le à l'étudiant avec la raison avant d'écrire le test.
- Budget : 3 fichiers de test, 6 tests par fichier au plus, sur des données jouets minuscules, calculables à la main.
- Pas de test pour la collecte (réseau), la lecture et l'écriture de fichiers, les figures, `config.py`, ni pour une fonction triviale. Pas de mock.
- Les contrôles de cohérence des données (nombre de lignes après une jointure, plages de valeurs, unicité des codes) sont des `assert` avec un message dans le pipeline, pas des tests.
- À la fin d'un ticket, passe `tests/` en revue : tout test qui ne protège pas un calcul critique est supprimé.

## Expliquer le travail
Le risque du projet n'est pas seulement un bug : c'est qu'un membre du groupe ne comprenne plus pourquoi le code fait ce qu'il fait. Il ne pourrait alors ni le défendre en soutenance, ni le corriger. Aucune étape ne bloque pour autant l'avancée.
- Un choix qui compte change un chiffre des résultats (filtre, seuil, dénominateur, géographie, valeurs manquantes), s'écarte du plan ou en tranche un point ouvert, ajoute une dépendance ou une source, ou décide comment une erreur est traitée. Dis-le au moment où tu le fais, en une ou deux phrases : ce que tu retiens, ce que tu écartes, pourquoi. Continue sans attendre de réponse. Si tu le décides seul, sans que le plan ou l'étudiant l'ait demandé, écris-le : « j'ai décidé seul de… ».
- Le pourquoi reste dans le dépôt : une phrase de docstring ou de commentaire à l'endroit du choix et, pour un choix qui compte, une ligne du journal (§13) que tu proposes en fin de ticket. Pas de nouveau fichier.
- Tout compte rendu (fin de ticket, réponse à « où on en est ? ») suit la méthode de `.claude/skills/expliquer/SKILL.md` : de la prose, l'essentiel en première phrase, les choses nommées par leur rôle et non par leur fichier, les termes définis, des chiffres que tu as vus, le vérifié séparé du non vérifié, les longueurs fixées par la méthode. Quand l'étudiant demande un résumé, un point ou la raison d'un choix, charge cette méthode même s'il n'a pas tapé `/expliquer`.
- Une liste de fichiers modifiés n'est pas un résumé : `git diff --stat` la donne.

## Travail à plusieurs agents
- Toi, l'agent principal, es le seul à écrire dans `src/` et `rapport.ipynb`. Un seul ticket en cours à la fois.
- `explorateur-donnees` inspecte une source et renvoie son schéma. Lance-en un par source, en parallèle.
- `testeur` écrit, avant l'implémentation, les tests d'un calcul critique (voir « Tests ») à partir de sa spécification, dans `tests/` uniquement.
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
- la modification d'un test existant, un nouveau fichier de test hors de ceux du plan, plus de 6 tests dans un fichier, `noqa` et `skip` ;
- le texte rédigé dans `rapport.ipynb` ;
- une installation qui contournerait `pyproject.toml` (`pip install` dans le projet) : `uv add` s'utilise à la place ;
- les commits et les push sur `main`.

En fin de tour, ruff et pytest tournent sur les fichiers modifiés, et le budget de tests est vérifié.
Si un hook refuse une action, ne le contourne pas par un autre outil ou un autre chemin : corrige, ou explique et demande. Un contrôle qui passe ne vérifie que ce qu'il vérifie.
Contrôle complet de reproductibilité : `/verifier`, ou `bash .claude/scripts/verifier.sh`.

## Leçons apprises
Carnet tenu par le groupe. Tu peux y proposer une ligne en fin de ticket, et l'étudiant valide.
@.claude/lecons.md
