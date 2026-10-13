#!/usr/bin/env bash
# Contrôle complet avant rendu : ce que fera le correcteur (installation neuve, exécution
# du notebook) et l'hygiène du dépôt (données, secrets, URL en dur).
# Usage : bash .claude/scripts/verifier.sh [--rapide]   (--rapide : sans exécuter rapport.ipynb)
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

rapide=false
[[ "${1:-}" == "--rapide" ]] && rapide=true
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
resultats=()
echecs=0

# etape <nom> <commande...> : lance la commande et n'affiche sa sortie qu'en cas d'échec.
etape() {
    local nom=$1
    shift
    if "$@" >"$tmp/sortie" 2>&1; then
        resultats+=("OK      $nom")
    else
        resultats+=("ÉCHEC   $nom")
        echecs=$((echecs + 1))
        echo "--- $nom ---"
        tail -n 40 "$tmp/sortie"
        echo
    fi
}
saute() { resultats+=("SAUTÉ   $1 ($2)"); }

# Les contrôles d'hygiène échouent (code 1) dès qu'ils trouvent quelque chose.
aucune_donnee_suivie() {
    ! git ls-files | grep -Ei '\.(csv|parquet|xlsx?|zip|gpkg|shp|geojson|feather)$'
}
aucun_gros_fichier() {
    ! git ls-files -z | xargs -0 -r du -k 2>/dev/null | awk '$1 > 5120 { print $2 " (" $1 " ko)"; found = 1 } END { exit !found }'
}
aucun_secret() {
    # Noms de fichiers seulement : on n'affiche jamais le secret lui-même.
    ! git ls-files | grep -E '(^|/)\.env' &&
        ! git grep -lIE 'ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|hvs\.[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|BEGIN [A-Z ]*PRIVATE KEY|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.'
}
aucune_url_en_dur() {
    [[ ! -d src ]] || ! grep -rnE --include='*.py' 'https?://|s3://' src | grep -v 'src/cadres_lycees/config.py'
}
notebooks_sans_sorties() {
    local notebooks
    mapfile -t notebooks < <(git ls-files '*.ipynb')
    ((${#notebooks[@]} == 0)) || uvx nb-clean check "${notebooks[@]}"
}

if [[ -f pyproject.toml ]]; then
    # Environnement neuf construit uniquement depuis uv.lock, comme chez le correcteur.
    export UV_PROJECT_ENVIRONMENT="$tmp/venv"
    etape "uv.lock cohérent avec pyproject.toml" uv lock --check
    etape "installation depuis uv.lock (environnement neuf)" uv sync --locked
    if uv run --no-sync ruff --version >/dev/null 2>&1; then ruff=(uv run --no-sync ruff); else ruff=(uvx ruff); fi
    etape "ruff check" "${ruff[@]}" check .
    etape "ruff format" "${ruff[@]}" format --check .
    if [[ -d tests ]]; then etape "pytest (tous les tests)" uv run --no-sync pytest -q; else saute "pytest" "pas de dossier tests/"; fi
    if [[ ! -f rapport.ipynb ]]; then
        saute "exécution de rapport.ipynb" "fichier absent"
    elif $rapide; then
        saute "exécution de rapport.ipynb" "--rapide"
    else
        etape "exécution de rapport.ipynb de bout en bout" uv run --no-sync jupyter nbconvert \
            --to notebook --execute rapport.ipynb --output-dir "$tmp" --ExecutePreprocessor.timeout=3600
    fi
else
    saute "installation, ruff, pytest, notebook" "pas encore de pyproject.toml (ticket T0)"
fi
etape "notebooks commités sans sorties (nb-clean)" notebooks_sans_sorties
etape "aucune donnée suivie par Git" aucune_donnee_suivie
etape "aucun fichier suivi de plus de 5 Mo" aucun_gros_fichier
etape "aucun secret ni .env suivi par Git" aucun_secret
etape "aucune URL en dur hors de config.py" aucune_url_en_dur
# Le budget de tests est un avertissement : l'étudiant peut avoir validé un test de plus.
if bilan=$(python3 .claude/hooks/budget_tests.py 2>&1); then
    resultats+=("OK      $bilan")
else
    resultats+=("AVERT   $bilan")
fi

echo "=== Récapitulatif ==="
printf '%s\n' "${resultats[@]}"
((echecs == 0))
