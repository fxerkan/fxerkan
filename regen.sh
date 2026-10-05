#!/usr/bin/env bash
# Regenerate the contribution-city SVG from your live GitHub data.
# Usage: ./regen.sh            (fetch fresh data + render)
#        ./regen.sh --render   (re-render only, e.g. after editing render.py)
#        THEME=matrix CITY=metropolis ./regen.sh --render   (pick theme + city)
set -euo pipefail
cd "$(dirname "$0")"

[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -q fonttools==4.62.1 brotli==1.2.0; }

if [ "${1:-}" != "--render" ]; then
  GITHUB_TOKEN="$(gh auth token)" .venv/bin/python tools/profile/fetch.py
fi

THEME="${THEME:-cyberpunk}" CITY="${CITY:-cycle}" .venv/bin/python - <<'PY'
import os, sys, json, pathlib
sys.path.insert(0, "tools/profile")
import render as r, city_variants as v
r.apply_theme(json.load(open("tools/profile/themes.json"))[os.environ["THEME"]])
cal = json.load(open("tools/profile/data/calendar.json"))
stats = json.load(open("tools/profile/data/stats.json"))
builders = {"classic": r.build_city, "metropolis": v.build_metropolis, "reactor": v.build_reactor,
            "circuit": v.build_circuit, "terrain": v.build_terrain, "rally": v.build_rally,
            "cycle": v.build_cycle}
pathlib.Path("assets").mkdir(exist_ok=True)
pathlib.Path("assets/contribution-city.svg").write_text(builders[os.environ["CITY"]](cal, stats["updated"]))
print(f"rendered assets/contribution-city.svg [theme={os.environ['THEME']} city={os.environ['CITY']}]")
PY

# preview PNG (optional, needs rsvg-convert: brew install librsvg)
command -v rsvg-convert >/dev/null && \
  rsvg-convert -w 1400 -b "#0d1117" assets/contribution-city.svg -o assets/contribution-city.png && \
  echo "preview -> assets/contribution-city.png" || true
