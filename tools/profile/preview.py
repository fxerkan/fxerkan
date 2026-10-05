"""Stitch a rendered theme's SVG slices into one full-page preview PNG.

Usage: preview.py themes/<name> out.png

Rasterizes each slice with rsvg-convert (2x) and composites them in README order:
full-width slices stacked, the links row and project cards laid out side by side,
all on the theme's background colour.
"""
import json, pathlib, subprocess, sys, tempfile

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
SCALE = 2
PAGEW = 880 * SCALE


def raster(svg: pathlib.Path, width: int) -> Image.Image:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t:
        subprocess.run(["rsvg-convert", "-w", str(width), str(svg), "-o", t.name], check=True)
        return Image.open(t.name).convert("RGBA")


def main():
    base = pathlib.Path(sys.argv[1])
    outp = pathlib.Path(sys.argv[2])
    assets = base / "assets"
    prof = json.load(open(HERE / "profile.json"))
    theme = json.load(open(HERE / "themes.json"))[base.name]
    bg = theme["bg"]

    links = [("dev" if k == "devdotto" else k) for k, *_ in prof["links"]]
    slugs = [p["slug"] for p in prof["projects"]]

    # each entry is a row: a list of (svg filename, svg-native width).
    # order mirrors compose_readme.py: header, projects, contribution, stats, writing, stack, links, footer
    rows = [[("header.svg", 880)]]
    rows.append([("projects.svg", 880)])                                   # 01
    for i in range(0, len(slugs), 2):
        rows.append([(f"card-{s}.svg", 440) for s in slugs[i:i + 2]])
    if (assets / "contribution-city.svg").exists():                        # 02
        rows.append([("contribution-city.svg", 880)])
    rows.append([("stats.svg", 880)])                                      # 03
    posts = sorted((assets / "writing").glob("post-*.svg")) if (assets / "writing").exists() else []
    if posts:                                                              # 04
        rows.append([("writing.svg", 880)])
        for p in posts:
            rows.append([(f"writing/{p.name}", 880)])
        rows.append([("writing/all-articles.svg", 880)])
    rows.append([("stack.svg", 880)])                                      # 05
    rows.append([("links.svg", 880)])                                      # 06
    rows.append([(f"links/{fn}.svg", 880 // len(links)) for fn in links])
    rows.append([("footer.svg", 880)])

    # rasterize and measure
    rendered = []
    for row in rows:
        imgs, x = [], 0
        for fn, w in row:
            img = raster(assets / fn, w * SCALE)
            imgs.append((img, x))
            x += img.width
        rendered.append((imgs, max(i.height for i, _ in imgs)))

    total_h = sum(h for _, h in rendered)
    page = Image.new("RGBA", (PAGEW, total_h), bg)
    y = 0
    for imgs, h in rendered:
        for img, x in imgs:
            page.alpha_composite(img, (x, y))
        y += h
    page.convert("RGB").save(outp)
    print(f"{outp} {page.width}x{page.height}")


if __name__ == "__main__":
    main()
