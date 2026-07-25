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
| `export/man9-solid.3mf` | 九萬 — the densest glyph in the set |
| `export/pin5-solid.3mf` | 5-dot — five annuli, the gap-rule case |

(`<face>-test.3mf` is the Phase 2 tricolour tile, not this one.)

Both are 24 × 32 × 3 mm, origin at the plate, face engraved 0.5 mm into the
**+Z** side. Previews in `img/`.

## Regenerating them

Needs OpenSCAD (2021.01 or later — SVG `import()` is required).

```sh
cd models/mahjong
openscad -o export/man9-solid.3mf tile.scad
openscad -o export/pin5-solid.3mf \
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

**Slice this one:**

| File | What it is |
| --- | --- |
| `export/man9-test.3mf` | 九萬, all three colours, one object |
| `export/pin5-test.3mf` | 5-dot, all three colours, one object |

Each holds three named parts carrying their display colours:

| Part | Filament | Colour | Where it sits |
| --- | --- | --- | --- |
| `glyph` | Black | `#1A1A1A` | Top 0.48 mm — the symbol, inlaid flush |
| `body` | White | `#F2F2F2` | 0.48 → 3 mm — everything else |
| `back` | Wood-fill | `#9E7042` | Bottom 0.48 mm |

The individual bodies are still there as `export/<face>-{back,body,glyph}.3mf`
if you want to inspect or re-mix one, but there is no longer any reason to load
them by hand. Previews: `img/man9-tricolour.png`, `img/pin5-tricolour.png`
(shown exploded — in the file the parts are coincident).

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

for f in man9 pin5; do
  tools/merge_3mf.py export/$f-test.3mf \
    back=#9E7042=export/$f-back.3mf \
    body=#F2F2F2=export/$f-body.3mf \
    glyph=#1A1A1A=export/$f-glyph.3mf --name "$f tile"
done
```

Two steps because OpenSCAD 2021.01 writes one object per 3MF and drops
`color()` on export. `tools/merge_3mf.py` packs the bodies into one file as a
component assembly with base materials — see that script's header for why
components rather than three build items.

## Assembling in ElegooSlicer

Import `export/<face>-test.3mf`. That is all — it arrives as a single object
with three parts already positioned.

Then check two things before slicing:

1. The object's size reads **24 × 32 × 3 mm**. If it reads three objects on the
   plate instead of one, your slicer flattened the component assembly; the parts
   still share an origin, so select all three and group them.
2. Each part is pointed at the right physical spool. The display colours are a
   hint the slicer is free to ignore, and it does not know which extruder holds
   wood-fill. Part names are `back`, `body`, `glyph`.

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
