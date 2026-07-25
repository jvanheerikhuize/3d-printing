# Phase 1 test tile — print note

Two tiles, single colour, ~20 minutes. The point is not to get a usable tile;
it is to answer two questions that no amount of modelling settles:

1. **Do the 萬 strokes survive a 0.4 mm nozzle at a 24 mm face?**
   `tools/check_strokes.py` says no (README §4). Print it anyway — the script
   measures the artwork, not the printer, and a photograph of the real thing is
   what decides whether the failure is cosmetic or fatal.
2. **How does 3 mm feel in the hand?** Nothing but holding one answers this.

## Files

Pre-exported, ready to slice:

| File | What it is |
| --- | --- |
| `export/man9-test.3mf` | 九萬 — the densest glyph in the set |
| `export/pin5-test.3mf` | 5-dot — five annuli, the gap-rule case |

Both are 24 × 32 × 3 mm, origin at the plate, face engraved 0.5 mm into the
**+Z** side. Previews in `img/`.

## Regenerating them

Needs OpenSCAD (2021.01 or later — SVG `import()` is required).

```sh
cd models/mahjong
openscad -o export/man9-test.3mf tile.scad
openscad -o export/pin5-test.3mf \
  -D 'face_add=["faces/pin5-black.svg","faces/pin5-navy.svg","faces/pin5-red.svg"]' \
  -D 'face_sub=["faces/pin5-white.svg"]' \
  tile.scad
```

Pin5 needs the `face_sub` because the artwork is a z-stack — see README §4,
"Dots as relief".

## Slicing (Centauri Carbon 2, 0.4 mm nozzle)

- **Orientation: face up.** The engraved glyph is then a real top surface rather
  than a bridged void. (Phase 2 inverts this — flat face, printed face *down*,
  colour carried by separate bodies.)
- Layer height **0.16 mm** — 0.5 mm of relief is exactly three layers.
- Top layers **≥ 5**, so the engraved floor is solid.
- Infill **≥ 25 %**; on a 3 mm slab this costs almost nothing and the tile should
  feel dense.
- No supports. No brim — the 0.4 mm bottom chamfer is the elephant's-foot
  allowance.
- Print both on one plate.

## What to look at afterwards

- Hold the 萬 up to a light. Are the horizontal strokes separate, or have any
  pairs fused into a blob? Count how many.
- Run a fingernail along the top edge. Can you lift this tile off a stack? That
  is what `chamfer_face = 0.6` is for; if not, raise it.
- Do the pin5 rings read as rings at arm's length?
- Weigh one. The budget in README §9 assumes ~2.9 g; 144 tiles multiplies any
  error by a lot.

Record the answers in README §12 before starting Phase 2.
