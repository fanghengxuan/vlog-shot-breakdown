#!/usr/bin/env python3
"""Detect candidate shot boundaries with ffmpeg's scene score.

Usage:
    python tools/scene_detect.py --video input.mp4 --threshold 0.30

Output:
    one timestamp per line (seconds), plus a CSV-friendly summary on stderr.

Note:
    A low threshold (0.12) catches soft cuts but also fast pans and occlusions.
    Always verify candidates by extracting frames before and after each cut.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import shutil
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect candidate shot boundaries.")
    parser.add_argument("--video", required=True)
    parser.add_argument("--threshold", type=float, default=0.30)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()

    if shutil.which(args.ffmpeg) is None and not os.path.exists(args.ffmpeg):
        raise SystemExit(f"ffmpeg not found: {args.ffmpeg}")
    if not os.path.exists(args.video):
        raise SystemExit(f"video not found: {args.video}")

    vf = f"select='gt(scene,{args.threshold})',showinfo"
    cmd = [args.ffmpeg, "-hide_banner", "-i", args.video,
           "-vf", vf, "-an", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(proc.returncode)

    times = re.findall(r"pts_time:([0-9.]+)", proc.stderr)
    for t in times:
        print(t)
    sys.stderr.write(f"{len(times)} candidate cuts at threshold {args.threshold}\n")


if __name__ == "__main__":
    main()
