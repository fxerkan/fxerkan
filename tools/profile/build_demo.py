"""Builds the live animated demo gallery under docs/ (served by GitHub Pages).

Renders every contribution style for every theme with the reduced-motion guard OFF,
so the gallery always animates (even if your OS has "reduce motion" on), and writes
docs/index.html with a theme switcher. The profile README links its contribution
image here, since GitHub respects reduce-motion and shows it static there.

Usage: build_demo.py              (reads data/*.json, writes docs/)
"""
import html as _html
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R          # noqa: E402
import city_variants as V   # noqa: E402

ROOT = HERE.parent.parent
DOCS = ROOT / "docs"
STYLES = ["cycle", "reactor", "metropolis", "circuit", "terrain", "classic", "rally"]
LABELS = {"cycle": "Cycle — all styles", "reactor": "Reactor", "metropolis": "Metropolis",
          "circuit": "Circuit", "terrain": "Terrain", "classic": "City", "rally": "Rally"}
BUILDERS = {"reactor": V.build_reactor, "metropolis": V.build_metropolis, "circuit": V.build_circuit,
            "terrain": V.build_terrain, "classic": R.build_city, "rally": V.build_rally,
            "cycle": V.build_cycle}


def page(themes):
    tkeys = list(themes)
    labels = {k: themes[k]["label"].split("—")[0].strip() for k in tkeys}
    btns = "".join(f'<button class="theme" data-theme="{k}"{" aria-current=\"true\"" if i == 0 else ""}>{_html.escape(labels[k])}</button>'
                   for i, k in enumerate(tkeys))
    figs = "".join(f'''<figure>
  <figcaption><span class="num">{i:02d}</span>{_html.escape(LABELS[s])}</figcaption>
  <img data-style="{s}" src="styles/{tkeys[0]}/{s}.svg" alt="{_html.escape(LABELS[s])} contribution style" loading="lazy">
</figure>''' for i, s in enumerate(STYLES))
    first = tkeys[0]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FXerkan · contribution styles</title>
<style>
  :root {{ --bg:#03040a; --fg:#c9d1d9; --dim:#6e7681; --accent:#00d9ff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
    font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
  header {{ position:sticky; top:0; z-index:5; backdrop-filter:blur(8px);
    background:color-mix(in srgb, var(--bg) 82%, transparent);
    border-bottom:1px solid #1b2230; padding:16px 20px; }}
  .wrap {{ max-width:912px; margin:0 auto; }}
  h1 {{ font-size:16px; margin:0 0 2px; letter-spacing:1px; }}
  h1 .cy {{ color:var(--accent); }}
  .sub {{ color:var(--dim); font-size:12px; margin:0 0 12px; }}
  .themes {{ display:flex; gap:8px; flex-wrap:wrap; }}
  button.theme {{ cursor:pointer; font:inherit; font-size:12px; letter-spacing:1px;
    color:var(--fg); background:#0b111b; border:1px solid #27303f; border-radius:7px; padding:7px 14px; }}
  button.theme[aria-current="true"] {{ border-color:var(--accent); color:var(--accent);
    box-shadow:0 0 0 1px var(--accent) inset, 0 0 14px -4px var(--accent); }}
  main {{ max-width:912px; margin:0 auto; padding:24px 16px 80px; }}
  figure {{ margin:0 0 30px; }}
  figcaption {{ font-size:12px; letter-spacing:2px; text-transform:uppercase; color:var(--dim);
    margin:0 0 8px; display:flex; gap:10px; align-items:center; }}
  .num {{ color:var(--accent); opacity:.6; }}
  img {{ width:100%; height:auto; display:block; border:1px solid #141b26; border-radius:10px; }}
  footer {{ max-width:912px; margin:0 auto; padding:0 16px 60px; color:var(--dim); font-size:12px; }}
  a {{ color:var(--accent); }}
</style>
</head>
<body>
<header><div class="wrap">
  <h1><span class="cy">~/</span>contribution-styles <span style="color:var(--dim)">// live &amp; animated</span></h1>
  <p class="sub">The same year of contributions, seven ways. On the GitHub profile the image is static and
  rotates daily — here every style animates. Pick a palette:</p>
  <div class="themes">{btns}</div>
</div></header>
<main>{figs}</main>
<footer>Generated from <a href="https://github.com/fxerkan/fxerkan">fxerkan/fxerkan</a> ·
  <a href="https://fxerkan.com">fxerkan.com</a></footer>
<script>
  const themes = {json.dumps(tkeys)};
  let cur = {json.dumps(first)};
  function setTheme(t) {{
    cur = t;
    document.querySelectorAll('img[data-style]').forEach(img => {{
      img.src = 'styles/' + t + '/' + img.dataset.style + '.svg';
    }});
    document.querySelectorAll('button.theme').forEach(b =>
      b.setAttribute('aria-current', b.dataset.theme === t ? 'true' : 'false'));
  }}
  document.querySelectorAll('button.theme').forEach(b =>
    b.addEventListener('click', () => setTheme(b.dataset.theme)));
</script>
</body>
</html>
"""


def main():
    themes = json.load(open(HERE / "themes.json"))
    cal = json.load(open(HERE / "data" / "calendar.json"))
    upd = json.load(open(HERE / "data" / "stats.json"))["updated"]
    R.MOTION_GUARD = False
    try:
        for tname, t in themes.items():
            R.apply_theme(t)
            out = DOCS / "styles" / tname
            out.mkdir(parents=True, exist_ok=True)
            for s in STYLES:
                (out / f"{s}.svg").write_text(BUILDERS[s](cal, upd))
    finally:
        R.MOTION_GUARD = True
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(page(themes))
    (DOCS / ".nojekyll").write_text("")
    print(f"demo gallery -> {DOCS} ({len(themes)} themes x {len(STYLES)} styles)")


if __name__ == "__main__":
    main()
