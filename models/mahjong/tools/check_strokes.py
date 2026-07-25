#!/usr/bin/env python3
"""Measure a face's thinnest stroke and tightest gap against the nozzle floor.

README.md §4 fixes two numbers for a 0.4 mm nozzle at 0.42 mm line width: a
stroke needs two extrusion lines to exist at all, so **0.85 mm** is the minimum
printable stroke, and **0.8 mm** is the minimum gap that will not fuse shut.
This checks a face against both before anything is printed.

Where the ink comes from
------------------------
From the *composited* render, not from layer algebra. The artwork is a z-stack
rather than a partition — in `Pin5` the white spokes are painted over the navy
disc — so unioning the colour layers gives solid dots and quietly throws away
the very gaps this script exists to measure. Rendering `<name>.svg` over white
and keeping the non-white pixels reproduces exactly what ends up inked.

How the widths are measured
---------------------------
Via the medial axis. The obvious test — "open the mask with a disk of diameter
*d* and see if anything is removed" — does not work: opening rounds every sharp
convex corner, so it removes a sliver at *any* radius, and the answer collapses
to the smallest *d* tried.

Instead, take the Euclidean distance transform `D` (distance from each ink pixel
to the nearest background pixel) and keep its ridge — the pixels that are local
maxima. On a ridge pixel `D` is the local half-width, so the thinnest stroke in
the face is `2 * min(D)` over the ridge. Running the same measurement on the
inverted mask measures the gaps between strokes.

Ridge pixels with `D` under a pixel or so are rasterisation noise on the
boundary rather than real features, hence `NOISE_PX`. At the default 40 px/mm
that floor is 0.05 mm — two orders below anything the nozzle cares about.

Usage
-----
    check_strokes.py <faces-dir> <name> [--face-w 24] [--res 40] [--debug]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

# README.md §4. Both are millimetres on the finished face.
MIN_STROKE_MM = 0.85
MIN_GAP_MM = 0.80

# Ridge pixels thinner than this are raster noise, not geometry.
NOISE_PX = 1.5


def render_ink(svg: Path, px_w: int, out: Path) -> np.ndarray:
    """Composite the face over white; return a mask of the inked pixels.

    `--export-area-page` keeps the raster framed on the 300x400 canvas rather
    than cropped to the artwork, so pixel coordinates map linearly to the face.
    """
    subprocess.run(
        [
            "inkscape",
            "--export-type=png",
            f"--export-filename={out.resolve()}",
            "--export-area-page",
            "--export-background=white",
            "--export-background-opacity=255",
            f"--export-width={px_w}",
            str(svg.resolve()),
        ],
        check=True,
        capture_output=True,
    )
    rgb = np.array(Image.open(out).convert("RGB")).astype(np.int16)
    # Anything meaningfully darker or more saturated than the page is ink. The
    # threshold sits far from both endpoints, so antialiased edges land where
    # they should and nothing hinges on its exact value.
    return (255 - rgb).max(axis=2) > 96


def ridge_widths(mask: np.ndarray) -> np.ndarray:
    """Local feature widths, in pixels, sampled along the mask's medial axis."""
    dist = ndimage.distance_transform_edt(mask)
    ridge = (dist >= ndimage.maximum_filter(dist, size=3)) & (dist > NOISE_PX)
    return 2.0 * dist[ridge]


def report(label: str, mask: np.ndarray, mm_per_px: float, floor_mm: float) -> bool:
    """Print one measurement line; return True if it clears the floor.

    The verdict is taken from the 1st percentile, not the minimum. Where two
    shapes are drawn tangent the true local width is zero by construction, so the
    minimum measures the rasteriser rather than the artwork — visibly, `man9`
    reports the same 0.25 mm minimum at 24, 30, 36 and 48 mm faces while the
    fraction under the floor falls from 36% to 2.5%. One fused tangency point is
    a cosmetic non-event; a third of the outline fusing is not.
    """
    widths = ridge_widths(mask) * mm_per_px
    if widths.size == 0:
        print(f"  {label:<12} no measurable features")
        return False
    thin = float((widths < floor_mm).mean()) * 100.0
    p1 = float(np.percentile(widths, 1))
    ok = p1 >= floor_mm
    print(
        f"  {label:<12} p1 {p1:.2f} mm   min {widths.min():.2f} mm"
        f"   median {np.median(widths):.2f} mm   floor {floor_mm:.2f} mm"
        f"   {'PASS' if ok else 'FAIL'}"
        + ("" if ok else f"  ({thin:.1f}% of the medial axis is under it)")
    )
    return ok


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("faces", type=Path, help="directory of extracted face SVGs")
    ap.add_argument("name", help="face basename, e.g. man9")
    ap.add_argument("--face-w", type=float, default=24.0, help="face width in mm")
    ap.add_argument("--res", type=float, default=40.0, help="pixels per mm")
    ap.add_argument("--debug", action="store_true", help="write the ink mask as a PNG")
    args = ap.parse_args(argv)

    svg = args.faces / f"{args.name}.svg"
    if not svg.exists():
        print(f"no such face: {svg}", file=sys.stderr)
        return 1

    px_w = int(round(args.face_w * args.res))
    mm_per_px = args.face_w / px_w
    print(f"{args.name}: face {args.face_w:.0f} mm wide, rendered at {args.res:.0f} px/mm")

    # Scratch lives beside the faces: Inkscape here is sandboxed and cannot
    # reach /tmp, where it writes nothing and reports no error.
    with tempfile.TemporaryDirectory(dir=args.faces) as td:
        ink = render_ink(svg, px_w, Path(td) / "ink.png")

    if args.debug:
        dbg = args.faces / f"{args.name}-ink.png"
        Image.fromarray(np.where(ink, 0, 255).astype("uint8")).save(dbg)
        print(f"  ink mask -> {dbg}")

    ok = report("stroke", ink, mm_per_px, MIN_STROKE_MM)
    # Gaps are the holes in the ink, so measure the complement. The surrounding
    # margin is part of it too and simply reports a very large width.
    ok &= report("gap", ~ink, mm_per_px, MIN_GAP_MM)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
