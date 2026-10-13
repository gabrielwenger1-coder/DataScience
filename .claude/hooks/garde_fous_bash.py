"""Garde-fous avant toute commande shell lancée par Claude (hook PreToolUse sur Bash).

Ce n'est pas un bac à sable : une commande détournée peut passer. Le but est d'arrêter
les erreurs courantes (secret affiché, installation hors pyproject, push sur main…)
et de rendre les règles du groupe explicites pour Claude.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import budget_tests

RACINE = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

PROTEGES = r"(\S*/)?(PLAN\.md|CLAUDE\.md|ruff\.toml)\b|\S*\.claude/"
REFUS = (
    (
        r"\bprintenv\b|(^|[;&|(]\s*)(env|set|export|export -p)\s*($|[;&|)])|/proc/\S*environ",
        "Affiche les variables d'environnement, qui contiennent des jetons (S3, Vault, GitHub).",
    ),
    (
        r"\$\{?(AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|VAULT_TOKEN|GIT_PERSONAL_ACCESS_TOKEN)",
        "Affiche un secret.",
    ),
    (
        r"git\s+remote\s+(-v|get-url|show)|git\s+config\s+(-l|--list|.*remote\.)|\.git/config",
        "Sur SSPCloud, l'URL du dépôt distant contient un jeton GitHub.",
    ),
    (
        r"(?i)(\bgit\s+commit\b|\bgh\s+pr\s+(create|edit)\b)[\s\S]*"
        r"(co-authored-by|generated with|noreply@anthropic)",
        "Les commits et les pull requests sont au nom de l'étudiant : pas de Co-Authored-By "
        "ni de signature d'assistant (CLAUDE.md).",
    ),
    (r"--no-verify\b", "Contourne les hooks git (pre-commit)."),
    (r"git\s+push\b.*(\s-f\b|--force)", "Push forcé."),
    (
        r"git\s+push\b.*\b(main|master)\b",
        "Push sur main : passer par une pull request relue (PLAN §8.1).",
    ),
    (
        r"git\s+add\s+(.*\s)?(-A|--all|\.)(\s|$)",
        "Ajout en bloc : liste les fichiers explicitement (évite d'ajouter données ou secrets).",
    ),
    (
        r"git\s+add\b.*\.(csv|parquet|xlsx?|zip|gpkg|shp|geojson|feather)\b",
        "Les données vont sur S3, pas dans Git (PLAN §7).",
    ),
    (
        rf"(>>?\s*|\btee\s+(-a\s+)?|\bsed\s+-i\S*\s+(.*\s)?|\b(rm|mv)\s+(.*\s)?)({PROTEGES})"
        rf"|\bcp\s+(-\S+\s+)*\S+\s+({PROTEGES})",
        "Écriture d'un fichier du plan ou du harness : Claude ne le modifie pas.",
    ),
)
A_VALIDER = (
    (
        r"\bgit\s+add\b[^;&|\n]*\btests(/|\s|$)",
        "Ajout d'un test au dépôt : seuls les tests qui protègent un calcul critique restent "
        f"(CLAUDE.md). Une vérification ponctuelle va dans {budget_tests.DOSSIER_ESSAIS}/.",
    ),
    (r"\bgit\s+commit\b", "Commit : l'étudiant relit le diff et le message (PLAN §8.1)."),
    (r"\bgit\s+push\b", "Push : l'étudiant valide."),
    (r"\bgit\s+(merge|rebase)\b", "Fusion : elle passe normalement par une pull request."),
    (
        r"\bgit\s+(reset\s+--hard|clean\s+-\S*f|checkout\s+(\S+\s+)?--\s|restore\s)"
        r"|\brm\s+-\S*r\S*\s+(?!/tmp/)",
        "Commande destructrice : du travail non commité peut être perdu.",
    ),
)
# Les agents qui relisent, notent ou pilotent ne changent rien à l'état du dépôt git.
RELECTEURS = ("relecteur", "auditeur-methodo", "correcteur", "pilote")
GIT_ECRITURE = r"\bgit\s+(commit|add|checkout|switch|reset|restore|stash|push|merge|rebase|rm|mv)\b"

# Installer une bibliothèque est permis : `uv add` pour le projet, ou n'importe quoi dans un
# environnement jetable hors du dépôt. Seule une installation qui viserait l'environnement du
# projet sans passer par pyproject.toml est refusée : le correcteur ne la retrouverait pas.
INSTALLATION = re.compile(r"\b(pip3?|python3?\s+-m\s+pip|uv\s+pip|conda|mamba)\s+install\b")
SEPARATEURS = re.compile(r"&&|\|\||[;|\n]")
OPTION_CIBLE = re.compile(r"(?<=\s)(?:--python|-p|--target|-t|--prefix)(?:=|\s+)(\S+)")
INTERPRETEUR = re.compile(r"(\S+)/bin/(?:python3?|pip3?)(?=\s)")
RAISON_INSTALLATION = (
    "Cette installation ne passerait pas par pyproject.toml : le projet ne s'installerait pas "
    "à l'identique chez le correcteur (PLAN §8.2). Pour l'ajouter au projet : `uv add <paquet>` "
    "(ou `uv add --dev`). Pour l'essayer sans l'ajouter : `uv venv /tmp/essai` puis "
    "`uv pip install --python /tmp/essai/bin/python <paquet>`."
)


def repondre(decision: str, raison: str) -> None:
    """Transmet la décision à Claude Code et termine le hook."""
    sortie = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": raison,
        }
    }
    print(json.dumps(sortie, ensure_ascii=False))
    sys.exit(0)


def branche_courante() -> str:
    """Renvoie la branche git courante du projet (chaîne vide hors dépôt)."""
    resultat = subprocess.run(
        ["git", "-C", str(RACINE), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return resultat.stdout.strip()


def tests_indexes() -> list[str]:
    """Liste les fichiers de tests/ déjà ajoutés à l'index git."""
    resultat = subprocess.run(
        ["git", "-C", str(RACINE), "diff", "--cached", "--name-only", "--", "tests/"],
        capture_output=True,
        text=True,
        check=False,
    )
    return resultat.stdout.split()


def cible_hors_projet(segment: str, cwd: Path) -> bool:
    """Vrai si la commande installe dans un environnement ou un dossier hors du projet."""
    cibles = OPTION_CIBLE.findall(segment) + INTERPRETEUR.findall(segment)
    for cible in cibles:
        if "/" not in cible:  # `--python 3.13` désigne une version, pas un dossier
            continue
        chemin = Path(os.path.normpath(cwd / Path(cible.strip("'\"")).expanduser()))
        # On ne suit pas le lien final : `.venv/bin/python` pointe vers l'interpréteur système.
        if not (chemin.parent.resolve() / chemin.name).is_relative_to(RACINE):
            return True
    return False


def installation_refusee(commande: str, cwd: Path) -> bool:
    """Vrai si une installation de la commande vise l'environnement du projet."""
    return any(
        INSTALLATION.search(segment) and not cible_hors_projet(segment, cwd)
        for segment in SEPARATEURS.split(commande)
    )


def main() -> None:
    """Refuse ou soumet à validation la commande selon les règles ci-dessus."""
    entree = json.load(sys.stdin)
    commande = entree.get("tool_input", {}).get("command", "")
    agent = entree.get("agent_type") or ""

    for motif, raison in REFUS:
        if re.search(motif, commande):
            repondre("deny", raison)
    if installation_refusee(commande, Path(entree.get("cwd") or RACINE)):
        repondre("deny", RAISON_INSTALLATION)
    if agent in RELECTEURS and re.search(GIT_ECRITURE, commande):
        repondre("deny", f"L'agent {agent} ne modifie pas l'état du dépôt git.")
    cree_branche = re.search(r"git\s+(switch\s+-c|checkout\s+-b)\b", commande)
    if (
        re.search(r"\bgit\s+(commit|push)\b", commande)
        and not cree_branche
        and branche_courante() in ("main", "master")
    ):
        repondre(
            "deny",
            "Tu es sur main, qui est protégée : crée d'abord une branche "
            "(feat/…, fix/…, docs/…) (PLAN §8.1).",
        )
    if re.search(r"\bgit\s+commit\b", commande) and (tests := tests_indexes()):
        repondre(
            "ask",
            f"Ce commit contient des tests ({', '.join(tests)}) : seuls ceux qui protègent un "
            "calcul critique restent dans le dépôt (CLAUDE.md). Relis le diff et le message.",
        )
    for motif, raison in A_VALIDER:
        if re.search(motif, commande):
            repondre("ask", raison)


if __name__ == "__main__":
    main()
