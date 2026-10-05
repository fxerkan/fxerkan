# contribution-city — FXerkan profile console

Full "cyberpunk console" GitHub profile (header, links, stats, contribution-city,
projects, stack, writing, footer) rendered as stacked SVG slices — in 3 themes.

| theme | concept | preview |
|-------|---------|---------|
| `cyberpunk` | neon cyan / magenta | [themes/cyberpunk/preview.png](themes/cyberpunk/preview.png) |
| `matrix` | green phosphor | [themes/matrix/preview.png](themes/matrix/preview.png) |
| `f1` | Ferrari red / pit amber | [themes/f1/preview.png](themes/f1/preview.png) |

## Edit & rebuild

- **Content** → `tools/profile/profile.json` (name, links, projects, stack, taglines)
- **Themes / colors** → `tools/profile/themes.json` (add a theme = add a key)
- **Layout / shapes** → `tools/profile/render.py`

```bash
./build-themes.sh            # fetch live GitHub data + render all themes + previews
./build-themes.sh --no-fetch # re-render only (after editing json/py)
```

Each run writes `themes/<name>/{assets/*.svg, README.md, preview.png}`.
Data is fetched with your `gh` token (injected via env, never printed).

## Publish (when ready)

1. Pick a theme folder, e.g. `themes/cyberpunk`.
2. Create a repo named **`fxerkan/fxerkan`** (special profile repo).
3. Copy that theme's `assets/` + `README.md` to the repo root, plus `tools/` + `.github/workflows/update-profile.yml` to auto-refresh daily.
4. Push. The workflow re-fetches and re-renders every day (fix its `--theme` flag to your pick).

> `.github/workflows/update-profile.yml` currently renders into `assets/` with the default theme; set `--theme <name>` on its render step to lock your choice.
