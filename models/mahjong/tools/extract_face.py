#!/usr/bin/env python3
"""Turn an upstream mahjong tile SVG into normalised, per-colour face files.

The upstream artwork (see ../vendor/riichi-mahjong-tiles/SOURCE.md) is drawn for
screen rendering: nested groups, live strokes, and unused template geometry
parked in <defs>. OpenSCAD's import() wants none of that — it wants flat filled
paths on a known canvas.

Pipeline
--------
1. Flatten with Inkscape: ungroup everything, convert shapes and strokes to
   filled paths. Anything in <defs> stays in <defs> and is dropped in step 2.
2. Bucket the surviving paths by fill colour. The artwork is already
   colour-separated at source, so this is a filter, not a redraw.
3. Measure the union bounding box of all buckets by rasterising and reading the
   alpha channel. This is exact and sidesteps Bezier bbox estimation.
4. Emit one SVG per colour plus a merged silhouette, each on the same canvas
   with the same transform, so the colour layers stay in register when OpenSCAD
   stacks them.

The colour layers overlap
-------------------------
The artwork is a z-stack, not a partition: in `Pin5` the white spokes are drawn
*over* the navy disc, so `pin5-navy.svg` is a solid disc and `pin5-white.svg`
puts the holes back. Document order is preserved in every emitted file, so
stacking them in the order this script prints them reproduces the original.
A colour's *exclusive* region is its paths minus everything listed after it —
that subtraction belongs in OpenSCAD (Phase 2), not here, because SVG cannot
express it.

Output canvas is `300mm x 400mm` with `viewBox="0 0 300 400"`, i.e. one user
unit == one millimetre. That is deliberate: OpenSCAD interprets a unitless SVG
at 72 dpi, and pinning explicit mm units means tile.scad can scale by a plain
`face_w / 300` with no dpi constant to get wrong.

Usage
-----
    extract_face.py <name> <in.svg> [--outdir DIR] [--fill 0.86]
"""

from __future__ import annotations

import argparse
import collections
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)

# Hex fills used by the upstream artwork, mapped to names that mean something to
# a slicer operator loading four spools. Unknown fills fall back to their hex.
COLOUR_NAMES = {
    "#000000": "black",
    "#b93c3c": "red",
    "#ffffff": "white",
    "#000037": "navy",
    "#008000": "green",
}

# Inkscape does the flattening; --actions is the only interface that ungroups
# and converts strokes in one non-interactive pass.
FLATTEN_ACTIONS = (
    "select-all:layers;selection-ungroup;"
    "select-all;object-to-path;"
    "select-all;object-stroke-to-path"
)


def flatten(src: Path, dst: Path) -> None:
    """Ungroup, shapes-to-paths, strokes-to-paths, via Inkscape.

    Inkscape silently refuses relative paths here, so everything handed to it in
    this file is resolved absolute first.
    """
    subprocess.run(
        [
            "inkscape",
            "--export-type=svg",
            "--export-plain-svg",
            f"--export-filename={dst.resolve()}",
            f"--actions={FLATTEN_ACTIONS}",
            str(src.resolve()),
        ],
        check=True,
        capture_output=True,
    )
    if not dst.exists():
        raise RuntimeError(f"inkscape produced no output for {src}")


def fill_of(el: ET.Element) -> str | None:
    """Resolve an element's fill from either the attribute or the style string.

    A path with no fill anywhere is *black*, not unpainted — that is SVG's
    initial value, and Pin5's outer rings rely on it. Treating those as
    colourless silently dropped five paths per tile from every colour layer.
    """
    style = el.get("style", "")
    m = re.search(r"(?:^|;)\s*fill:\s*(#[0-9a-fA-F]{6})", style)
    if m:
        return m.group(1).lower()
    fill = el.get("fill")
    if fill and fill.startswith("#") and len(fill) == 7:
        return fill.lower()
    if fill is None and "fill:" not in style:
        return "#000000"
    return None


DROP_TAGS = {f"{{{SVG}}}defs", f"{{{SVG}}}metadata"}


def artwork_tree(flat: Path) -> ET.ElementTree:
    """Load the flattened SVG with the non-artwork branches pruned.

    Everything real hangs off nested <g> elements that carry their own
    translates — Inkscape's ungroup pushes transforms onto groups rather than
    baking them into path data. So the paths are filtered *in place* rather than
    lifted out by their `d` string; lifting them loses those ancestor
    transforms and scatters the glyph across the plane.

    <defs> holds the template leftovers (an arrow marker, construction circles,
    a clip rect) and <metadata> the RDF block. Neither renders; both go.
    """
    tree = ET.parse(flat)
    root = tree.getroot()
    for child in list(root):
        if child.tag in DROP_TAGS:
            root.remove(child)
    return tree


def census(tree: ET.ElementTree) -> "collections.OrderedDict[str, int]":
    """Count the surviving paths per fill colour, in document order."""
    counts: collections.OrderedDict[str, int] = collections.OrderedDict()
    for el in tree.getroot().iter(f"{{{SVG}}}path"):
        colour = fill_of(el)
        if colour and el.get("d"):
            counts[colour] = counts.get(colour, 0) + 1
    return counts


def write_svg(
    path: Path,
    tree: ET.ElementTree,
    transform: str | None,
    keep: str | None = None,
) -> None:
    """Write the artwork onto the canonical 300x400 mm canvas.

    `keep` restricts output to a single fill colour; None keeps every colour.
    Empty groups are left in place — they render as nothing and removing them
    would mean another parent-map walk for no gain.
    """
    import copy

    tree = copy.deepcopy(tree)
    root = tree.getroot()

    if keep is not None:
        parents = {c: p for p in root.iter() for c in p}
        for el in list(root.iter(f"{{{SVG}}}path")):
            colour = fill_of(el)
            if colour != keep:
                parents[el].remove(el)

    # Re-parent everything under one group so the normalising transform applies
    # on top of the artwork's own transforms rather than replacing them.
    wrapper = ET.Element(f"{{{SVG}}}g")
    if transform:
        wrapper.set("transform", transform)
    for child in list(root):
        root.remove(child)
        wrapper.append(child)
    root.append(wrapper)

    # One user unit == one millimetre, so tile.scad scales by face_w / 300 with
    # no dpi assumption anywhere in the chain.
    root.set("width", "300mm")
    root.set("height", "400mm")
    root.set("viewBox", "0 0 300 400")

    tree.write(path, encoding="unicode", xml_declaration=True)


def raster_bbox(svg: Path, px: int, tmp: Path) -> tuple[float, float, float, float]:
    """Union bbox of the drawn pixels, in canvas units, via an alpha raster."""
    png = tmp / "bbox.png"
    subprocess.run(
        [
            "inkscape",
            "--export-type=png",
            f"--export-filename={png.resolve()}",
            "--export-area-page",
            f"--export-width={px}",
            str(svg.resolve()),
        ],
        check=True,
        capture_output=True,
    )
    from PIL import Image
    import numpy as np

    a = np.array(Image.open(png).convert("RGBA"))[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if len(xs) == 0:
        raise RuntimeError(f"{svg} rasterised to nothing")
    scale = 300.0 / a.shape[1]  # canvas units per pixel
    x0, x1 = xs.min() * scale, (xs.max() + 1) * scale
    y0, y1 = ys.min() * scale, (ys.max() + 1) * scale
    return x0, y0, x1 - x0, y1 - y0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("name", help="output basename, e.g. man9")
    ap.add_argument("source", type=Path, help="upstream SVG")
    ap.add_argument("--outdir", type=Path, default=Path("faces"))
    ap.add_argument(
        "--fill",
        type=float,
        default=0.86,
        help="fraction of the canvas the glyph fills (aspect preserved)",
    )
    ap.add_argument("--raster-px", type=int, default=1200)
    args = ap.parse_args(argv)

    args.outdir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=args.outdir) as td:
        tmp = Path(td)
        flat = tmp / "flat.svg"
        flatten(args.source, flat)
        tree = artwork_tree(flat)
        counts = census(tree)
        if not counts:
            print(f"{args.name}: no filled paths found", file=sys.stderr)
            return 1

        # Measure the union of every colour together, then apply that one
        # transform to all of them so the layers stay registered.
        probe = tmp / "probe.svg"
        write_svg(probe, tree, None)
        x, y, w, h = raster_bbox(probe, args.raster_px, tmp)

        s = min(args.fill * 300.0 / w, args.fill * 400.0 / h)
        tx = (300.0 - w * s) / 2.0 - x * s
        ty = (400.0 - h * s) / 2.0 - y * s
        transform = f"translate({tx:.4f},{ty:.4f}) scale({s:.6f})"

        write_svg(args.outdir / f"{args.name}.svg", tree, transform)
        for colour in counts:
            cname = COLOUR_NAMES.get(colour, colour.lstrip("#"))
            write_svg(args.outdir / f"{args.name}-{cname}.svg", tree, transform, keep=colour)

        summary = ", ".join(
            f"{COLOUR_NAMES.get(c, c)}x{n}" for c, n in counts.items()
        )
        print(
            f"{args.name}: {summary} | src bbox {w:.1f}x{h:.1f} "
            f"| scale {s:.4f} -> glyph {w*s:.1f}x{h*s:.1f} of 300x400"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
