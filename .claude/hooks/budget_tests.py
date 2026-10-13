"""Budget des tests conservés dans le dépôt, partagé par les hooks et verifier.sh.

Le plan (§7) ne prévoit que `tests/test_accessibilite.py` et `tests/test_geo.py`. Une
vérification ponctuelle va hors du dépôt, et un contrôle de données est un `assert` dans le
pipeline : seuls les tests qui protègent un calcul critique restent dans `tests/`.

Lancé seul, le module affiche le bilan et renvoie 1 si le budget est dépassé.
"""

import re
import sys
from pathlib import Path

DOSSIER_ESSAIS = "/tmp/essais"
TESTS_PREVUS = ("tests/test_accessibilite.py", "tests/test_geo.py", "tests/conftest.py")
MAX_FICHIERS = 3
MAX_TESTS_PAR_FICHIER = 6
FONCTION_DE_TEST = re.compile(r"^\s*(?:async\s+)?def test_\w+", re.MULTILINE)


def nb_tests(texte: str) -> int:
    """Compte les fonctions de test d'un fichier Python."""
    return len(FONCTION_DE_TEST.findall(texte))


def tests_du_depot(racine: Path) -> dict[str, int]:
    """Renvoie le nombre de tests de chaque fichier test_*.py de `tests/`."""
    fichiers = sorted(racine.glob("tests/**/test_*.py"))
    return {
        fichier.relative_to(racine).as_posix(): nb_tests(fichier.read_text(errors="replace"))
        for fichier in fichiers
    }


def depassements(racine: Path) -> str | None:
    """Décrit les dépassements du budget, ou renvoie None s'il est respecté."""
    tests = tests_du_depot(racine)
    problemes = []
    if len(tests) > MAX_FICHIERS:
        problemes.append(f"{len(tests)} fichiers de test (budget : {MAX_FICHIERS})")
    for fichier, nombre in tests.items():
        if nombre > MAX_TESTS_PAR_FICHIER:
            problemes.append(f"{fichier} : {nombre} tests (budget : {MAX_TESTS_PAR_FICHIER})")
    return "; ".join(problemes) or None


def main() -> None:
    """Affiche le bilan du dossier courant et renvoie 1 si le budget est dépassé."""
    racine = Path.cwd()
    tests = tests_du_depot(racine)
    resume = f"tests dans le dépôt : {len(tests)} fichier(s), {sum(tests.values())} test(s)"
    if probleme := depassements(racine):
        print(f"{resume}. Budget dépassé : {probleme}")
        sys.exit(1)
    print(f"{resume} (budget : {MAX_FICHIERS} fichiers, {MAX_TESTS_PAR_FICHIER} tests chacun)")


if __name__ == "__main__":
    main()
