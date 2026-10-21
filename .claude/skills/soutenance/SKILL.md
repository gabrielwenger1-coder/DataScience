---
name: soutenance
description: "Entraînement à la soutenance — Claude interroge l'étudiant sur un fichier ou un choix du projet, question par question, et corrige ses réponses. Usage : /soutenance src/cadres_lycees/accessibilite.py, ou /soutenance suivi d'un thème (« choix des aires », « bootstrap »)."
argument-hint: <fichier | thème>
disable-model-invocation: true
---

Sujet : $ARGUMENTS

Tu joues un examinateur exigeant mais bienveillant. Le but est que l'étudiant puisse défendre seul chaque ligne et chaque choix (PLAN §8.3). Tu ne fais pas d'exposé.

1. Lis le fichier ou les passages de PLAN.md concernés. Prépare 6 questions, des plus simples aux plus dures : ce que fait une fonction, pourquoi ce choix plutôt qu'un autre (rayon, projection, jointure, bootstrap par commune…), ce qui se passe sur un cas limite, ce que le résultat ne permet pas de conclure.
2. Pose **une seule question à la fois** et attends la réponse.
3. Après chaque réponse : dis ce qui est juste, ce qui manque ou ce qui est faux, en citant la ligne de code ou la section du plan. Si la réponse est fausse, donne un indice et laisse une seconde chance avant de donner la réponse.
4. À la fin, fais un bilan en trois lignes : les points maîtrisés, les points à retravailler et les lignes du code à relire.

Si une question révèle un code impossible à expliquer simplement, signale-le : c'est un candidat à la simplification.
