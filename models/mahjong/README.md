# Mahjong Tile Set

A full 144-tile mahjong set with classic symbols, printed on an Elegoo Centauri Carbon 2 with a 0.4 mm nozzle and the four-colour CANVAS system.

Status: **planning**. Nothing printed yet. This document is the design brief and roadmap.

**Confirmed:** Centauri Carbon 2 (CANVAS available) · **solitaire only** — no wall-building, tiles never stand on edge · **3 mm** height, kept as a generator parameter.

---

## 1. The idea

Generate the whole set parametrically rather than modelling 144 tiles by hand: take a CC0 vector tile set, convert each face to an SVG path, and feed it into an OpenSCAD generator that extrudes a tile body with the face inlaid or engraved. One `.scad` file plus 44 face SVGs produces every tile, and changing the tile thickness, corner radius, or face style is a parameter change rather than a remodel.

This reuses the pattern already built in [`openSCAD/Stencil Generator`](../../../openSCAD/) (SVG → 3D with beveled edges) and the artwork conventions in [`stencils`](../../../stencils/).

---

## 2. Tile height — 3 mm, settled

The set is for **mahjong solitaire only**: tiles are laid face-up in a stacked layout and matched in pairs. They are never stood on edge and never form a wall. That removes the only argument for a tall tile, and the original **3 mm** figure is the right answer rather than a compromise.

| Option | Height | Behaviour | Print cost (est.) |
| --- | --- | --- | --- |
| **A. Flat** ✅ | 3 mm | Lies flat, stacks in layers; solitaire | ~410 g, ~12–15 h |
| B. Standard | 16 mm | Full-size wall tile, ~18 g each | ~2.2 kg, ~4–5 days |
| C. Half-height | 8 mm | Stands in a wall, half the print | ~1.1 kg, ~2 days |

Going flat is worth roughly **five times less filament and a day less printing** than a standing set — solitaire is by far the cheaper game to print.

Height stays a `tile_h` parameter in the generator anyway. It costs nothing to keep, and it means a wall set later is a re-slice rather than a redesign.

Two things that follow from flat tiles:

- **A solitaire layout stacks up to five layers deep.** At 3 mm that is a 15 mm pile — low, stable, easy to see across. Standard 16 mm tiles would make an 80 mm tower.
- **They will feel light** — ~2.9 g against ~18 g for a real tile. For solitaire that is mostly fine, since tiles are slid and lifted rather than slammed. If it bothers you, 5 mm is the cheapest fix and still stacks low.

**Do not scale the face down.** The 32 × 24 mm face is what makes the 0.4 mm nozzle viable — see §4 — and it is independent of height. A thin tile with a shrunken face is the one combination that fails.

One optional extra, cheap because the generator already exists: a shallow **0.4 mm register recess** on the tile back, matching the face outline, so stacked layers key into the tiles below instead of sliding. Worth a parameter and a test tile; not required.

---

## 3. Printer notes

**Elegoo Centauri Carbon 2**, 0.4 mm nozzle, with the four-colour **CANVAS** system. 256 × 256 × 256 mm CoreXY, fully enclosed, 320 °C hardened nozzle, 110 °C bed.

(For the record, since it came up: there is no "Centauri Carbon 3." The line is the original Centauri Carbon, and the Centauri Carbon 2 / 2 Combo launched January 2026 — the CC2 is what adds CANVAS. CANVAS also shipped as a $55 add-on for the original in April 2026.)

This is the good case. Four colours resolves §5 outright — classic polychrome faces come off the plate finished, with no pauses, no filament swaps, and no hand-painting. The 256 mm bed takes a large plate of tiles, and the enclosure gives a stable chamber for a long multi-colour run.

---

## 4. Why the 0.4 mm nozzle works — but only at full face size

The binding constraint is the 萬 (*wàn*) character on the Characters suit: roughly 12 strokes stacked inside one glyph.

The rule of thumb for FDM text is that a stroke narrower than the extrusion width will not form, and **a stroke that gets fewer than two extrusion lines is likely to fail**. With a 0.4 mm nozzle at ~0.42 mm line width, that sets a floor of **≈ 0.85 mm minimum stroke width**.

| Face size | 萬 glyph height | Approx. stroke width (bold CJK) | Verdict |
| --- | --- | --- | --- |
| 32 × 24 mm | ~14 mm | ~1.0–1.2 mm | ✅ comfortable |
| 26 × 20 mm | ~11 mm | ~0.8–0.9 mm | ⚠️ marginal |
| 24 × 18 mm | ~10 mm | ~0.7–0.8 mm | ❌ strokes merge |

So: **keep the face at 32 × 24 mm**, use a heavy CJK weight (Noto Sans CJK Bold / Source Han Sans Heavy), and add a small outward offset to any glyph whose strokes measure under 0.85 mm. A 0.2 mm nozzle would lift the ceiling considerably, but at 144 tiles the print time makes that a poor trade.

Other geometry rules that follow from the nozzle:

- Inlay depth: **~0.5 mm** — 3 layers at 0.16 mm, the coloured region of a face-down print
- Gap between adjacent strokes: **≥ 0.8 mm**, or they fuse into a blob
- Corner radius 3 mm, and a 0.4 mm × 45° chamfer on the bottom edge to absorb elephant's foot
- A light chamfer on the top face edge too — on a 3 mm tile there is almost nothing to grip, and a chamfered edge is what lets a fingernail lift one tile off a stack

---

## 5. Colour — solved by CANVAS

On a single-extruder machine this is the hardest part of the project: a pause-and-swap changes colour for *every* object on the plate at that Z height, so you get one accent colour per plate and classic polychrome means hand-painting 144 tiles. **CANVAS removes the problem entirely.** Four colours, no pauses, correct classic colours off the plate:

| Slot | Filament | Used for |
| --- | --- | --- |
| 1 | Ivory / bone white | Tile body and face background |
| 2 | Red | 萬 character, 中, the 1-bamboo bird, red dots |
| 3 | Green | 發, bamboo sticks, green dots |
| 4 | Blue / black | Suit numerals, winds, blue dots, 白 frame |

That covers every classic face. Four slots is exactly enough — which is lucky, and worth not spending: don't add a fifth accent colour to the artwork.

### Build it as a face-down inlay

Print **face-down on smooth PEI**, with the coloured symbol occupying the **first 3 layers (~0.5 mm)** and the body printing above it. This is the same technique as the single-extruder two-tone trick, just with CANVAS doing the swaps:

- The face comes out **dead flat and glossy** against the build plate — the closest thing to real melamine tiles you'll get off an FDM printer.
- Colour is *inlaid*, not printed on top, so it cannot scuff off with handling. On a set that gets shuffled every game, this matters more than it sounds.
- Colour is confined to the bottom 0.5 mm, which bounds purge waste — see below.
- No supports, no painting, no post-processing.

### The one real cost: purge waste

Every colour change on a single-nozzle multi-material system flushes the old filament out. Rough order of magnitude: **~0.5–1 g per change**, and the arithmetic is what decides whether this is trivial or ruinous.

The saving grace is that the slicer groups by colour **across the whole plate**, not per tile. On a given layer it prints every red region on every tile, then swaps once, then every green region, and so on. So the cost is roughly:

> (colours on the layer − 1) × (number of face layers) × (grams per change)

At 4 colours over 3 face layers that's ~9 changes per plate, call it **~5–10 g per plate**, so ~15–30 g across the three plates. Against a ~410 g set that is a few per cent — worth measuring, not worth worrying about. Above the face, the tile is single-colour ivory and there are no changes at all.

Note this is one place where the flat tile is *less* forgiving: purge is a fixed cost per plate, so on a 410 g set it is a larger share than it would be on a 2 kg one. It is still small; it just means don't be careless with flush volumes.

**The rule that keeps it that way: confine colour to the face layers.** If the design puts colour anywhere in the body, or the slicer decides to alternate colours up the stack, the change count multiplies by the layer count and the purge tower can outweigh the tiles. Verify this on the Phase 4 test plate by reading the slicer's flush estimate before committing to a full run — it reports it directly.

Set the purge/flush volumes properly for the light-to-dark transitions (ivory→red is cheap, red→ivory is expensive; the slicer's matrix handles this if you let it). Keep the purge tower on — with this few changes it costs almost nothing and prevents colour bleed into the faces.

---

## 6. Tile inventory (144)

| Group | Symbols | Distinct | ×4 | Total |
| --- | --- | --- | --- | --- |
| Characters (萬 / craks) | 一–九 萬 | 9 | 4 | 36 |
| Bamboo (索 / sticks) | 1–9 | 9 | 4 | 36 |
| Dots (筒 / circles) | 1–9 | 9 | 4 | 36 |
| Winds | 東 南 西 北 | 4 | 4 | 16 |
| Dragons | 中 發 白 | 3 | 4 | 12 |
| Flowers | 梅 蘭 菊 竹 | 4 | 1 | 4 |
| Seasons | 春 夏 秋 冬 | 4 | 1 | 4 |
| | | **42** | | **144** |

Solitaire needs the full 144 — the layout is built from 72 pairs, so **flowers and seasons are not optional here** even though they are only 8 tiles. In solitaire they match within their group (any flower pairs with any flower, any season with any season), which is why they appear once each rather than four times.

Add 4 blanks as spares — tiles get lost, and a spare is free while the plate is already running.

---

## 7. Artwork pipeline

**Source:** [FluffyStuff/riichi-mahjong-tiles](https://github.com/FluffyStuff/riichi-mahjong-tiles) — complete vector tile set, released **CC0 (public domain, no attribution required)**. This is the cleanest licence of the options; the Wikimedia Commons tile SVGs are CC BY-SA 4.0, which would drag a share-alike obligation into the repo for no benefit.

```mermaid
flowchart LR
    A["CC0 tile SVGs<br/>(FluffyStuff)"] --> B["Strip tile border,<br/>keep face symbol only"]
    B --> C["Split by colour<br/>red / green / blue"]
    C --> D["Flatten each to a<br/>filled path, close gaps"]
    D --> E["Widen strokes<br/>to at least 0.85 mm"]
    E --> F["44 faces x per-colour SVGs<br/>faces/&lt;tile&gt;-&lt;colour&gt;.svg"]
    F --> G["tile.scad<br/>parametric generator"]
    G --> H["144 multi-part 3MFs<br/>one body per colour"]
    H --> I["ElegooSlicer<br/>assign CANVAS slots"]
    I --> J["Printed set"]
```

Two steps carry the risk:

- **`C` — colour separation.** CANVAS means each face is no longer one path but one path *per colour*, all sharing the same face plane. They must tile the face exactly: any gap shows as an ivory hairline, any overlap is a geometry conflict the slicer resolves unpredictably. Build the accent shapes to butt exactly, and let the ivory background be everything not covered.
- **`E` — stroke widening.** A per-glyph check against the 0.85 mm floor, not a blanket offset, or the dots suit bloats. Note this now applies *per colour region*: a 0.6 mm red stroke sitting inside a green shape is just as unprintable as one on bare ivory.

Export as **multi-part 3MF rather than STL** — one part per colour, all in a common origin. STL cannot carry the part separation, and re-aligning four meshes per tile by hand 144 times is not a plan.

---

## 8. Draft print settings

Starting point, to be corrected by the test plate:

| Setting | Value | Why |
| --- | --- | --- |
| Layer height | 0.16 mm | Finer steps on the inlay; 3 mm = 19 layers, the face is the first 3 |
| First layer | 0.20 mm | Adhesion for a large flat footprint |
| Line width | 0.42 mm | Default for 0.4 nozzle |
| Walls | 3 | Crisp tile edges |
| Top/bottom layers | 5 / 5 | At 3 mm the tile is nearly solid regardless |
| Infill | 100 % | Weight and a solid "clack"; at 19 layers it is almost free |
| Material | PLA or PLA+ | Stiff, dimensionally stable, cheap at 144 parts |
| Bed / plate | Smooth PEI, face-down | Glossy face, closest to real melamine tiles |
| Elephant-foot comp. | 0.15–0.20 mm | Keeps the inlaid face edge sharp |
| Brim | Off, unless corners lift | Thin wide parts are the classic curl case |
| Colour | CANVAS, 4 slots | §5 — colour confined to the bottom 3 layers |
| Purge tower | On | Cheap at ~9 changes/plate; prevents bleed into faces |
| Flush volumes | Slicer defaults, then tune | Dark→ivory is the expensive transition |

Chamber: leave the door ajar for PLA — the enclosure is an asset for ABS but PLA will heat-creep in a sealed hot chamber.

The setting that actually decides success here is **elephant-foot compensation**, not infill. On a 19-layer tile the first layer is a much larger share of the part, so first-layer squish shows up directly as a fattened, blurred face edge. Dial it in on the Phase 1 tile.

---

## 9. Budget (estimates, not measured)

At **3 mm**, per §2.

- **Per tile:** 32 × 24 × 3 mm ≈ 2.3 cm³ ≈ **2.9 g** solid PLA
- **Set:** ~410 g body filament, plus ~15–30 g purge across three plates → comfortably **one spool**
- **Plate capacity:** ~48–63 tiles at 2–4 mm spacing → **3 plates**
- **Time:** roughly 4–5 h per plate, **~12–15 h total**

The whole set fits in a single spool and a couple of evenings. That is the solitaire dividend: a wall set is five spools' worth of plastic and the better part of a week.

Reality check on feel: a real size-32 tile is ~18 g, these are ~2.9 g, and **they will feel light**. For solitaire it matters much less than it would for a wall game — you slide and lift tiles rather than stand or slam them — but it is a real difference, not something the settings will hide. If it bothers you after Phase 1, raise `tile_h` to 5 mm: still stacks low, still one spool, ~5 g per tile.

---

## 10. Roadmap

```mermaid
flowchart TD
    P1["Phase 1 — Single test tile<br/>5-dot + 9-characters<br/>Validate stroke width"] --> P2
    P2["Phase 2 — Artwork pipeline<br/>44 faces, split per colour"] --> P3
    P3["Phase 3 — tile.scad<br/>Parametric generator + 3MFs"] --> P4
    P4["Phase 4 — Test plate<br/>~12 tiles, check purge<br/>+ stack a 3-layer pile"] --> P5
    P5["Phase 5 — Full run<br/>3 plates, 144 tiles"] --> P6
    P6["Phase 6 — Storage<br/>Box, trays, tile backs"]
```

Phase 0 is gone — printer, colour route, game, and height are all settled. This is now a straight build.

**Phase 1 — One test tile.** Print **9-characters** (the densest glyph) and **5-dots** at full 32 × 24 mm × 3 mm, single colour. This is the entire technical risk of the project in a 20-minute print. If 九萬 comes out legible, nothing else here is hard. Check the weight in the hand at the same time — it is the cheapest moment to decide whether 3 mm is too light.

**Phase 2 — Artwork.** Extract 44 faces from the CC0 set, strip borders, flatten to filled paths, **split each face into per-colour SVGs**, and audit every region against the 0.85 mm floor. The slowest phase and the one that decides how good the set looks. The colour split is new work that the single-colour plan did not have.

**Phase 3 — Generator.** `tile.scad` with parameters for size, `tile_h`, corner radius, chamfer, inlay depth, face style, and the optional back register recess from §2. Batch-export 144 **multi-part 3MFs**, one body per colour.

**Phase 4 — Test plate.** ~12 tiles covering every suit and every colour. Check the slicer's flush estimate against the §5 budget, tune elephant-foot compensation and spacing, and confirm no corner lift across a full-width plate — thin flat parts are where curl actually happens. Then **stack them three layers deep and push the pile around**: solitaire only works if tiles sit on each other without sliding, and that is the one thing a single test tile cannot tell you.

**Phase 5 — Full run.** Three plates, ~12–15 h. Nothing to sort by colour; CANVAS handles it.

**Phase 6 — Storage.** A box and stacking trays, sized off *measured* tiles rather than nominal ones. Flat tiles store well — 144 at 3 mm is a stack about the size of a paperback.

---

## 11. Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| 萬 strokes merge at 0.4 mm | Medium | Phase 1 test tile settles it before any bulk work |
| Ivory hairlines at colour boundaries | Medium | Phase 2 — coloured regions must butt exactly, not merely abut visually |
| Thin flat tiles curl at the corners | Medium | Enclosure, smooth PEI, chamfered bottom, brim if the test plate lifts |
| Purge waste blows past the §5 estimate | Medium | Colour must stay in the face layers; check the flush estimate on the Phase 4 plate |
| Tiles feel too light | Certain at 3 mm | Accept it — solitaire tolerates it — or go to 5 mm after Phase 1 |
| Stacked layers slide apart in play | Medium | Test a 3-layer pile at Phase 4; the §2 back recess is the fix if it does |
| Colour bleeds between slots | Low | Purge tower on, tune flush volumes for dark→ivory |

## 12. Open questions

1. Chinese, Hong Kong, or Riichi face conventions? (Affects flowers and the 白 dragon — blank vs framed.)

That is the only one left. Printer, colour route, game, and height are all settled — nothing is blocked on an answer, since the face convention only bites in Phase 2.

---

## Sources

- [Elegoo Centauri Carbon — official product page](https://us.elegoo.com/products/centauri-carbon)
- [Elegoo Centauri Carbon 2 Combo launch (Jan 2026)](https://tools.prnewswire.com/en-us/live/20813/release/20260119EN65865)
- [CANVAS multi-colour system for Centauri Carbon](https://www.creativebloq.com/3d/elegoo-launches-the-multi-colour-system-long-promised-for-its-best-selling-centauri-carbon-3d-printer)
- [World Mahjong Organization tile size standard](https://www.chinadaily.com.cn/china/2011-11/24/content_14150841.htm)
- [Mahjong tile size guide](https://mahjongplaybook.com/american-majong/mahjong-tile-size-guide/)
- [FluffyStuff/riichi-mahjong-tiles — CC0 vector tiles](https://github.com/FluffyStuff/riichi-mahjong-tiles)
- [Wikimedia Commons mahjong tile SVGs (CC BY-SA 4.0)](https://commons.wikimedia.org/wiki/Category:SVG_illustrations_of_Mahjong_tiles)
- [Readable 3D printed text — best practices](https://mandarin3d.com/blog/text-and-engravings-best-practices-for-readable-3d-printed-text)
- [FFF design rules — minimum feature size](https://www.hydraresearch3d.com/design-rules)
