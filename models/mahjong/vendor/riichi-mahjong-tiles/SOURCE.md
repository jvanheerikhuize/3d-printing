# Vendored artwork

| | |
| --- | --- |
| Upstream | [FluffyStuff/riichi-mahjong-tiles](https://github.com/FluffyStuff/riichi-mahjong-tiles) |
| Licence | CC0 1.0 — public domain (see [LICENSE.md](LICENSE.md)) |
| Vendored | 2026-07-25 |
| Files | `Man9.svg`, `Pin5.svg` — copied verbatim from `Regular/` |

Only the two Phase 1 faces are vendored. The rest of the 44 arrive in Phase 2.

## Why these two

`Man9` (九萬) is the densest glyph in the set — if its strokes survive a 0.4 mm
nozzle, nothing else in the set is harder. `Pin5` is the opposite case: large
concentric circles, which stress the *gap* rule rather than the stroke rule.

## Canvas

Both files are `width="300" height="400" viewBox="0 0 300 400"` — a 3:4 ratio
that maps exactly onto the 24 × 32 mm tile face chosen in
[../../README.md](../../README.md) §4.

The artwork is already colour-separated at source, which is what makes the
Phase 2 colour split a filtering job rather than a redraw. Flattened path counts
per fill, as reported by `tools/extract_face.py`:

| Face | Fills |
| --- | --- |
| `Man9` | red ×8 (the 萬), black ×3 (the 九) |
| `Pin5` | black ×5, white ×15, navy ×8, red ×2 |

Two traps live in those numbers.

`Pin5`'s five black paths carry **no fill attribute at all** — they are black by
SVG's initial value, not by declaration. Treating an absent fill as "unpainted"
drops the outer ring of every dot, silently, from every colour layer.

And the layers are a **z-stack, not a partition**. `Pin5` is a thick black disc,
then a white ring, then a navy disc, then white spokes over the navy, then a
centre dot. Unioning them gives a plain circle; everything that makes it a 5-dot
is in the boundaries between them. The subtraction that recovers a colour's
exclusive region belongs in OpenSCAD — see `tile.scad`'s `face_add` / `face_sub`
and README §4, "Dots as relief".

Upstream files also carry unused template geometry in `<defs>` (an orange guide
path, three construction circles, a red background rect). `tools/extract_face.py`
discards it — see that script's header.
