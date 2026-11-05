#!/usr/bin/env python3
"""Split the side-by-side spheres renders into one GIF per method.

The renders in viz/spheres_env_gifs/ show two samplers side by side (left
half / right half). The explorer wants one clip per (scenario, method,
outcome), so this crops the halves into

    viz/spheres_scenario_method_gifs/<level>/<method>__<outcome>.gif

which tools/build_manifest.py picks up like the shelf task. Outcomes are
read off each render's final frame ("cost=... OK" / "collision"). Only
collision-free CS-Pi rollouts are used.

Level 2 is left out on purpose: the out_of_distribution_* renders replay the
Level 1 trajectories with extra obstacles drawn in, and their printed cost
ignores those obstacles, so they cannot show avoidance of unseen obstacles.

    python3 tools/split_spheres.py --ffmpeg /path/to/ffmpeg
then
    python3 tools/convert_media.py --ffmpeg /path/to/ffmpeg
    python3 tools/build_manifest.py
"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "viz" / "spheres_env_gifs" / "in_distribution_EnvSpheres3D"
DST = ROOT / "viz" / "spheres_scenario_method_gifs"

# (level, method key, outcome) -> (source render, half)
CLIPS = {
    ("level_1", "amr", "success"): ("amr_vs_guidance_sample00", "right"),
    ("level_1", "tweedie", "fail"): ("amr_vs_guidance_sample00", "left"),
    ("level_1", "tweedie", "success"): ("amr_vs_guidance_sample01", "left"),
    ("level_1", "unguided", "fail"): ("amr_success_sample01", "left"),
    ("level_1", "unguided", "success"): ("amr_success_sample00", "left"),
}


def crop(ffmpeg: str, src: Path, half: str, dst: Path) -> None:
    x = "0" if half == "left" else "iw/2"
    vf = (f"crop=iw/2:ih:{x}:0,split[a][b];"
          "[a]palettegen=reserve_transparent=0:stats_mode=full[p];"
          "[b][p]paletteuse=dither=none")
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ffmpeg, "-loglevel", "error", "-y", "-i", str(src),
                    "-filter_complex", vf, "-loop", "0", str(dst)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    for (level, method, outcome), (name, half) in CLIPS.items():
        dst = DST / level / f"{method}__{outcome}.gif"
        if dst.exists() and not args.force:
            print("skip", dst.relative_to(ROOT))
            continue
        crop(args.ffmpeg, SRC / f"{name}.gif", half, dst)
        print("wrote", dst.relative_to(ROOT), "<-", f"{name} ({half})")


if __name__ == "__main__":
    main()
