# Per-apartment extraction — plan + validated findings

Goal: crop each apartment's plan from the floor-plans sheet, match it to a row in
`data/parsed/apartments.json` (building/floor/stack), and infer its facing.

Decisions (agreed): emit **one crop per apartments.json row** (105 rows — repeated
typical floors share a source plate, so their pixels are identical); deliver
**crops + a matching JSON** (app wiring is a later step).

## Validated facts

**Scale:** the vector `<Path>` coordinates are **real millimetres** (red mamad
≈12 m², footprint ≈23 m). Area in m² = filled-pixel count × (mm_per_px/1000)².

**Sheet layout = a left→right sequence of COMPOSITE floor plans.**
Each drawn plate is a *whole-site composite* showing **all three buildings at one
floor level** — בנין 1 & 2 on the top row and בנין 3 below, in an L — each with a
north arrow and a `תכנית קומה N` title. The sequence runs left→right: basement/
ground (sparse) → residential floors → the green landscaped site plan → roof/
amenity (`תכנית קומה … 4 דירות`). So a "plate" = a **floor**, not a building.
This matches the note that floors are *similar but not identical*: each floor is
drawn separately (e.g. upper floors merge two units into a larger free-market apt).

**Floor titles are READABLE (vision) — floor identification is solved.** Read this
session from each composite's title block (living-room anchor index → floor):

| anchor i | living-x | floor title |
|---|---|---|
| 0 | 272197 | קומה 6 |
| 1 | 319268 | קומה 5 |
| 3 | 368720 | קומה 4 |
| 5 | 419303 | קומה 3 (top-row square = בנין 2) |
| 6 | 445834 | קומה 1 |
| 7 | 467193 | קומה 0 (ground) |
| 9 | 514437 | קומה -1 |

(Anchors 2,4,8,10 read the same way; floor digits do NOT come out as text — the
glyphs lack `UnicodeString` — so titles require vision.)

**Stack numbering is per-building** (NOT a physical position):
`B1 s1=109, B2 s1=89, B3 s1=110.5`. Match cells to stacks *within* a building.

**Per-(building,floor) area sets** (sorted m², for matching cells inside a square):

| area set (m²) | building/floors |
|---|---|
| 185 | B1F0 |
| 76,79,89,105.4,109 | B1F1–6, B2F1–4 |
| 76,89,109,126,134 | B1F7, B2F5–6 |
| 148,158 | B1F8, B2F7–8, B3F7–8 |
| 76,79,105.4,109.5,110.5 | B3F1–5 |
| 76,79,106 | B3F0 |

Building order within a composite is fixed by the **3 `בנין` title markers** + the
L-layout (בנין 1 & 2 top row, בנין 3 below).

**Colour legend:** black=walls/dims, **blue #007FFF/#0080FF = apartment boundary**,
**red #FF0000 = mamad + kitchen cabinetry**, greens=landscaping.

> ⚠️ **TWO COORDINATE SYSTEMS — do not mix.** The flat regex path-extraction and
> the `mutool` render (`p2.png`, `CONTENT_X_MAX≈691204`, living rooms at x≈272197…)
> share one space. `tools/xps_reader.py` applies the page's 0.08 canvas transform,
> so its coords are **0.08×** (living rooms at x≈21776…). Geometry that must line up
> with the render MUST use the flat space. Mixing them is why the first
> `segment_units` pass found 0 squares.

## What works / what's hard

- **Locating a building square works** (`black`-footprint bbox → a clean ~20×15 m
  plate showing the 5 blue-outlined apartments around the core). Cropping a whole
  square is reliable today.
- **Rasterising the linework as continuous segments works** (95k segments → dense
  mask). The cached `geo_*.npy` are path *vertices only*, so filling those leaks —
  you must draw the **segments** between consecutive vertices.
- **Per-cell area via flood-fill is the hard part and is NOT solved yet.** Even with
  a dense segment mask, apartments connect to the core/corridor through **door
  openings**, so an interior region floods out to the exterior → 0 clean cells.
  This is the standard floor-plan-vectorisation problem. Viable approaches:
  1. **Vectorise the blue boundary**: snap/stitch the dashed blue polylines into
     closed loops (bridge gaps ≤ threshold), then shoelace each loop → area. The
     blue layer is *meant* to delimit each apartment, so this is the most faithful.
  2. **Close door gaps before filling**: detect short wall gaps (door swings) and
     bridge them, or seed-fill from each apartment interior with a strong
     `binary_closing`, validating against the expected 5-area set.
  3. **Vision-assisted**: for each square crop, identify the 5 cells visually and
     read each unit's labelled/penthouse area; use geometry only for the crop bbox.

## Tools in place
- `tools/xps_reader.py` — transform-aware glyph/path reader (0.08× space; reads
  title-block text in nested canvases — used to read room labels & `בנין`/`קומה`).
- `tools/extract_geometry.py` — path geometry by colour (flat mm); bbox/area helper.
- `tools/crop_plan.py` — crop any content-space (flat) bbox to PNG.
- `tools/extract_text.py` — flat glyph reader (room labels, raw coords).
- `tools/segment_units.py` — segmentation skeleton; **needs fixing**: use the flat
  coordinate space (not xps_reader's 0.08×) and rasterise segments, then adopt the
  blue-loop or door-gap-closing method above for per-cell areas.

## Segmentation attempts — what failed and why (honest record)
1. **Flood-fill on a black/all-colour segment mask** → 0 clean cells: apartments
   connect to the core/corridor through **door openings**, so an interior leaks to
   the exterior.
2. **Blue-boundary "legal outline" flood-fill** → also 0 cells. Rendering the blue
   mask of one square (`/tmp/blue_mask.png` this session) shows the blue layer is
   **fragmented tick-marks / short segments, NOT closed apartment loops** — so it
   can't be filled either. (An intermediate commit wrongly claimed this produced
   "5 clean cells"; that was false and was reverted.)

**Conclusion:** automatic per-cell area from any single colour layer is the genuine
hard floor-plan-vectorisation problem and is **not** solved by simple raster fill.

## Status (end of this session)
**Solved:** structural model (composite=floor); scale=mm; the 2-coord pitfall;
**floor identification by reading the `תכנית קומה N` title (vision)**;
per-(building,floor) area sets; **whole building-square cropping**; the facing rule
(corner vs square centre, up=N/right=E).

**Not solved:** fully-automatic per-cell **area** measurement (see attempts above).

**Recommended path to a complete dataset (chosen: vision-assisted):** geometry for
the reliable parts (locate composite, read floor title, crop each building square),
then **identify the 5 cells per square visually** (the squares render clearly) and
take each unit's area from the price list to assign the stack. This yields per-unit
crops + facing + stack match without depending on the unsolved auto-segmentation.
A future pure-automatic route would need real polyline vectorisation (snap+close
walls into rooms, or merge rooms within a blue/■ boundary), not raster fill.

No `unit_plans.json` is committed until it carries real matched data.
