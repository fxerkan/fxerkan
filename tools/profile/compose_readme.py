"""Compose the full profile README for a rendered theme folder.

Usage: compose_readme.py themes/<name>   (prints README.md to stdout)

Stacks every rendered slice into one seamless console, mirroring the original
layout: header, links row, stats, contribution-city, projects (2-up), stack,
writing rows, footer. Content comes from profile.json + data/*.json.
"""
import datetime, html, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
e = lambda s: html.escape(str(s), quote=True)


def main():
    prof = json.load(open(HERE / "profile.json"))
    stats = json.load(open(DATA / "stats.json"))
    articles = json.load(open(DATA / "articles.json"))
    links = prof["links"]
    lw = f"{100 // len(links)}%"

    out = ['<p align="center">']
    hd = prof["header"]
    site = hd.get("brand", "fxerkan.com")
    site_url = site if site.startswith("http") else f"https://{site}"
    demo_url = prof.get("demo_url", "https://fxerkan.github.io/fxerkan/")
    gh_url = f"https://github.com/{prof['username']}"
    medium_url = f"https://medium.com/@{prof.get('medium_user', prof['username'])}"
    # header image is a link to the site (clicking opens fxerkan.com, not the raw SVG)
    out.append(f'<a href="{e(site_url)}"><img src="./assets/header.svg" width="100%" align="top" alt="{e(hd["desc"])}"></a>')

    # 01 — projects (pinned repos), 2-up
    out.append(f'<a href="{e(gh_url)}?tab=repositories"><img src="./assets/projects.svg" width="100%" align="top" alt="Projects — pinned repositories"></a>')
    cards = []
    for p in prof["projects"]:
        alt = f'{p["name"]} — {p["tag"]}. {p["desc"]} {p["stack"].replace(" · ", ", ")}.'
        cards.append(f'<a href="{e(p["url"])}"><img src="./assets/card-{p["slug"]}.svg" width="50%" align="top" alt="{e(alt)}"></a>')
    for i in range(0, len(cards), 2):
        out.append("".join(cards[i:i + 2]))

    # 02 — contribution graphic
    if (DATA / "calendar.json").exists():
        cal = json.load(open(DATA / "calendar.json"))
        total = sum(n for _, n in cal)
        bd, bn = max(cal, key=lambda t: t[1])
        d = datetime.date.fromisoformat(bd)
        calt = (f"Contribution graphic for the last year ({total:,} contributions, busiest day {d:%B} {d.day} with {bn}). "
                f"Click for the live animated gallery with theme switching.")
        # the contribution image links to the live demo (animated, theme-switchable) — the style here rotates daily
        out.append(f'<a href="{e(demo_url)}"><img src="./assets/contribution-city.svg" width="100%" align="top" alt="{e(calt)}"></a>')

    # 03 — stats
    since = datetime.date.fromisoformat(stats["created_at"][:10])
    langs = ", ".join(k for k, _ in sorted(stats["languages"].items(), key=lambda kv: -kv[1])[:5])
    salt = (f'{stats["stars"]} total stars; {stats.get("contributions_year", 0)} contributions in {stats["year"]}, '
            f'{stats.get("contributions_all", 0)} all time; {stats["prs"]} pull requests ({stats["prs_merged"]} merged); '
            f'current streak {stats["streak_current"]} days, longest {stats["streak_longest"]}; {stats["followers"]} followers; '
            f'member since {since:%B %Y}. Top languages: {langs}.')
    out.append(f'<a href="{e(gh_url)}"><img src="./assets/stats.svg" width="100%" align="top" alt="Stats: {e(salt)}"></a>')

    # 04 — writing (canonical links point to Medium; cross-posted to DEV and coderlegion)
    if articles:
        out.append(f'<a href="{e(medium_url)}"><img src="./assets/writing.svg" width="100%" align="top" alt="Writing — articles on Medium, DEV and coderlegion"></a>')
        out.append("<!-- writing:start -->")
        for i, a in enumerate(articles[:5], 1):
            alt = (f'{a["title"]} — published {a["published_at"][:10]}, '
                   f'{a.get("reactions", 0)} reactions, {a.get("comments", 0)} comments')
            out.append(f'<a href="{e(a["url"])}"><img src="./assets/writing/post-{i}.svg" width="100%" align="top" alt="{e(alt)}"></a>')
        out.append("<!-- writing:end -->")
        medium = f'https://medium.com/@{e(prof.get("medium_user", prof["username"]))}'
        out.append(f'<a href="{medium}"><img src="./assets/writing/all-articles.svg" width="100%" align="top" alt="Read all articles on Medium"></a>')

    # 05 — stack
    sdesc = "Tech stack. " + " ".join(f"{c}: {', '.join(items)}." for c, items in prof["stack"])
    out.append(f'<a href="{e(site_url)}"><img src="./assets/stack.svg" width="100%" align="top" alt="{e(sdesc)}"></a>')

    # 06 — links / where to find me
    out.append(f'<a href="{e(site_url)}"><img src="./assets/links.svg" width="100%" align="top" alt="Links — where to find me"></a>')
    link_row = []
    for key, label, handle, url in links:
        fn = "dev" if key == "devdotto" else key
        link_row.append(f'<a href="{e(url)}"><img src="./assets/links/{fn}.svg" width="{lw}" align="top" alt="{e(label)}"></a>')
    out.append("".join(link_row))

    # footer → the full story at fxerkan.com (whole slice is a link)
    site = hd.get("brand", "fxerkan.com")
    site_url = site if site.startswith("http") else f"https://{site}"
    out.append(f'<a href="{e(site_url)}"><img src="./assets/footer.svg" width="100%" align="top" '
               f'alt="The rest of the story — full CV, certifications, experience and the apps I build at {e(site)}."></a>')
    out.append("</p>")
    readme = "\n".join(out)
    # cache-bust every asset URL by the data date so GitHub's image proxy (camo) refetches
    # on each refresh instead of serving a stale SVG (this is why updates weren't showing)
    ver = stats.get("updated", "")
    if ver:
        readme = re.sub(r'(src="\./assets/[^"]+?)"', rf'\1?v={ver}"', readme)
    print(readme)


if __name__ == "__main__":
    main()
