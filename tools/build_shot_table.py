#!/usr/bin/env python3
"""Build a shot-breakdown Excel sheet with one screenshot per shot.

CSV columns:
    shot, group, start, end, capture, scene, picture, camera, light, analysis, certainty

Example:
    python tools/build_shot_table.py \
        --video input.mp4 \
        --shots examples/example-shots.csv \
        --out out/breakdown.xlsx

Requires: ffmpeg, openpyxl, Pillow
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image as PILImage
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

FONT = "Microsoft YaHei"
HEADERS = [
    "镜号", "截图", "时间码", "时长(s)", "场景",
    "画面内容", "机位 / 景别 / 运镜", "光线 / 声音 / 字幕",
    "分析 / 复刻要点", "确定性",
]
WIDTHS = {"A": 5.5, "B": 25, "C": 10.5, "D": 7.5, "E": 14,
          "F": 24, "G": 30, "H": 24, "I": 40, "J": 7.5}
THIN = Side(style="thin", color="CDBBA4")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def parse_time(value: str) -> float:
    """Accept 12.3, 00:12.3 or 01:02:03.4 and return seconds."""
    value = str(value).strip()
    if not value:
        raise ValueError("empty time")
    parts = value.split(":")
    if len(parts) == 1:
        return float(parts[0])
    seconds = 0.0
    for part in parts:
        seconds = seconds * 60 + float(part)
    return seconds


def fmt_time(seconds: float) -> str:
    minutes, sec = divmod(max(seconds, 0.0), 60)
    return f"{int(minutes):02d}:{sec:04.1f}"


def read_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def extract_frame(ffmpeg: str, video: str, at: float, out_path: str) -> None:
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{at:.3f}", "-i", video,
        "-frames:v", "1", "-q:v", "2", out_path,
    ]
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed at {at:.2f}s:\n{result.stderr.strip()}")


def build(args: argparse.Namespace) -> None:
    rows = read_rows(args.shots)
    if not rows:
        raise SystemExit("CSV has no rows")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="shot_frames_")
    img_w = args.image_width
    img_h = round(img_w * 2 / 3)

    wb = Workbook()
    ws = wb.active
    ws.title = args.sheet_name
    ws.sheet_view.showGridLines = False
    for col, width in WIDTHS.items():
        ws.column_dimensions[col].width = width

    # Title
    ws.merge_cells("A1:J1")
    c = ws["A1"]
    c.value = args.title
    c.font = Font(name=FONT, size=15, bold=True, color="2B2118")
    c.alignment = Alignment(vertical="center", horizontal="left")
    c.fill = PatternFill("solid", fgColor="F8F3EA")
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:J2")
    c = ws["A2"]
    c.value = args.meta
    c.font = Font(name=FONT, size=9, color="6A5A47")
    c.alignment = Alignment(vertical="center", horizontal="left")
    c.fill = PatternFill("solid", fgColor="F8F3EA")
    ws.row_dimensions[2].height = 20

    # Header
    for j, header in enumerate(HEADERS, 1):
        c = ws.cell(row=3, column=j, value=header)
        c.font = Font(name=FONT, size=9.5, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="3F3226")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[3].height = 30

    r = 4
    current_group = None
    for idx, row in enumerate(rows, 1):
        group = (row.get("group") or "").strip()
        if group and group != current_group:
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10)
            c = ws.cell(row=r, column=1, value=group)
            c.font = Font(name=FONT, size=10, bold=True, color="5A4028")
            c.fill = PatternFill("solid", fgColor="EFE4D3")
            c.alignment = Alignment(vertical="center", horizontal="left")
            for j in range(1, 11):
                ws.cell(row=r, column=j).border = BORDER
                ws.cell(row=r, column=j).fill = PatternFill("solid", fgColor="EFE4D3")
            ws.row_dimensions[r].height = 21
            r += 1
            current_group = group

        shot = (row.get("shot") or f"{idx:02d}").strip()
        start = parse_time(row["start"])
        end = parse_time(row["end"])
        duration = end - start
        capture = parse_time(row["capture"]) if (row.get("capture") or "").strip() else (start + end) / 2

        frame_path = os.path.join(tmp_dir, f"shot_{idx:03d}.jpg")
        extract_frame(args.ffmpeg, args.video, capture, frame_path)

        values = [
            shot,
            "",
            fmt_time(start),
            round(duration, 1),
            row.get("scene", ""),
            row.get("picture", ""),
            row.get("camera", ""),
            row.get("light", ""),
            row.get("analysis", ""),
            row.get("certainty", ""),
        ]
        for j, value in enumerate(values, 1):
            c = ws.cell(row=r, column=j, value=value)
            c.font = Font(name=FONT, size=9, color="241D15")
            c.alignment = Alignment(
                vertical="top", wrap_text=True,
                horizontal="center" if j in (1, 3, 4, 10) else "left",
            )
            c.border = BORDER
            if j == 4:
                c.number_format = "0.0"
            if r % 2 == 0:
                c.fill = PatternFill("solid", fgColor="FBF8F3")

        ws.cell(row=r, column=1).font = Font(name=FONT, size=11, bold=True, color="7A5327")
        ws.cell(row=r, column=10).font = Font(name=FONT, size=9, bold=True, color="6D4C2C")
        ws.row_dimensions[r].height = max(90, round(img_h * 0.75) + 4)

        im = PILImage.open(frame_path).convert("RGB").resize((img_w, img_h), PILImage.LANCZOS)
        thumb = os.path.join(tmp_dir, f"thumb_{idx:03d}.jpg")
        im.save(thumb, "JPEG", quality=88, optimize=True)
        img = XLImage(thumb)
        img.width, img.height = img_w, img_h
        ws.add_image(img, f"B{r}")
        r += 1

    ws.freeze_panes = "A4"
    ws.print_title_rows = "3:3"
    ws.print_area = f"A1:J{r - 1}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins.left = 0.25
    ws.page_margins.right = 0.25
    ws.page_margins.top = 0.35
    ws.page_margins.bottom = 0.35
    ws.oddFooter.center.text = "第 &P / &N 页"
    ws.oddFooter.center.size = 8

    wb.save(args.out)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"saved {args.out} ({r - 1} rows, {len(rows)} images)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a shot-breakdown Excel sheet.")
    parser.add_argument("--video", required=True, help="input video path")
    parser.add_argument("--shots", required=True, help="CSV with shot rows")
    parser.add_argument("--out", required=True, help="output .xlsx path")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable")
    parser.add_argument("--image-width", type=int, default=180, help="thumbnail width in px")
    parser.add_argument("--title", default="Vlog 逆向拆解 · 逐镜脚本")
    parser.add_argument("--meta", default="逐镜拆解｜机位/景别/运镜 + 光线/声音｜仅用于学习分析")
    parser.add_argument("--sheet-name", default="逐镜表")
    args = parser.parse_args()

    if shutil.which(args.ffmpeg) is None and not os.path.exists(args.ffmpeg):
        raise SystemExit(f"ffmpeg not found: {args.ffmpeg}")
    if not os.path.exists(args.video):
        raise SystemExit(f"video not found: {args.video}")

    build(args)


if __name__ == "__main__":
    main()
