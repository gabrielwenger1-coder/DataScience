---
name: passation
description: "Prépare la passation d'un ticket avancé par l'étudiant à un coéquipier qui doit le relire puis le reprendre : texte de pull request et d'issue en clair, ce qu'il doit comprendre et vérifier. Usage : /passation T2 Solal, ou /passation suivi du ticket et du prénom du relecteur."
argument-hint: "<ticket> <prénom du relecteur>"
disable-model-invocation: true
---

Ticket et relecteur : $ARGUMENTS

L'étudiant a avancé ce ticket. Le relecteur désigné ne l'a pas suivi : il doit le lire, le comprendre, puis le reprendre à son nom. Le travail reste signé de celui qui l'a fait : ne mets jamais le nom du relecteur comme auteur d'un commit. La responsabilité de relire passe par l'issue assignée et la demande de relecture sur la pull request (PLAN §8.1). Tu n'exécutes ni `gh` ni `git push` : tu prépares les textes et les commandes, l'étudiant les lance.

1. **Rassembler les faits** comme `/expliquer` : `git diff main...HEAD`, le journal (§13), le code des choix qui comptent. Lance les commandes de test pour savoir ce qui passe réellement.
2. **Rédiger la description de la pull request**, à la première personne de l'étudiant et en phrases (pas de puces de fichiers, termes définis, chiffres vus), 300 mots au plus, sans mention d'un assistant ni d'un outil. Dans l'ordre :
   - ce que fait la branche, en deux ou trois phrases ;
   - les trois choix à connaître, chacun avec ce qui a été écarté et ce qu'il change pour les résultats ;
   - comment la lancer et ce que le relecteur doit voir apparaître (commandes exactes, sortie attendue) ;
   - ce qui n'est pas vérifié ou fragile ;
   - trois questions auxquelles le relecteur doit savoir répondre avant de dire « relu », parce qu'un examinateur les poserait ;
   - ce que le relecteur reprend ensuite (la suite du ticket, les trous connus).
3. **Proposer l'assignation** : le titre de l'issue du ticket, l'issue à assigner au relecteur, la pull request avec lui comme relecteur demandé (l'identifiant GitHub est à fournir par l'étudiant). Termine par les commandes `gh issue create` et `gh pr create --reviewer`, sans les lancer.
4. **Dire ce qui reste à faire pour le relecteur** en une phrase : relire, poser ses questions, puis corriger ou continuer avec ses propres commits.

Présentation à l'étudiant : quatre phrases de prose au plus avant les textes (pas de puces, pas de liste de fichiers) pour dire ce qui est prêt, ce qu'il doit trancher avant d'envoyer (la branche de base de la pull request, un choix du texte qu'il ne défendrait pas) et ce qui n'est pas vérifié. Si le ticket repose sur des branches pas encore fusionnées, dis-le en une phrase et propose la base adaptée. Le push reste à sa main : donne la commande, ne la lance pas. Si le diff révèle un choix sans ligne au journal, propose cette ligne en fin de réponse.
