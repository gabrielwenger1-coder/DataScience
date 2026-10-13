"""Garde-fous avant toute écriture de fichier par Claude (hook PreToolUse).

Chaque règle traduit une consigne de PLAN.md ou de CLAUDE.md. Le hook répond « deny »
(refus : Claude doit corriger) ou « ask » (l'étudiant valide), avec la raison.
Sans réponse, l'écriture suit les permissions habituelles.
"""

import json
import os
import re
import sys
from fnmatch import fnmatch
from pathlib import Path

import budget_tests

RACINE = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

# Le plan, les consignes et le harness lui-même : un agent ne doit pas pouvoir
# assouplir les règles qui le contrôlent. Seul l'agent pilote touche au plan.
PROTEGES = ("PLAN.md", "docs/PLAN.md", "CLAUDE.md", "ruff.toml", ".claude/*")
PLANS = ("docs/PLAN.md", "PLAN.md")
FICHIERS_DU_PILOTE = (*PLANS, ".claude/pilotage.md")
CARNET = ".claude/lecons.md"

MODULES = (
    "__init__",
    "config",
    "stockage",
    "collecte",
    "nettoyage",
    "geo",
    "accessibilite",
    "analyse",
    "figures",
    "pipeline",
)
# Arborescence prévue par PLAN §7. Créer un fichier ailleurs demande une validation.
ARBORESCENCE = (
    "README.md",
    "pyproject.toml",
    "uv.lock",
    ".python-version",
    ".gitignore",
    ".pre-commit-config.yaml",
    "_quarto.yml",
    "rapport.ipynb",
    "docs/dictionnaire_variables.md",
    "tests/*",
    "notebooks/exploration/*.ipynb",
    "data/*",
    *(f"src/cadres_lycees/{module}.py" for module in MODULES),
)

SECRETS = re.compile(
    r"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}"
    r"|hvs\.[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
    r"|(?i:aws_secret_access_key|aws_session_token)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{16,}"
)
EN_DUR = re.compile(r"https?://|s3://|/home/onyxia")
CONTOURNEMENTS = re.compile(
    r"#\s*noqa|#\s*type:\s*ignore|#\s*pragma:\s*no cover|pytest\.mark\.(skip|xfail)"
)


def repondre(decision: str, raisons: list[str]) -> None:
    """Transmet la décision à Claude Code et termine le hook."""
    sortie = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": " ".join(raisons),
        }
    }
    print(json.dumps(sortie, ensure_ascii=False))
    sys.exit(0)


def correspond(chemin: str, motifs: tuple[str, ...]) -> bool:
    """Indique si le chemin relatif correspond à l'un des motifs (fnmatch, `*` inclut `/`)."""
    return any(fnmatch(chemin, motif) for motif in motifs)


def texte_ecrit(params: dict) -> str:
    """Rassemble le texte que l'outil s'apprête à écrire, quel que soit l'outil."""
    morceaux = [params.get(cle) or "" for cle in ("content", "new_string", "new_source")]
    morceaux += [edit.get("new_string", "") for edit in params.get("edits", [])]
    return "\n".join(morceaux)


def est_prose(source: str) -> bool:
    """Vrai si une cellule Markdown contient autre chose que des titres."""
    lignes = [ligne.strip() for ligne in source.splitlines() if ligne.strip()]
    return any(not ligne.startswith("#") for ligne in lignes)


def contenu_apres(chemin: str, outil: str, params: dict) -> str:
    """Renvoie le contenu du fichier une fois l'écriture faite (Write, Edit ou MultiEdit)."""
    if outil == "Write":
        return params.get("content", "")
    fichier = RACINE / chemin
    contenu = fichier.read_text(errors="replace") if fichier.exists() else ""
    for modification in params.get("edits") or [params]:
        contenu = contenu.replace(
            modification.get("old_string", ""), modification.get("new_string", ""), 1
        )
    return contenu


def raisons_tests(chemin: str, outil: str, params: dict, existe: bool) -> list[str]:
    """Liste les raisons de soumettre à l'étudiant l'ajout ou l'extension d'un test."""
    if not chemin.startswith("tests/"):
        return []
    raisons = []
    if not existe and chemin not in budget_tests.TESTS_PREVUS:
        raisons.append(
            f"Nouveau fichier dans tests/ : {chemin}. Seuls les tests qui protègent un calcul "
            "critique restent dans le dépôt (CLAUDE.md) ; une vérification ponctuelle va dans "
            f"{budget_tests.DOSSIER_ESSAIS}/."
        )
    nombre = budget_tests.nb_tests(contenu_apres(chemin, outil, params))
    if nombre > budget_tests.MAX_TESTS_PAR_FICHIER:
        raisons.append(
            f"{chemin} aurait {nombre} tests (budget : {budget_tests.MAX_TESTS_PAR_FICHIER} "
            "par fichier) : ne garde que les plus importants."
        )
    return raisons


def raison_refus(chemin: str, texte: str, agent: str) -> str | None:
    """Renvoie la raison de refuser l'écriture, ou None si rien ne l'interdit."""
    if SECRETS.search(texte):
        return (
            "Le contenu ressemble à un secret (jeton, clé). Aucun secret dans le dépôt : "
            "lis-le depuis les variables d'environnement (PLAN §7)."
        )
    if agent == "pilote":
        if chemin in FICHIERS_DU_PILOTE:
            return None
        return "Le pilote ne modifie que docs/PLAN.md et .claude/pilotage.md : ni code, ni harness."
    if chemin in PLANS:
        return (
            "Seul l'agent pilote modifie le plan, après confrontation avec le correcteur et "
            "validation de l'étudiant (/pilotage)."
        )
    if correspond(chemin, PROTEGES) and chemin != CARNET:
        return (
            f"{chemin} fait partie du harness : Claude ne le modifie pas. "
            "Propose le changement à l'étudiant."
        )
    if agent == "testeur" and not chemin.startswith("tests/"):
        return "L'agent testeur n'écrit que dans tests/."
    if fnmatch(chemin, "src/*.py") and not chemin.endswith("/config.py") and EN_DUR.search(texte):
        return (
            "URL ou chemin en dur hors de config.py (PLAN §8.2). Ajoute la constante dans "
            "src/cadres_lycees/config.py et importe-la."
        )
    return None


def raisons_validation(chemin: str, texte: str, agent: str, outil: str, params: dict) -> list[str]:
    """Liste les raisons de soumettre l'écriture à l'étudiant (liste vide sinon)."""
    existe = (RACINE / chemin).exists()
    raisons = []
    if chemin == CARNET:
        raisons.append("Ajout au carnet de leçons : l'étudiant valide la leçon proposée.")
    if agent == "pilote" and chemin in PLANS:
        raisons.append(
            "Amendement du plan par le pilote : relis le diff. Chaque amendement validé a sa "
            "ligne dans le journal des décisions (§13)."
        )
    if CONTOURNEMENTS.search(texte):
        raisons.append(
            "Désactivation d'un contrôle (noqa, type: ignore, skip, xfail) : "
            "elle doit être justifiée."
        )
    if not existe and not correspond(chemin, ARBORESCENCE):
        raisons.append(
            f"Nouveau fichier hors de l'arborescence prévue (PLAN §7) : {chemin}. "
            "Un module utils.py ou un fichier de notes est rarement justifié ; une vérification "
            f"ponctuelle va dans {budget_tests.DOSSIER_ESSAIS}/."
        )
    if existe and chemin.startswith("tests/") and agent != "testeur":
        raisons.append(
            "Modification d'un test existant : vérifier qu'on ne l'adapte pas au "
            "code pour le faire passer."
        )
    raisons += raisons_tests(chemin, outil, params, existe)
    if chemin == "rapport.ipynb" and outil == "Write" and existe:
        raisons.append("Réécriture complète de rapport.ipynb : passer par NotebookEdit.")
    if (
        chemin == "rapport.ipynb"
        and params.get("cell_type") == "markdown"
        and est_prose(params.get("new_source", ""))
    ):
        raisons.append(
            "Texte rédigé dans le rapport : les interprétations et la rédaction "
            "sont écrites par le groupe (PLAN §8.3). Claude ne pose que des titres."
        )
    return raisons


def main() -> None:
    """Refuse l'écriture, la soumet à l'étudiant, ou la laisse suivre son cours."""
    entree = json.load(sys.stdin)
    outil = entree.get("tool_name", "")
    params = entree.get("tool_input", {})
    agent = entree.get("agent_type") or ""

    absolu = Path(params.get("file_path") or params.get("notebook_path") or "")
    absolu = (RACINE / absolu).resolve() if not absolu.is_absolute() else absolu.resolve()
    if not absolu.is_relative_to(RACINE):
        return
    chemin = absolu.relative_to(RACINE).as_posix()
    texte = texte_ecrit(params)

    if raison := raison_refus(chemin, texte, agent):
        repondre("deny", [raison])
    if raisons := raisons_validation(chemin, texte, agent, outil, params):
        repondre("ask", raisons)


if __name__ == "__main__":
    main()
