#!/usr/bin/env python3
"""Scan viz/ for rollout GIFs and write site/src/data/media_manifest.json.

The manifest maps each explorer cell to the
MP4 / WebM / poster that tools/convert_media.py produced under
site/public/media/. The site reads it and never hardcodes clip paths.

Typical use after adding GIFs:
    python3 tools/convert_media.py --ffmpeg /path/to/ffmpeg
    python3 tools/build_manifest.py

Layouts:
  * Scenario-major, with success/fail (the shelf task):
        viz/<task>_scenario_method_gifs/<scenario>/<method>__<outcome>.gif
    where outcome is "success" or "fail". A missing cell is meaningful (see
    the explorer's absence reasons). The spheres task lives here too, made
    by tools/split_spheres.py from the side-by-side renders.
  * Method-major, one rollout per cell (3D-Orient): registered in
    SINGLE_OUTCOME_TASKS below.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # dimensions are optional; they only reserve layout space
    Image = None

ROOT = Path(__file__).resolve().parent.parent
VIZ = ROOT / "viz"
PUBLIC = ROOT / "site" / "public"
OUT = ROOT / "site" / "src" / "data" / "media_manifest.json"

GIF_RE = re.compile(r"^(?P<method>[a-z0-9_]+)__(?P<outcome>success|fail)\.gif$")

# Method-major, single-rollout tasks (one GIF per method per scenario, no
# success/fail split). Layout: viz/<dir>/<method-folder>/<scenario>.gif.
# `methods` maps the site method key -> the source folder name.
SINGLE_OUTCOME_TASKS = [
    {
        "task": "3dorient",
        "dir": "orientation_task_gifs",
        "scenarios": ["config1", "config2", "task28", "task31", "task43"],
        "methods": [
            ("amr", "amr_eeprox_ref"),
            ("amr_dyn", "amr_eeprox_dynamic"),
            ("unguided", "unguided"),
            ("tweedie", "tweedie_alpha0.03"),
            ("tweedie_weak", "tweedie_alpha0.003"),
            ("trust", "trust_w0.001"),
        ],
    },
]


def to_video(gif: Path) -> dict:
    """viz/...gif -> {mp4, webm, poster, w, h} with paths relative to site/public."""
    stem = "media/" + gif.relative_to(ROOT).as_posix()[: -len(".gif")]
    out: dict = {"mp4": stem + ".mp4", "webm": stem + ".webm", "poster": stem + ".jpg"}
    for k in ("mp4", "webm", "poster"):
        if not (PUBLIC / out[k]).is_file():
            print(f"  ! missing {out[k]} (run tools/convert_media.py)")
    poster = PUBLIC / out["poster"]
    if Image is not None and poster.is_file():
        with Image.open(poster) as im:
            out["w"], out["h"] = im.size
    return out


def build_scenario_major() -> dict:
    tasks: dict = {}
    for task_dir in sorted(VIZ.iterdir()) if VIZ.is_dir() else []:
        if not task_dir.is_dir() or not task_dir.name.endswith("_scenario_method_gifs"):
            continue
        task = tasks.setdefault(task_dir.name.replace("_scenario_method_gifs", ""), {})
        for scen_dir in sorted(p for p in task_dir.iterdir() if p.is_dir()):
            cell: dict = {}
            for gif in sorted(scen_dir.glob("*.gif")):
                m = GIF_RE.match(gif.name)
                if m:
                    cell.setdefault(m["method"], {})[m["outcome"]] = to_video(gif)
            if cell:
                task[scen_dir.name] = cell
    return tasks


def add_single_outcome(tasks: dict) -> None:
    for spec in SINGLE_OUTCOME_TASKS:
        base = VIZ / spec["dir"]
        if not base.is_dir():
            continue
        task = tasks.setdefault(spec["task"], {})
        for scen in spec["scenarios"]:
            cell: dict = {}
            for site_key, folder in spec["methods"]:
                gif = base / folder / f"{scen}.gif"
                if not gif.is_file():
                    print(f"  ! missing {gif.relative_to(ROOT)}")
                    continue
                cell[site_key] = {"rollout": to_video(gif)}
            if cell:
                task[scen] = cell


def still(path: str, thumb: str | None = None) -> dict:
    """A still image (relative to site/public) shown in place of a video."""
    out: dict = {"img": path}
    if not (PUBLIC / path).is_file():
        print(f"  ! missing {path}")
    elif Image is not None:
        with Image.open(PUBLIC / path) as im:
            out["w"], out["h"] = im.size
    if thumb:
        out["thumb"] = thumb
    return out


def add_2d(tasks: dict) -> None:
    """2D Avoidance: one still per (scenario, method), cut by tools/crop_2d_grid.py."""
    base = PUBLIC / "figures" / "2d"
    if not base.is_dir():
        return
    task = tasks.setdefault("2d", {})
    for scen_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        task[scen_dir.name] = {
            png.stem: {"rollout": still(png.relative_to(PUBLIC).as_posix())}
            for png in sorted(scen_dir.glob("*.png"))
        }


def media_video(stem: str) -> dict:
    """A clip already converted under site/public/media (e.g. hardware/...)."""
    out: dict = {"mp4": f"media/{stem}.mp4", "webm": f"media/{stem}.webm", "poster": f"media/{stem}.jpg"}
    for k in ("mp4", "webm", "poster"):
        if not (PUBLIC / out[k]).is_file():
            print(f"  ! missing {out[k]}")
    if Image is not None and (PUBLIC / out["poster"]).is_file():
        with Image.open(PUBLIC / out["poster"]) as im:
            out["w"], out["h"] = im.size
    return out


# The filmed real-world runs, for the Results comparison (task "hardware").
HARDWARE = {
    "amr": {"success": "hardware/cspi_success_0"},
    "unguided": {"fail": "hardware/unconstrained_1x"},
    "tweedie": {"fail": "hardware/gradient_guidance"},
    "trust": {"fail": "hardware/trust_fail"},
    "projection": {"fail": "hardware/project_fail"},
}


def add_hardware(tasks: dict) -> None:
    tasks["hardware"] = {"real": {m: {o: media_video(stem) for o, stem in outs.items()}
                                  for m, outs in HARDWARE.items()}}


def main() -> None:
    tasks = build_scenario_major()
    add_single_outcome(tasks)
    add_2d(tasks)
    add_hardware(tasks)
    data = {"tasks": tasks}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    n = sum(len(o) for t in tasks.values() for s in t.values() for o in s.values())
    print(f"wrote {OUT.relative_to(ROOT)}: {len(tasks)} task(s), {n} explorer clip(s)")


if __name__ == "__main__":
    main()
