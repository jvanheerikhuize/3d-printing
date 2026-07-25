// Parametric mahjong tile — see README.md for the design brief.
//
// Generates one tile: a rounded, chamfered slab with a face taken from the
// normalised SVGs in faces/ (produced by tools/extract_face.py).
//
// The face SVGs are 300 x 400 mm canvases where one user unit is one
// millimetre, so the only scale factor anywhere in the chain is tile_w / 300.
//
// Orientation: the face is at +Z. The Phase 1 test tile prints face *up* so the
// engraved glyph is a real top surface rather than a bridged void. The Phase 2
// colour tiles invert this and print face *down* — see PRINT.md.
//
// Two products come out of this one file, selected by `part`:
//
//   solid           one body, glyph cut in as relief          (Phase 1)
//   back/body/glyph three coplanar bodies, one per filament   (Phase 2)
//
// Render (see PRINT.md for the exact commands):
//   openscad -o man9.3mf tile.scad
//   openscad -o man9-glyph.3mf -D 'part="glyph"' tile.scad

/* [Tile] */
// Width of the tile face, mm
tile_w = 24;
// Length of the tile face, mm
tile_l = 32;
// Tile thickness, mm
tile_h = 3;
// Corner rounding radius, mm
corner_r = 2;

/* [Edges] */
// Chamfer on the face-side edge, mm — lifts a tile off the stack below it
chamfer_face = 0.6;
// Chamfer on the back-side edge, mm — also the elephant-foot allowance when
// this side is the one on the plate
chamfer_back = 0.4;

/* [Face] */
// SVGs unioned to form the face, relative to this file
face_add = ["faces/man9.svg"];
// SVGs subtracted from it afterwards
face_sub = [];
// "engrave" cuts the glyph in, "emboss" stands it proud, "flat" leaves the face
// blank for the multi-part colour workflow
face_mode = "engrave"; // [engrave, emboss, flat]
// Relief depth, mm. 0.5 is three layers at 0.16 mm.
face_depth = 0.5;

/* [Back] */
// Register recess in the back, mm deep. 0 disables it. Lets a tile sit into the
// tile below without sliding when stacked five deep.
back_recess = 0;
// Inset of the recess from the tile edge, mm
back_recess_inset = 2;

/* [Colour split] */
// What to emit. "solid" is the Phase 1 single-colour tile and is the only mode
// that obeys face_mode. The other three are the Phase 2 colour bodies — export
// one file each and load them into the slicer as parts of a single object.
// "all" previews the three together and is not meant for export.
part = "solid"; // [solid, all, back, body, glyph]
// Thickness of the wood-coloured back, mm. 0.48 is three layers at 0.16.
back_h = 0.48;
// Depth of the black glyph inlay, mm. Flush with the face, not proud.
glyph_h = 0.48;
// Gap between the bodies in the "all" preview, mm. Must stay above zero: the
// three parts share surfaces exactly, and OpenCSG's preview cannot resolve
// coincident faces between separate CSG products — assembled, it paints the
// whole tile in whichever part it picked, which is a picture of a renderer bug
// rather than of the tile. Exploding them removes the ambiguity and is the more
// legible drawing anyway.
explode = 2;

/* [Quality] */
$fn = 64;
// Trivial overlap used to keep booleans off coincident faces
eps = 0.01;

// ---------------------------------------------------------------------------

// Rounded rectangle centred on the origin, shrunk by `inset` on every side.
module rounded_rect(w, l, r, inset = 0) {
    ri = max(r - inset, 0.01);
    offset(r = ri) offset(delta = -ri)
        square([max(w - 2 * inset, 0.01), max(l - 2 * inset, 0.01)], center = true);
}

// Slab with both edges chamfered. Built as the hull of three thin plates: the
// inset ones at top and bottom produce the chamfers, the full-size middle pair
// keeps the sides vertical between them.
module tile_body() {
    hull() {
        linear_extrude(eps)
            rounded_rect(tile_w, tile_l, corner_r, chamfer_back);
        translate([0, 0, chamfer_back]) linear_extrude(eps)
            rounded_rect(tile_w, tile_l, corner_r);
        translate([0, 0, tile_h - chamfer_face - eps]) linear_extrude(eps)
            rounded_rect(tile_w, tile_l, corner_r);
        translate([0, 0, tile_h - eps]) linear_extrude(eps)
            rounded_rect(tile_w, tile_l, corner_r, chamfer_face);
    }
}

// The face artwork as a 2D shape, centred on the origin and scaled to the tile.
//
// No Y mirror here despite SVG's downward Y axis: import() already resolves the
// viewBox into OpenSCAD's coordinates, and adding a flip puts 萬 above 九.
//
// face_add is unioned and face_sub removed, because the artwork is a z-stack
// rather than a colour partition and SVG cannot express the subtraction. A
// single-colour Man9 is just its silhouette, so face_add alone covers it. Pin5
// is not: its outer black ring, white ring, navy disc and white spokes union to
// a plain circle, and everything that makes it a 5-dot lives in the boundaries
// between them. Relief has to come from the dark layers with the white cut back
// out — see "Dots as relief" in README.md §4.
module face_2d() {
    scale(tile_w / 300) translate([-150, -200]) difference() {
        union() { for (f = face_add) import(f, center = false); }
        for (f = face_sub) import(f, center = false);
    }
}

module tile() {
    difference() {
        union() {
            tile_body();
            if (face_mode == "emboss")
                translate([0, 0, tile_h - eps])
                    linear_extrude(face_depth + eps) face_2d();
        }
        if (face_mode == "engrave")
            translate([0, 0, tile_h - face_depth])
                linear_extrude(face_depth + eps) face_2d();
        if (back_recess > 0)
            translate([0, 0, -eps])
                linear_extrude(back_recess + eps)
                    rounded_rect(tile_w, tile_l, corner_r, back_recess_inset);
    }
}

// ---------------------------------------------------------------------------
// Phase 2: the three colour bodies.
//
// All three are carved from the same tile_body(), so they share one origin and
// mate exactly — the slicer needs no alignment beyond "these are one object".
// They partition the tile: back + body + glyph is tile_body(), with no overlap
// and nothing left over. That matters because overlapping parts make the slicer
// pick a winner per region, silently, and gaps between parts become voids.

// The tile between two heights. Intersecting rather than extruding a fresh
// profile keeps the chamfered edges: the wood back carries the bottom chamfer
// and the white body carries the top one, without either being restated here.
module slab(z0, z1) {
    intersection() {
        tile_body();
        translate([0, 0, z0])
            linear_extrude(z1 - z0)
                square([tile_w * 2, tile_l * 2], center = true);
    }
}

// The glyph as a solid, flush with the face. This is also exactly the volume
// the white body has removed from it, so the two are defined by one expression
// and cannot drift apart when the artwork or the depth changes.
module glyph_solid() {
    intersection() {
        slab(tile_h - glyph_h, tile_h);
        translate([0, 0, tile_h - glyph_h - eps])
            linear_extrude(glyph_h + 2 * eps) face_2d();
    }
}

module part_back()  { slab(0, back_h); }
module part_glyph() { glyph_solid(); }
module part_body()  { difference() { slab(back_h, tile_h); glyph_solid(); } }

// ---------------------------------------------------------------------------

assert(back_h + glyph_h < tile_h,
       "back_h + glyph_h must leave white body between them");

if (part == "solid")      tile();
else if (part == "back")  part_back();
else if (part == "body")  part_body();
else if (part == "glyph") part_glyph();
else if (part == "all") {
    // Preview only, and exploded — see `explode`. colour() is dropped on export
    // anyway, so rendering this to a file gives one fused mesh with gaps in it.
    assert(explode > 0, "the assembled preview does not render; keep explode > 0");
    color([0.62, 0.44, 0.26]) part_back();
    translate([0, 0, explode]) {
        color("white") part_body();
        translate([0, 0, explode]) color("black") part_glyph();
    }
} else {
    assert(false, "part must be one of: solid, all, back, body, glyph");
}
