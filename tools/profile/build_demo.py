"""Builds the live demo under docs/ (served by GitHub Pages).

For every theme it renders the WHOLE profile — every slice (rails, boxes, icons,
cards, links, footer) in that theme's colours — with the reduced-motion guard OFF,
and the contribution graphic as the animated cycle in the middle. docs/index.html
shows the full profile and a palette switcher that recolours everything live.
(GitHub respects reduce-motion on the profile README, so there it stays static and
the style rotates daily — this page is where it's always animated and theme-able.)

Usage: build_demo.py              (reads data/*.json + profile.json, writes docs/)
"""
import html as _html
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R          # noqa: E402

ROOT = HERE.parent.parent
DOCS = ROOT / "docs"


def page(themes, prof, articles):
    tkeys = list(themes)
    labels = {k: themes[k]["label"].split("—")[0].strip() for k in tkeys}
    first = tkeys[0]
    slugs = [p["slug"] for p in prof["projects"]]
    links = [("dev" if l[0] == "devdotto" else l[0]) for l in prof["links"]]
    nposts = min(5, len(articles))

    def img(slice_path):
        return f'<img data-slice="{slice_path}" src="profile/{first}/{slice_path}" loading="lazy" alt="">'

    rows = [img("header.svg"), img("projects.svg")]
    rows.append('<div class="grid2">' + "".join(f'<div>{img(f"card-{s}.svg")}</div>' for s in slugs) + "</div>")
    rows.append(img("contribution-city.svg"))                  # animated cycle
    rows.append(img("stats.svg"))
    if nposts:
        rows.append(img("writing.svg"))
        rows += [img(f"writing/post-{i}.svg") for i in range(1, nposts + 1)]
        rows.append(img("writing/all-articles.svg"))
    rows.append(img("stack.svg"))
    rows.append(img("links.svg"))
    rows.append('<div class="lrow">' + "".join(f'<div>{img(f"links/{fn}.svg")}</div>' for fn in links) + "</div>")
    rows.append(img("footer.svg"))
    profile = "\n".join(rows)
    btns = "".join(f'<button class="theme" data-theme="{k}"{" aria-current=\"true\"" if i == 0 else ""}>{_html.escape(labels[k])}</button>'
                   for i, k in enumerate(tkeys))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FXerkan · live profile</title>
<style>
  :root {{ --bg:#05060c; --fg:#c9d1d9; --dim:#6e7681; --accent:#00d9ff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
    font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
  header {{ position:sticky; top:0; z-index:5; backdrop-filter:blur(9px);
    background:color-mix(in srgb, var(--bg) 80%, transparent);
    border-bottom:1px solid #1b2230; padding:14px 18px; }}
  .wrap {{ max-width:912px; margin:0 auto; }}
  h1 {{ font-size:15px; margin:0 0 2px; letter-spacing:1px; }}
  h1 .cy {{ color:var(--accent); }}
  .sub {{ color:var(--dim); font-size:12px; margin:0 0 11px; max-width:760px; }}
  .themes {{ display:flex; gap:8px; flex-wrap:wrap; }}
  button.theme {{ cursor:pointer; font:inherit; font-size:12px; letter-spacing:.5px;
    color:var(--fg); background:#0b111b; border:1px solid #27303f; border-radius:7px; padding:7px 13px; }}
  button.theme[aria-current="true"] {{ border-color:var(--accent); color:var(--accent);
    box-shadow:0 0 0 1px var(--accent) inset, 0 0 14px -4px var(--accent); }}
  main {{ max-width:880px; margin:0 auto; padding:0 8px 70px; }}
  main img {{ width:100%; height:auto; display:block; }}
  .grid2 {{ display:flex; }} .grid2 > div {{ width:50%; }}
  .lrow {{ display:flex; }} .lrow > div {{ flex:1; }}
  footer {{ max-width:880px; margin:0 auto; padding:18px 10px 60px; color:var(--dim); font-size:12px; }}
  a {{ color:var(--accent); }}
</style>
</head>
<body>
<header><div class="wrap">
  <h1><span class="cy">~/</span>live-profile <span style="color:var(--dim)">// animated · theme-switchable</span></h1>
  <p class="sub">The whole FXerkan profile, rendered live in each palette — rails, cards, icons and all —
  with the contribution graphic cycling through every style in the middle. On GitHub the profile is static
  (GitHub honours reduce-motion) and its style rotates daily; here it always animates. Pick a palette:</p>
  <div class="themes">{btns}</div>
</div></header>
<main>{profile}</main>
<footer>Generated from <a href="https://github.com/fxerkan/fxerkan">fxerkan/fxerkan</a> ·
  <a href="https://fxerkan.com">fxerkan.com</a></footer>
<script>
  function setTheme(t) {{
    document.querySelectorAll('img[data-slice]').forEach(i => {{ i.src = 'profile/' + t + '/' + i.dataset.slice; }});
    document.querySelectorAll('button.theme').forEach(b => b.setAttribute('aria-current', b.dataset.theme === t ? 'true' : 'false'));
  }}
  document.querySelectorAll('button.theme').forEach(b => b.addEventListener('click', () => setTheme(b.dataset.theme)));
</script>
</body>
</html>
"""


def main():
    themes = json.load(open(HERE / "themes.json"))
    prof = json.load(open(HERE / "profile.json"))
    articles = json.load(open(HERE / "data" / "articles.json"))
    if (DOCS / "profile").exists():
        shutil.rmtree(DOCS / "profile")
    R.MOTION_GUARD = False
    try:
        for tname in themes:                                   # full profile per theme (contribution = animated cycle)
            sys.argv = ["render", "--out", str(DOCS / "profile" / tname), "--theme", tname, "--city", "cycle"]
            R.main()
    finally:
        R.MOTION_GUARD = True
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(page(themes, prof, articles))
    (DOCS / ".nojekyll").write_text("")
    print(f"demo -> {DOCS} (full profile x {len(themes)} themes)")


if __name__ == "__main__":
    main()
