#!/usr/bin/env python3
"""Scan viz/ for rollout GIFs and write site/src/data/media_manifest.json.

The manifest maps each explorer cell (and each spheres-gallery clip) to the
MP4 / WebM / poster that tools/convert_media.py produced under
site/public/media/. The site reads it and never hardcodes clip paths.

Typical use after adding GIFs:
    python3 tools/convert_media.py --ffmpeg /path/to/ffmpeg
    python3 tools/build_manifest.py

Layouts:
  * Scenario-major, with success/fail (the shelf task):
        viz/<task>_scenario_method_gifs/<scenario>/<method>__<outcome>.gif
    where outcome is "success" or "fail". A missing cell is meaningful (see
    the explorer's absence reasons).
  * Method-major, one rollout per cell (3D-Orient): registered in
    SINGLE_OUTCOME_TASKS below.
  * viz/spheres_env_gifs/<distribution>/*.gif for the spheres gallery.
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
SPHERES = "spheres_env_gifs"

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
            ("amr_joint", "amr_joint_prox"),
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


def build_spheres() -> dict:
    """Gallery clips for the spheres environment, grouped by distribution."""
    groups: dict = {}
    base = VIZ / SPHERES
    for d in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
        key = "in_distribution" if d.name.startswith("in_") else "out_of_distribution"
        groups[key] = [{"name": g.stem, **to_video(g)} for g in sorted(d.glob("*.gif"))]
    return groups


def main() -> None:
    tasks = build_scenario_major()
    add_single_outcome(tasks)
    data = {"tasks": tasks, "spheres": build_spheres()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    n = sum(len(o) for t in tasks.values() for s in t.values() for o in s.values())
    print(f"wrote {OUT.relative_to(ROOT)}: {len(tasks)} task(s), {n} explorer clip(s), "
          f"{sum(len(v) for v in data['spheres'].values())} spheres clip(s)")


if __name__ == "__main__":
    main()
