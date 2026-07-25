#!/usr/bin/env python3
"""Pack several single-mesh 3MFs into one coloured, multi-part 3MF.

OpenSCAD 2021.01 writes exactly one object per 3MF and drops `color()` on
export, so the three colour bodies of a tile come out as three grey files that
have to be reassembled by hand in the slicer. This does that assembly offline:
it reads the parts, gives each one a base material with a display colour, and
wraps them in a *component* object so a slicer imports the result as one object
with three parts rather than three loose objects on the plate.

Why components rather than three top-level objects
--------------------------------------------------
A 3MF `<build>` may list several items, and every mainstream slicer will happily
show them — as siblings. Moving or rotating one then desynchronises it from the
others, and the shared origin that makes these parts mate exactly is lost the
first time anyone drags something. A single `<object>` whose `<components>`
reference the part objects is the spec's way of saying "these are one thing",
and PrusaSlicer-derived slicers (ElegooSlicer, OrcaSlicer, Bambu Studio) map it
onto their object/part model directly.

Colours travel as `<basematerials>`, one `<base>` per part, referenced from the
part object's `pid`/`pindex`. That is the core-spec mechanism, understood
without any vendor extension. Slicers treat it as a filament hint, not as a
binding assignment — you may still have to point each part at the right physical
spool, but they arrive named and coloured rather than as three grey lumps.

Geometry is copied verbatim. No transform is applied and no vertex is touched,
because the parts already share one origin by construction (see tile.scad).

Usage
-----
    merge_3mf.py OUT.3mf NAME=COLOUR=IN.3mf [NAME=COLOUR=IN.3mf ...]

    merge_3mf.py man9-test.3mf \\
        back=#9E7042=man9-back.3mf \\
        body=#F2F2F2=man9-body.3mf \\
        glyph=#1A1A1A=man9-glyph.3mf
"""

from __future__ import annotations

import argparse
import re
import sys
import uuid
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
MATL = "http://schemas.microsoft.com/3dmanufacturing/material/2015/02"

CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
\t<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />
\t<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
</Types>
"""

RELS = """<?xml version="1.0" encoding="utf-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
\t<Relationship Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="/3D/3dmodel.model" Id="rel0" />
</Relationships>
"""


def read_mesh(path: Path) -> ET.Element:
    """Return the `<mesh>` of the single object in a 3MF."""
    with zipfile.ZipFile(path) as z:
        # The relationship in _rels/.rels names the model part, but every writer
        # in practice puts it here, and a wrong guess fails loudly below.
        root = ET.fromstring(z.read("3D/3dmodel.model"))
    objects = root.findall(f".//{{{CORE}}}object")
    if len(objects) != 1:
        raise SystemExit(f"{path}: expected exactly 1 object, found {len(objects)}")
    mesh = objects[0].find(f"{{{CORE}}}mesh")
    if mesh is None:
        raise SystemExit(f"{path}: object has no mesh (a component object?)")
    return mesh


def parse_part(spec: str) -> tuple[str, str, Path]:
    name, colour, filename = spec.split("=", 2)
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?", colour):
        raise SystemExit(f"{spec}: colour must be #RRGGBB or #RRGGBBAA")
    if len(colour) == 7:
        colour += "FF"  # displaycolor is sRGBA; opaque unless told otherwise
    return name, colour.upper(), Path(filename)


def build_model(parts: list[tuple[str, str, Path]], name: str) -> bytes:
    for prefix, uri in (("", CORE), ("m", MATL), ("p", PROD)):
        ET.register_namespace(prefix, uri)

    model = ET.Element(
        f"{{{CORE}}}model",
        {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "en-US"},
    )
    resources = ET.SubElement(model, f"{{{CORE}}}resources")

    # Resource ids share one namespace across materials and objects, so the
    # material group takes 1 and the objects start at 2.
    materials = ET.SubElement(resources, f"{{{CORE}}}basematerials", {"id": "1"})
    for part_name, colour, _ in parts:
        ET.SubElement(
            materials, f"{{{CORE}}}base", {"name": part_name, "displaycolor": colour}
        )

    for index, (part_name, _, path) in enumerate(parts):
        obj = ET.SubElement(
            resources,
            f"{{{CORE}}}object",
            {
                "id": str(index + 2),
                "name": part_name,
                "type": "model",
                "pid": "1",
                "pindex": str(index),
                f"{{{PROD}}}UUID": str(uuid.uuid4()),
            },
        )
        obj.append(read_mesh(path))

    assembly_id = str(len(parts) + 2)
    assembly = ET.SubElement(
        resources,
        f"{{{CORE}}}object",
        {
            "id": assembly_id,
            "name": name,
            "type": "model",
            f"{{{PROD}}}UUID": str(uuid.uuid4()),
        },
    )
    components = ET.SubElement(assembly, f"{{{CORE}}}components")
    for index, _ in enumerate(parts):
        ET.SubElement(
            components,
            f"{{{CORE}}}component",
            {
                "objectid": str(index + 2),
                f"{{{PROD}}}UUID": str(uuid.uuid4()),
            },
        )

    build = ET.SubElement(model, f"{{{CORE}}}build", {f"{{{PROD}}}UUID": str(uuid.uuid4())})
    ET.SubElement(
        build,
        f"{{{CORE}}}item",
        {"objectid": assembly_id, f"{{{PROD}}}UUID": str(uuid.uuid4())},
    )

    ET.indent(model, space="\t")
    return b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(model, encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("out", type=Path, help="3MF to write")
    ap.add_argument("parts", nargs="+", metavar="NAME=#RRGGBB=IN.3mf")
    ap.add_argument("--name", help="assembly object name (default: output stem)")
    args = ap.parse_args(argv)

    parts = [parse_part(p) for p in args.parts]
    missing = [str(p) for _, _, p in parts if not p.exists()]
    if missing:
        print("no such file: " + ", ".join(missing), file=sys.stderr)
        return 1

    model = build_model(parts, args.name or args.out.stem)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("3D/3dmodel.model", model)
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)

    print(f"{args.out}: {len(parts)} parts, {args.out.stat().st_size} bytes")
    for part_name, colour, path in parts:
        print(f"  {part_name:<6} {colour}  <- {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
