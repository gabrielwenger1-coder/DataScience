# Tableau de bord du pilotage

Tenu par l'agent pilote à chaque /pilotage. Les décisions elles-mêmes vont dans le journal de docs/PLAN.md (§13).

Dernier point de pilotage : 2026-10-13

## Note prévisionnelle du correcteur

| Date | Données /4 | Descriptif /4 | Démarche et repro /5 | Code /2 | Soutenance /5 | Total /20 |
|------|-----------|---------------|----------------------|---------|---------------|-----------|
| 13/10 état actuel | 0,5 | 0 | 1,5 | 0,6 | 1,2 | environ 4 (pas de notebook, donc pas de moyenne) |
| 13/10 plan exécuté avec A1 à A4 | 3,4 | 3,0 | 4,2 (3,2 si Git reste à un seul auteur) | 1,5 | 3,3 | environ 15,4 (fourchette 13,5 à 16,5) |

## Actions prioritaires

Suivi : aucun point de pilotage précédent. Amendements A1 à A4 appliqués au plan le 13/10 (journal §13).

1. Git actif à trois : pousser les branches, PR relues par un autre membre, premier commit de chacun des deux autres, aucune réécriture d'historique. Avant de fusionner le harness sur `main` : décider du sort de `CLAUDE.md` et ajouter au README une section « Usage de l'IA générative ».
2. Test `curl` anonyme de la lecture publique du S3, puis repli local quand `BUCKET_S3` manque, puis test du README sur le compte d'un autre membre. Tant que le `curl` n'a pas réussi, le §7 (lecture publique) reste conditionnel.
3. Jalon du 18/10 : tableau de support (8 candidates) commité, Fig. 1, choix des 3 aires journalisé dans une PR fusionnée avant tout T5, tag annoté `plan-fige` posé après la fusion, note de cadrage rédigée par le groupe. Si le calendrier glisse : squelette du notebook d'abord, PR et choix des aires jusqu'au 20/10.

## Points ouverts

- Le notebook reconstruit-il depuis le brut gelé ou lit-il `final/` ? Non décidé, non écrit au plan.
- Prénoms des trois membres à inscrire au §9 (seul « Giulio » est connu).
- Borne d'équilibre de distance au centre du §5.2 (2 km proposée, marquée « à valider » au plan) : à valider avant `plan-fige`.
- Lot hors quota de mise en cohérence du texte (`pynsee` §3.1 et §8.2, cartiflette §12.2 T0, arborescence §7, `docs/exploration_sources.md` §1 périmé) : non décidé, non appliqué.
- Décision sur `CLAUDE.md` et la section IA du README.
- Jeton GitHub visible dans le reflog : révocation conseillée à l'étudiant.
- Énoncé de H1 (§1.2, colonnes « Mesure » et « Test principal ») et §0 : non modifiés, à relire à la lumière de A4.

## Désaccords ouverts entre pilote et correcteur

Aucun. Le remède au support de H1 (paires avec `d_dist_lyc_prive_min` en principal, 10 km à côté du 5 km) a été tranché par l'étudiant dans le sens du correcteur le 13/10.
