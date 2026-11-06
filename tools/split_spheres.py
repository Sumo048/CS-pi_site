#!/usr/bin/env python3
"""Import the sphere-avoidance renders into the explorer's clip layout.

Source: a folder like ~/spheres_gifs/ rendered from the camera-ready release
run (see its README.md): <unit>/task<N>/{CS-Pi,Guidance,Trust,Projection,
Unguided}.gif plus info.json, for unit "id" (Level 1, 10 spheres) and "ood"
(Level 2, 16 spheres). The tasks are illustrative: picked where the shown
CS-Pi sample is collision-free and every other method's shown sample collides.

Output: viz/spheres_scenario_method_gifs/level_<L>_scenario_<S>/<method>__<outcome>.gif
with the outcome read from info.json (collision_waypoints == 0 -> success).
Each frame's three-line header (internal method name, level/task line, and the
final "RESULT: ..." line) is cropped off: rows 0-69; the scene starts at row 78.

    python3 tools/split_spheres.py --src ~/spheres_gifs --ffmpeg /path/to/ffmpeg
then
    python3 tools/convert_media.py --ffmpeg /path/to/ffmpeg
    python3 tools/build_manifest.py
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "viz" / "spheres_scenario_method_gifs"

# (unit, task) in scenario order per level
LEVELS = {
    1: ("id", [58, 86, 98]),
    2: ("ood", [41, 44, 60]),
}
METHODS = {  # render name -> site method key
    "CS-Pi": "amr",
    "Guidance": "tweedie",
    "Trust": "trust",
    "Projection": "projection",
    "Unguided": "unguided",
}
TOP_CROP = 70


def crop(ffmpeg: str, src: Path, dst: Path) -> None:
    vf = (f"crop=iw:ih-{TOP_CROP}:0:{TOP_CROP},split[a][b];"
          "[a]palettegen=reserve_transparent=0:stats_mode=full[p];"
          "[b][p]paletteuse=dither=none")
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ffmpeg, "-loglevel", "error", "-y", "-i", str(src),
                    "-filter_complex", vf, "-loop", "0", str(dst)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(Path.home() / "spheres_gifs"))
    ap.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    args = ap.parse_args()
    src = Path(args.src).expanduser()
    if DST.exists():
        shutil.rmtree(DST)
    for level, (unit, tasks) in LEVELS.items():
        for s, task in enumerate(tasks, start=1):
            folder = src / unit / f"task{task}"
            info = json.loads((folder / "info.json").read_text())
            scen = f"level_{level}_scenario_{s}"
            for render, key in METHODS.items():
                outcome = "success" if info[render]["collision_waypoints"] == 0 else "fail"
                crop(args.ffmpeg, folder / f"{render}.gif", DST / scen / f"{key}__{outcome}.gif")
                print(f"{scen}: {key}__{outcome}  <- {unit}/task{task}/{render}.gif "
                      f"({info[render]['collision_waypoints']}/64 colliding waypoints)")
    shutil.copy(src / "README.md", DST / "README.md")   # provenance and table numbers


if __name__ == "__main__":
    main()
