# CS-Pi project page

Project page for **CS-Pi: Constraint-Satisfying Flow Policy Sampling**
(CoRL 2026), live at <https://sumo048.github.io/CS-pi_site/>.

The page is an Astro site in [`site/`](site/) (see [`site/README.md`](site/README.md)
for running, editing and the theme). GitHub Actions builds it and deploys it to
GitHub Pages on every push to `main0` (`.github/workflows/astro.yml`); the
repository's **Settings → Pages → Source** must be **GitHub Actions**.

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
