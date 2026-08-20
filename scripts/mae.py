#!/usr/bin/env python3
"""Compare two screenshots. MAE = mean abs RGB error (0-255)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def parse_crop(raw: str) -> tuple[int, int, int, int]:
    parts = [int(x) for x in raw.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("crop must be x,y,x2,y2")
    return parts[0], parts[1], parts[2], parts[3]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("origin")
    p.add_argument("local")
    p.add_argument(
        "--width",
        type=int,
        default=390,
        help="clip both images to this width (390 mobile, 1440 desktop)",
    )
    p.add_argument("--crop", type=parse_crop, help="x,y,x2,y2")
    p.add_argument("--diff", type=Path, help="write difference PNG")
    args = p.parse_args()

    a = Image.open(args.origin).convert("RGB")
    b = Image.open(args.local).convert("RGB")
    if args.crop:
        a = a.crop(args.crop)
        b = b.crop(args.crop)
    w = min(a.width, b.width, args.width)
    h = min(a.height, b.height)
    a = a.crop((0, 0, w, h))
    b = b.crop((0, 0, w, h))
    d = ImageChops.difference(a, b)
    mae = sum(ImageStat.Stat(d).mean) / 3
    hist = d.convert("L").histogram()
    diff_ratio = sum(hist[16:]) / (w * h) * 100
    if args.diff:
        args.diff.parent.mkdir(parents=True, exist_ok=True)
        d.save(args.diff)
    print(f"size {w}x{h}")
    print(f"MAE {mae:.2f}")
    print(f"diff_ratio {diff_ratio:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
