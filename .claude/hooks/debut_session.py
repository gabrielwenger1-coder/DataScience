"""Contexte injecté au début de chaque session Claude Code (hook SessionStart).

Donne à Claude l'état du dépôt (branche, fichiers en cours, derniers commits) pour
qu'il reparte du travail réel et non de suppositions, et rappelle le point de pilotage
quand le dernier date de plus d'une semaine.
"""

import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RACINE = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
FREQUENCE_PILOTAGE = 7  # jours


def git(*arguments: str) -> str:
    """Exécute une commande git dans le projet et renvoie sa sortie."""
    resultat = subprocess.run(
        ["git", "-C", str(RACINE), *arguments], capture_output=True, text=True, check=False
    )
    return resultat.stdout.rstrip()  # rstrip : `git status --porcelain` commence par un espace


def rappel_pilotage() -> str | None:
    """Renvoie un rappel si aucun point de pilotage n'a eu lieu depuis une semaine."""
    tableau = RACINE / ".claude/pilotage.md"
    texte = tableau.read_text() if tableau.exists() else ""
    dernier = re.search(r"Dernier point de pilotage : (\d{4}-\d{2}-\d{2})", texte)
    if not dernier:
        return "Aucun point de pilotage n'a encore eu lieu : propose /pilotage au prochain jalon."
    ecart = (date.today() - date.fromisoformat(dernier.group(1))).days
    if ecart >= FREQUENCE_PILOTAGE:
        return f"Dernier point de pilotage il y a {ecart} jours : propose /pilotage à l'étudiant."
    return None


def main() -> None:
    """Assemble l'état du dépôt et le transmet à Claude."""
    entree = json.load(sys.stdin)
    branche = git("rev-parse", "--abbrev-ref", "HEAD")
    lignes = [f"Branche courante : {branche}."]
    if branche in ("main", "master"):
        lignes.append(
            "main est protégée : crée une branche (feat/…, fix/…, docs/…) avant de "
            "modifier du code."
        )
    en_cours = git("status", "--porcelain").splitlines()
    if en_cours:
        apercu = ", ".join(ligne[3:] for ligne in en_cours[:10])
        lignes.append(f"{len(en_cours)} fichier(s) modifié(s) ou non suivi(s) : {apercu}.")
    lignes.append("Derniers commits :\n" + git("log", "--oneline", "-5"))
    if not (RACINE / "pyproject.toml").exists():
        lignes.append(
            "Le squelette du dépôt (ticket T0) n'existe pas encore. Les sources de données ont "
            "déjà été explorées : lis docs/exploration_sources.md avant de commencer."
        )
    if rappel := rappel_pilotage():
        lignes.append(rappel)
    if entree.get("source") == "compact":
        lignes.append(
            "Le contexte vient d'être compacté : relis le ticket en cours et "
            "attends la validation de l'étudiant avant toute nouvelle étape."
        )

    sortie = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lignes),
        }
    }
    print(json.dumps(sortie, ensure_ascii=False))


if __name__ == "__main__":
    main()
