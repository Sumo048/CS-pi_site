#!/usr/bin/env python3
"""Replace the burned-in titles of the soft-preference clips with site names.

The renders' first line ("Unguided (no orientation cost)", "CS-Pi guided
(orientation weight 0.3)", ...) uses internal names. This covers that line
with a small white box and writes the site's name on it; everything else in
the frame (distance to goal, orientation error, scene) is untouched.

Originals:  assets/soft_pref/raw/<name>.gif
Output:     assets/soft_pref/<name>.gif   (then run tools/convert_media.py --force)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "assets" / "soft_pref" / "raw"
OUT = ROOT / "assets" / "soft_pref"

TITLES = {
    "agree_unconstrained": "Unconstrained",
    "agree_cspi": "CS-Pi",
    "conflict_unconstrained": "Unconstrained",
    "conflict_task_aligned": "CS-Pi, task aligned",
    "conflict_cost_aligned": "CS-Pi, cost aligned",
}
BOX = (0, 0, 640, 31)          # title line is rows 10-27; the metrics line starts at row 33
TEXT_XY = (9, 8)
INK = (27, 28, 30)
FONT = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 19)


def relabel(src: Path, dst: Path, title: str) -> None:
    im = Image.open(src)
    frames, durations = [], []
    for fr in ImageSequence.Iterator(im):
        f = fr.convert("RGB")
        d = ImageDraw.Draw(f)
        d.rectangle(BOX, fill=(255, 255, 255))
        d.text(TEXT_XY, title, font=FONT, fill=INK)
        frames.append(f)
        durations.append(fr.info.get("duration", im.info.get("duration", 100)))
    frames[0].save(dst, save_all=True, append_images=frames[1:], duration=durations,
                   loop=im.info.get("loop", 0), optimize=False, disposal=1)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name, title in TITLES.items():
        raw = RAW / f"{name}.gif"
        cur = OUT / f"{name}.gif"
        if not raw.exists():          # first run: keep the untouched render
            cur.rename(raw)
        relabel(raw, cur, title)
        print(f"{name}.gif -> '{title}'")


if __name__ == "__main__":
    main()
