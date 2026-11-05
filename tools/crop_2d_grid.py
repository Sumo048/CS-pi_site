#!/usr/bin/env python3
"""Cut the paper's 2D Avoidance grid into one image per (scenario, method).

Source: assets/2d_distributions_all.png, the appendix figure "2D Avoidance
trajectory distributions, all six scenarios" (writing/corl_2026_sumo/figures/
fig1_d3il_distributions.png): 6 scenario rows x 5 method columns, 20 rollouts
per panel. Panels are cropped losslessly (no recolouring, no scaling) to

    site/public/figures/2d/<scenario>/<method>.png

for the explorer's 2D Avoidance task. Panel edges were measured from the
1-px grey frames around each panel; the crop keeps the frame.

    python3 tools/crop_2d_grid.py && python3 tools/build_manifest.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "2d_distributions_all.png"
OUT = ROOT / "site" / "public" / "figures" / "2d"

# Column = method, row = scenario, in the order they appear in the figure.
METHODS = ["tweedie", "trust", "rejection", "amr", "projection"]
SCENARIOS = ["left", "right", "both", "cluttered", "narrow", "narrower"]
X = [(182, 663), (674, 1155), (1166, 1647), (1658, 2139), (2150, 2631)]
Y = [(58, 539), (550, 1031), (1042, 1523), (1534, 2015), (2026, 2507), (2518, 2999)]


def main() -> None:
    im = Image.open(SRC)
    assert im.size == (2651, 3110), f"unexpected source size {im.size}; re-measure X/Y"
    for (y0, y1), scen in zip(Y, SCENARIOS):
        for (x0, x1), method in zip(X, METHODS):
            dst = OUT / scen / f"{method}.png"
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.crop((x0, y0, x1 + 1, y1 + 1)).save(dst, optimize=True)
    print(f"wrote {len(Y) * len(X)} panels to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
