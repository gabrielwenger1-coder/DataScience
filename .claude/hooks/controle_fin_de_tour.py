"""Contrôle de fin de tour (hook Stop) : ruff et pytest sur le travail en cours.

Quand Claude veut rendre la main alors que des fichiers Python ont changé, le hook
formate ces fichiers, les passe à ruff, lance les tests rapides et, en cas d'échec,
renvoie Claude corriger une fois. Si l'échec persiste, l'étudiant est prévenu.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
SEUIL_DIFF = 400  # lignes ajoutées au-delà desquelles un ticket mérite d'être découpé


def lancer(commande: list[str], delai: int = 120) -> tuple[int, str]:
    """Exécute une commande depuis la racine du projet et renvoie (code, sortie)."""
    try:
        resultat = subprocess.run(
            commande, cwd=RACINE, capture_output=True, text=True, timeout=delai, check=False
        )
    except subprocess.TimeoutExpired:
        return 1, f"{' '.join(commande)} : délai de {delai} s dépassé."
    return resultat.returncode, (resultat.stdout + resultat.stderr).rstrip()


def fichiers_modifies() -> list[str]:
    """Liste les fichiers Python et notebooks modifiés ou nouveaux, hors brouillons."""
    _, sortie = lancer(["git", "status", "--porcelain", "--untracked-files=all"])
    chemins = [ligne[3:].split(" -> ")[-1] for ligne in sortie.splitlines()]
    return [
        chemin
        for chemin in chemins
        if chemin.endswith((".py", ".ipynb"))
        and not chemin.startswith("notebooks/exploration/")
        and (RACINE / chemin).exists()
    ]


def commande_ruff() -> list[str] | None:
    """Trouve ruff : celui du projet, sinon celui du système, sinon via uvx."""
    if (RACINE / ".venv/bin/ruff").exists():
        return [str(RACINE / ".venv/bin/ruff")]
    if shutil.which("ruff"):
        return ["ruff"]
    if shutil.which("uvx"):
        return ["uvx", "ruff"]
    return None


def lignes_ajoutees() -> int:
    """Compte les lignes Python ajoutées depuis le dernier commit, fichiers nouveaux compris."""
    _, numstat = lancer(["git", "diff", "--numstat", "HEAD", "--", "*.py"])
    total = sum(int(ligne.split()[0]) for ligne in numstat.splitlines() if ligne[0].isdigit())
    _, nouveaux = lancer(["git", "ls-files", "--others", "--exclude-standard"])
    for chemin in nouveaux.splitlines():
        if chemin.endswith(".py"):
            total += len((RACINE / chemin).read_text(errors="replace").splitlines())
    return total


def main() -> None:
    """Lance les contrôles et décide si Claude peut rendre la main."""
    entree = json.load(sys.stdin)
    fichiers = fichiers_modifies()
    if not fichiers:
        return

    problemes = []
    ruff = commande_ruff()
    if ruff:
        lancer([*ruff, "format", "--quiet", *fichiers])
        code, sortie = lancer([*ruff, "check", "--output-format", "concise", *fichiers])
        if code != 0:
            problemes.append(f"ruff check :\n{sortie[-2000:]}")
    if (RACINE / "tests").is_dir() and (RACINE / ".venv/bin/python").exists():
        options = ["-q", "-x", "--tb=short", "-m", "not reseau"]
        code, sortie = lancer([".venv/bin/python", "-m", "pytest", *options], delai=240)
        if code not in (0, 5):  # 5 : aucun test collecté
            problemes.append(f"pytest (tests marqués « reseau » exclus) :\n{sortie[-2500:]}")

    message = None
    if (ajout := lignes_ajoutees()) > SEUIL_DIFF:
        message = (
            f"{ajout} lignes ajoutées depuis le dernier commit : pense à découper "
            "(commits petits et fréquents, PLAN §8.1)."
        )
    if problemes and not entree.get("stop_hook_active"):
        print(
            "Contrôles de fin de tour en échec. Corrige-les avant de rendre la main, "
            "ou explique à l'étudiant pourquoi ils sortent du ticket. Ne désactive "
            "aucune règle et ne modifie pas un test pour le faire passer.\n\n"
            + "\n\n".join(problemes),
            file=sys.stderr,
        )
        sys.exit(2)
    if problemes:
        message = "Contrôles de fin de tour toujours en échec :\n" + "\n\n".join(problemes)[:800]
    if message:
        print(json.dumps({"systemMessage": message}, ensure_ascii=False))


if __name__ == "__main__":
    main()
