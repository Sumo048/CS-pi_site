# CS-Pi project page (Astro)

The CoRL 2026 project page for **CS-Pi: Constraint-Satisfying Flow Policy
Sampling**, built on
[RomanHauksson/academic-project-astro-template](https://github.com/RomanHauksson/academic-project-astro-template)
(see `documentation.md` for the template's own docs). It deploys to
<https://sumo048.github.io/CS-pi_site/>.

## Run locally

Node 24 or later.

```bash
cd site
npm install
npm run dev       # http://localhost:4321/CS-pi_site/
npm run build     # astro check + static build into site/dist/
npm run preview   # serve dist/ at http://localhost:4321/CS-pi_site/
```

## Where things live

| Path | What it is |
|------|------------|
| `src/paper.mdx` | The page: every section, in order. Edit prose here. |
| `src/data/site.ts` | Title, authors, links, methods, explorer tasks/scenarios, result tables, headline numbers (ported from the old `js/data.js`). |
| `src/data/spheres.ts` | Captions and outcomes for the spheres-environment clips. |
| `src/data/media_manifest.json` | **Generated** by `tools/build_manifest.py`. Video paths for the explorer, face-off and spheres gallery. |
| `src/islands/Explorer.tsx`, `FaceOff.tsx` | React islands (the old `js/explorer.js` logic). |
| `src/scripts/hero.js` | The hero canvas loop, ported from `js/hero.js` (colours now follow the theme). |
| `src/components/` | Template components (`Video`, `Figure`, `Picture`, tabs, `Header`) plus `Section`, `Clip`, `Hardware`, `ResultsTabs`, `SpheresGallery`, `ThemeToggle`. |
| `src/lib/lazyMedia.ts` | Lazy video/image loading; pauses clips that scroll off screen. |
| `src/styles/global.css` | All design tokens (light + dark) and layout. |
| `public/media/` | MP4 + WebM + poster JPG for every rollout clip. |
| `public/figures/` | Figures served at full, uncompressed resolution (`concept.png`, hardware frame strips). |
| `src/assets/figures/` | Figures that Astro compresses to AVIF/WebP at responsive sizes. |

## Adding or changing rollout clips

GIFs stay the source of truth in `../viz/` and `../assets/story/`.

```bash
# from the repository root
python3 tools/convert_media.py --ffmpeg /path/to/ffmpeg   # GIF -> MP4/WebM/poster in site/public/media
python3 tools/build_manifest.py                            # refresh src/data/media_manifest.json
```

`convert_media.py` skips outputs that already exist (`--force` to redo). For a
new explorer task or scenario, also add it to `TASKS` in `src/data/site.ts`.

## Theme

The page follows `prefers-color-scheme`; the corner toggle saves an explicit
choice in `localStorage`. `?theme=dark` / `?theme=light` forces one (handy for
screenshots). Colours are defined once, as CSS custom properties, at the top of
`src/styles/global.css`.

## Deploy

`.github/workflows/astro.yml` builds `site/` and deploys to GitHub Pages on
every push to `main0`. In the repository settings, **Pages → Build and
deployment → Source** must be set to **GitHub Actions**.
