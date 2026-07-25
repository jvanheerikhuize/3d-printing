// Parametric mahjong tile — see README.md for the design brief.
//
// Generates one tile: a rounded, chamfered slab with a face taken from the
// normalised SVGs in faces/ (produced by tools/extract_face.py).
//
// The face SVGs are 300 x 400 mm canvases where one user unit is one
// millimetre, so the only scale factor anywhere in the chain is tile_w / 300.
//
// Orientation: the face is at +Z. The Phase 1 test tile prints face *up* so the
// engraved glyph is a real top surface rather than a bridged void. Phase 2's
// multi-colour tiles use face_mode = "flat" and print face *down*, with the ink
// carried by separate coplanar bodies rather than by relief.
//
// Render (see PRINT.md for the two Phase 1 tiles):
//   openscad -o man9.3mf tile.scad

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

tile();
