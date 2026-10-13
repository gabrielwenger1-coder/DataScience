"""Contrôle des amendements du plan quand le pilote rend la main (hook SubagentStop).

Toute modification de docs/PLAN.md doit avoir sa ligne au journal des décisions (§13)
et rester légère. Si les choix fixés avant les résultats (§1.2 et §2) sont touchés,
le pilote doit le signaler et en donner la raison dans sa réponse.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
PLAN = "docs/PLAN.md"
SEUIL_LIGNES = 40  # lignes modifiées hors journal au-delà desquelles l'amendement n'est plus léger


def git(*arguments: str) -> subprocess.CompletedProcess:
    """Exécute une commande git dans le projet."""
    return subprocess.run(
        ["git", "-C", str(RACINE), *arguments], capture_output=True, text=True, check=False
    )


def debuts_de_section(texte: str) -> list[tuple[int, str]]:
    """Repère la ligne de début de chaque section numérotée (« ## 2. », « ### 2.4 »)."""
    debuts = []
    for numero, ligne in enumerate(texte.splitlines(), start=1):
        if titre := re.match(r"#{2,3} (\d+(?:\.\d+)?)[. ]", ligne):
            debuts.append((numero, titre.group(1)))
    return debuts


def section_de(numero: int, debuts: list[tuple[int, str]]) -> str:
    """Renvoie le numéro de la section qui contient la ligne donnée."""
    courante = ""
    for debut, section in debuts:
        if debut > numero:
            break
        courante = section
    return courante


def lignes_modifiees() -> list[tuple[str, str, str]]:
    """Liste (signe, section, texte) des lignes du plan modifiées depuis le dernier commit."""
    ancien = git("show", f"HEAD:{PLAN}")
    if ancien.returncode != 0:  # plan pas encore commité : rien à comparer
        return []
    debuts_ancien = debuts_de_section(ancien.stdout)
    debuts_nouveau = debuts_de_section((RACINE / PLAN).read_text())

    modifiees = []
    dans_un_bloc = False
    for ligne in git("diff", "-U0", "HEAD", "--", PLAN).stdout.splitlines():
        if bloc := re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", ligne):
            n_ancien, n_nouveau = int(bloc.group(1)), int(bloc.group(2))
            dans_un_bloc = True
        elif dans_un_bloc and ligne.startswith("-"):
            modifiees.append(("-", section_de(n_ancien, debuts_ancien), ligne[1:]))
            n_ancien += 1
        elif dans_un_bloc and ligne.startswith("+"):
            modifiees.append(("+", section_de(n_nouveau, debuts_nouveau), ligne[1:]))
            n_nouveau += 1
    return modifiees


def dans(section: str, parent: str) -> bool:
    """Vrai si la section est `parent` ou l'une de ses sous-sections."""
    return section == parent or section.startswith(parent + ".")


def main() -> None:
    """Vérifie la traçabilité et la taille des amendements, et signale les choix figés touchés."""
    entree = json.load(sys.stdin)
    modifiees = lignes_modifiees()
    hors_journal = [(signe, section) for signe, section, _ in modifiees if not dans(section, "13")]
    if not hors_journal:
        return
    nouvelles_entrees = [
        texte
        for signe, section, texte in modifiees
        if signe == "+" and dans(section, "13") and re.match(r"\|\s*\d", texte)
    ]
    figees = sorted({s for _, s in hors_journal if s == "1.2" or dans(s, "2")})

    # Chaque problème : (consigne renvoyée au pilote, avertissement affiché à l'étudiant).
    problemes = []
    if not nouvelles_entrees:
        problemes.append(
            (
                "Le plan a été modifié sans nouvelle ligne au journal des décisions (§13). "
                "Ajoute une ligne par amendement : date | décision | raison | auteur.",
                "plan modifié sans ligne au journal des décisions (§13).",
            )
        )
    if len(hors_journal) > SEUIL_LIGNES:
        problemes.append(
            (
                f"{len(hors_journal)} lignes du plan modifiées : un amendement doit rester léger. "
                "Réduis-le à l'essentiel, ou explique à l'étudiant pourquoi c'est impossible.",
                f"{len(hors_journal)} lignes du plan modifiées (amendement large).",
            )
        )
    if figees:
        sections = ", §".join(figees)
        problemes.append(
            (
                f"Tu as modifié des choix fixés avant les résultats (§{sections}). Termine ta "
                "réponse par un paragraphe « Choix figés modifiés » qui donne la raison, "
                "indépendante des résultats (PLAN §5.8).",
                f"choix fixés avant les résultats modifiés (§{sections}) : vérifie que la "
                "justification du pilote ne dépend pas des résultats.",
            )
        )
    if not problemes:
        return
    if not entree.get("stop_hook_active"):
        print("\n".join(consigne for consigne, _ in problemes), file=sys.stderr)
        sys.exit(2)
    # Second passage : le pilote rend la main et l'étudiant est prévenu.
    avertissement = "Pilote : " + " ".join(message for _, message in problemes)
    print(json.dumps({"systemMessage": avertissement}, ensure_ascii=False))


if __name__ == "__main__":
    main()
