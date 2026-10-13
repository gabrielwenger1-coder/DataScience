---
name: expliquer
description: "Explique en clair à l'étudiant ce qui a été fait dans le projet et pourquoi : avancement, gros changements, choix que l'assistant a pris seul. À utiliser dès que l'étudiant demande un résumé, un point, « où on en est », « qu'est-ce qui a changé » ou « pourquoi ce choix ». Usage : /expliquer, ou /expliquer suivi d'un ticket (T2), d'une branche, d'une décision ou d'une période (« depuis lundi »)."
argument-hint: "[ticket | branche | décision | période]"
---

Sujet demandé : $ARGUMENTS

Sans sujet, couvre ce qui s'est passé depuis la dernière fusion dans `main` (`git log main..HEAD`), ou les 15 derniers commits s'il n'y en a pas. La réponse reste dans la conversation : n'écris aucun fichier de compte rendu.

L'étudiant veut garder la main sur la direction du projet sans relire tout le code. Il ne veut ni liste à puces ni noms de fichiers qu'il ne connaît pas.

## 1. Rassembler les faits dans le dépôt

Une session qui vient de commencer ne sait rien : pars de ce que le dépôt contient, pas de ce que tu crois savoir.
- `git log` et `git diff` sur la période. Lis ce que le diff change, pas seulement les noms de fichiers touchés.
- Le journal des décisions (`docs/PLAN.md`, §13), `.claude/pilotage.md` et, pour une source de données, `docs/exploration_sources.md`.
- Pour une décision précise, le code qui l'applique et sa docstring. Si le journal dit une chose et le code en fait une autre, c'est la première chose à dire.
- Un chiffre ne figure dans la réponse que si tu l'as lu dans le journal ou dans une sortie de cette session. Dis d'où il vient quand tu ne l'as pas recalculé.

## 2. Trier : trois choix, pas plus

Un choix compte quand il change un chiffre des résultats (filtre, seuil, dénominateur, géographie, traitement des valeurs manquantes), s'écarte du plan ou tranche ce qu'il laissait ouvert, ajoute une dépendance ou une source, décide comment une erreur est traitée, ou donnerait lieu à un « pourquoi ? » à la soutenance. Un renommage, un formatage ou de la plomberie ne comptent pas.

Classe-les par poids sur les résultats et garde les trois premiers. Une période large ne rallonge pas la réponse : elle oblige à trier. Les autres tiennent en une phrase (« d'autres choix plus petits sont au journal »).

Sépare ce que le plan ou l'étudiant avait demandé de ce que l'assistant a décidé seul. Les choix pris seul sont ceux dont l'étudiant perd la trace : dis-les toujours. Dans une session neuve, tu ne peux pas le savoir : une demi-phrase suffit (« le journal ne dit pas lesquels l'assistant a proposés »).

## 3. Écrire

Le lecteur est un membre du groupe qui connaît la problématique mais n'a pas suivi la session. Le format est fixe, quelle que soit la période :

1. une phrase d'ouverture qui donne l'essentiel et se comprend seule ;
2. un paragraphe de deux phrases : ce que le projet sait faire de plus ;
3. au plus trois paragraphes de choix, de trois phrases au plus chacun, chacun ouvert par une demi-phrase en gras qui dit le choix en clair ;
4. une ou deux phrases sur ce que l'assistant a décidé seul ;
5. une phrase sur ce qui reste fragile ou à trancher ;
6. la ligne finale : « Pour creuser : demande-moi de détailler un point. Pour vérifier que tu sais le défendre : /soutenance suivi du thème. »

Cela fait 300 mots environ, 350 au plus, et 200 pour une question précise (« pourquoi ce choix ? » : une phrase d'ouverture, un paragraphe, la ligne finale). L'étudiant obtient plus long en disant « détaille ».

Dans les phrases :
- Pas de puces, pas de tableau, sauf si l'étudiant en demande. Une liste de fichiers ou de fonctions n'est pas un résumé : `git diff --stat` le fait.
- Nomme les choses par leur rôle dans le projet (« la collecte de l'annuaire des lycées », « le calcul du nombre de lycées à moins de 5 km »). Un nom de fichier, de fonction, de colonne ou de bibliothèque n'apparaît qu'après la phrase qui l'explique, entre parenthèses, et seulement si l'étudiant doit aller le lire. Trois au plus dans tout le texte.
- Pas de renvoi nu à une section du plan : dis ce qu'elle contient.
- Définis chaque terme technique à sa première apparition par ce qu'il fait ici (« le COG, la liste officielle des codes de communes, qui change chaque année »). Pas d'abréviation sans sa définition.
- Un choix, c'est dans l'ordre : la question qui se posait, ce qui a été retenu, ce qui a été écarté, ce que cela change pour les résultats ou pour la défense à l'oral.
- Donne les chiffres qui ancrent le propos, avec ce qu'ils signifient. Distingue ce que tu as vérifié (« j'ai relancé le calcul : … ») de ce que tu n'as pas pu vérifier. Une intention n'est jamais présentée comme un fait accompli.
- Ni compliment, ni emoji, ni récapitulatif qui répète, ni remarque sur ton propre travail de la session.

Exemple de ton, tiré du journal du 13/10 : « **Un lycée sans statut arrête la collecte.** Un lycée public du département 27 n'a aucun statut (public ou privé) dans l'annuaire de l'Éducation nationale. Un filtre sur « public » l'aurait fait disparaître de la base sans le moindre message, alors qu'il compte dans l'accès aux lycées des communes voisines. La collecte s'arrête donc en nommant ce lycée, au lieu de l'écarter en silence. Contrepartie : un trou dans l'annuaire bloquera le programme tant qu'on n'aura pas décidé quoi en faire. »

## 4. Relire avant d'envoyer

Compte les paragraphes de choix (trois au plus), les noms de code (trois au plus) et les puces (zéro). Vérifie que chaque terme est défini et que chaque chiffre a une source. Si la réponse est trop longue, coupe d'abord les choix les moins lourds, puis les chiffres secondaires. Dernier test : un coéquipier qui n'était pas là pourrait-il redire le choix principal et sa raison après cette lecture ? Sinon, réécris.
