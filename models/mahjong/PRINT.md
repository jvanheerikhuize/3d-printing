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

---

# Phase 2 tricolour tile — print note

Black symbol, white tile, wood back (README §5). Three filaments, three bodies
per tile, one object on the plate.

## Files

| File | Filament | Where it sits |
| --- | --- | --- |
| `export/<face>-glyph.3mf` | Black | Top 0.48 mm — the symbol, inlaid flush |
| `export/<face>-body.3mf` | White | 0.48 → 3 mm — everything else |
| `export/<face>-back.3mf` | Wood-fill | Bottom 0.48 mm |

`<face>` is `man9` or `pin5`. All six share the same origin and the same
24 × 32 × 3 mm envelope, so they need no alignment beyond being loaded together.
Previews: `img/man9-tricolour.png`, `img/pin5-tricolour.png` (shown exploded).

## Regenerating them

```sh
cd models/mahjong
for p in back body glyph; do
  openscad -o export/man9-$p.3mf -D "part=\"$p\"" tile.scad
  openscad -o export/pin5-$p.3mf -D "part=\"$p\"" \
    -D 'face_add=["faces/pin5-black.svg","faces/pin5-navy.svg","faces/pin5-red.svg"]' \
    -D 'face_sub=["faces/pin5-white.svg"]' \
    tile.scad
done
```

One file per body because OpenSCAD 2021.01 cannot write several objects into a
single 3MF. The slicer does the assembly.

## Assembling in ElegooSlicer

1. Import `<face>-body.3mf`. This is the parent.
2. Right-click it → **Add part → Load** → pick `<face>-glyph.3mf`, then again for
   `<face>-back.3mf`. Loading them as *parts* is what matters; importing them as
   three separate objects drops them at three different plate positions and the
   shared origin is lost.
3. Confirm the object's size still reads **24 × 32 × 3 mm**. If it grew, one of
   the parts came in as a sibling object rather than a part.
4. Assign filaments per part: body → white, glyph → black, back → wood.

## Slicing

Same as Phase 1 except:

- **Orientation: face down.** The opposite of the Phase 1 tile. The face is then
  ironed flat against smooth PEI, and the black glyph is inlaid rather than sat
  on top of the white — it cannot scuff off in a game's worth of shuffling.
- Layer height **0.16 mm** — both 0.48 mm bands are exactly three layers, so no
  colour boundary lands mid-layer.
- Elephant-foot compensation **0.15–0.20 mm**. This now acts on the *face*, and
  first-layer squish shows directly as a fattened, blurred symbol edge. It is the
  setting that decides whether this print looks good.
- Purge tower **on**; expect ~4 changes on a plate (README §5).
- No supports, no brim.

## What to look at afterwards

- Is the black symbol **flush** with the white face, or can you feel a step or a
  ridge with a fingernail? A step means the glyph body and the body's cavity
  disagree, which should be impossible by construction — if you feel one, say so,
  because it means the partition broke.
- Any **white bleeding into the black** at the boundary, or vice versa? That is a
  flush-volume problem, not a geometry one — raise the purge for that transition.
- Do the 0.48 mm bands read as crisp colour boundaries, or is there a smeared
  layer where the colour changes?
- Does the wood back look like wood at arm's length, or just brown?
- Weigh one against the Phase 1 tile — should be within a few per cent.
