#!/usr/bin/env bash
# Render every theme into themes/<name>/assets, write a README per theme,
# and stitch a full-page preview PNG (themes/<name>/preview.png).
# Usage: ./build-themes.sh [--no-fetch]   (themes come from tools/profile/themes.json)
#        CITY=metropolis ./build-themes.sh --no-fetch   (pick the city rendering)
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -q fonttools==4.62.1 brotli==1.2.0; }

[ "${1:-}" = "--no-fetch" ] || GITHUB_TOKEN="$(gh auth token)" $PY tools/profile/fetch.py

THEMES=$($PY -c "import json;print(' '.join(json.load(open('tools/profile/themes.json'))))")

for T in $THEMES; do
  OUT="themes/$T/assets"
  mkdir -p "$OUT"
  $PY tools/profile/render.py --out "$OUT" --theme "$T" --city "${CITY:-cycle}"
  # README that stacks every slice into one seamless console (relative to themes/<T>/)
  $PY tools/profile/compose_readme.py "themes/$T" > "themes/$T/README.md"
  # full-page preview PNG
  $PY tools/profile/preview.py "themes/$T" "themes/$T/preview.png"
  echo "theme $T -> themes/$T/{assets,README.md,preview.png}"
done
