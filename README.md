# CS-Pi project page

Project page for **CS-Pi: Constraint-Satisfying Flow Policy Sampling**
(CoRL 2026), live at <https://sumo048.github.io/CS-pi_site/>.

The page is an Astro site in [`site/`](site/) (see [`site/README.md`](site/README.md)
for running, editing and the theme). On every push to `main0`, GitHub Actions
builds it and commits the output to the `gh-pages` branch
(`.github/workflows/astro.yml`), which GitHub Pages serves. Repository setting:
**Settings → Pages → Source: Deploy from a branch → `gh-pages` / `(root)`**.
Don't edit `gh-pages` by hand; it is overwritten on every deploy.

| Path | What it is |
|------|------------|
| `site/` | The Astro site: content in `site/src/paper.mdx` and `site/src/data/`. |
| `viz/` | Source rollout GIFs for the explorer and the spheres gallery. |
| `assets/` | Source figures, story GIFs and hardware clips. |
| `tools/convert_media.py` | GIF → MP4 + WebM + poster into `site/public/media/`. |
| `tools/build_manifest.py` | Writes `site/src/data/media_manifest.json` from `viz/`. |

```bash
cd site && npm install && npm run dev   # http://localhost:4321/CS-pi_site/
```
