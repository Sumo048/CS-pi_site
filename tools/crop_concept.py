#!/usr/bin/env python3
"""Cut the concept figure into its four method panels (lossless, full height).

Source: site/public/figures/concept.png (the paper's fig:concept, 3818x1234).
Output: site/public/figures/concept/<method>.png, shown one per method in the
"Four ways" section; opened side by side they rebuild the full figure. Panel
edges are the 2-px frame lines found by scanning the image.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "public" / "figures" / "concept.png"
OUT = ROOT / "site" / "public" / "figures" / "concept"
PANELS = {  # x-range of each panel's frame (inclusive)
    "guidance": (300, 1091),
    "projection": (1108, 1831),
    "rejection": (1848, 2631),
    "cspi": (2648, 3805),
}


def main() -> None:
    im = Image.open(SRC)
    assert im.size == (3818, 1234), f"unexpected size {im.size}; re-measure PANELS"
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (x0, x1) in PANELS.items():
        crop = im.crop((x0 - 2, 0, min(im.width, x1 + 3), im.height))
        crop.save(OUT / f"{name}.png", optimize=True)
        print(name, crop.size)


if __name__ == "__main__":
    main()
