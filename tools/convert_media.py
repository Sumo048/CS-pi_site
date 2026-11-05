#!/usr/bin/env python3
"""Convert rollout GIFs (and hardware MP4s) to web MP4 + WebM + poster JPG.

Usage: python3 tools/convert_media.py --ffmpeg /path/to/ffmpeg [--force] [--workers 6]
Outputs mirror source paths under site/public/media/.
"""
import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "public" / "media"
# Raw side-by-side renders; tools/split_spheres.py turns them into per-method
# GIFs under viz/spheres_scenario_method_gifs/, which are converted instead.
SKIP_DIRS = {"spheres_env_gifs"}
VF = ("scale='min(1280,iw)':-2:flags=lanczos,"
      "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p")

MP4_ARGS = ["-c:v", "libx264", "-preset", "slow", "-crf", "27",
            "-profile:v", "high", "-movflags", "+faststart", "-an"]
WEBM_ARGS = ["-c:v", "libvpx-vp9", "-crf", "27", "-b:v", "0", "-row-mt", "1",
             "-deadline", "good", "-cpu-used", "2", "-an"]


def jobs():
    """Yield (src, out_stem, existing_poster_or_None, copy_mp4)."""
    for g in sorted((ROOT / "viz").rglob("*.gif")):
        rel = g.relative_to(ROOT / "viz")
        if rel.parts[0] in SKIP_DIRS:
            continue
        poster = ROOT / "assets" / "posters" / rel.with_suffix(".jpg")
        yield g, OUT / "viz" / rel.with_suffix(""), poster, False
    for g in sorted((ROOT / "assets" / "story").glob("*.gif")):
        yield g, OUT / "story" / g.stem, None, False
    hw = ROOT / "assets" / "hardware"
    for g in sorted(hw.glob("*.gif")):
        yield g, OUT / "hardware" / g.stem, hw / (g.stem + ".jpg"), False
    for m in sorted(hw.glob("*.mp4")):
        yield m, OUT / "hardware" / m.stem, hw / (m.stem + ".jpg"), True


def run(ff, args):
    p = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip())


def convert(ff, job, force):
    src, stem, poster, copy_mp4 = job
    stem.parent.mkdir(parents=True, exist_ok=True)
    mp4, webm, jpg = (stem.with_suffix(s) for s in (".mp4", ".webm", ".jpg"))
    done = []
    try:
        if force or not mp4.exists() or mp4.stat().st_size == 0:
            if copy_mp4:
                shutil.copyfile(src, mp4)
            else:
                run(ff, ["-i", str(src), "-vf", VF, *MP4_ARGS, str(mp4)])
            done.append("mp4")
        if force or not webm.exists() or webm.stat().st_size == 0:
            run(ff, ["-i", str(src), "-vf", VF, *WEBM_ARGS, str(webm)])
            done.append("webm")
        if force or not jpg.exists() or jpg.stat().st_size == 0:
            if poster is not None and poster.exists():
                shutil.copyfile(poster, jpg)
            else:
                run(ff, ["-i", str(src), "-vf", VF, "-frames:v", "1",
                         "-q:v", "4", str(jpg)])
            done.append("jpg")
        return src, done, None
    except Exception as e:  # noqa: BLE001
        return src, done, str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ffmpeg", default=os.environ.get("FFMPEG"))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if not a.ffmpeg:
        sys.exit("pass --ffmpeg or set $FFMPEG")
    all_jobs = list(jobs())
    failed = 0
    with ThreadPoolExecutor(a.workers) as ex:
        for i, (src, done, err) in enumerate(
                ex.map(lambda j: convert(a.ffmpeg, j, a.force), all_jobs), 1):
            rel = src.relative_to(ROOT)
            if err:
                failed += 1
                print(f"[{i}/{len(all_jobs)}] FAIL {rel}: {err}")
            else:
                print(f"[{i}/{len(all_jobs)}] {rel} {','.join(done) or 'skip'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
