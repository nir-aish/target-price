# Per-apartment extraction — plan + validated findings

Goal: crop each apartment's plan from the floor-plans sheet, match it to a row in
`data/parsed/apartments.json` (building/floor/stack), and infer its facing.

Decisions (agreed): match floors by **area-fingerprint** (vision-free); emit **one
crop per apartments.json row** (105 rows — repeated typical floors reuse the same
source plate, so their pixels are identical); deliver **crops + a matching JSON**
(app wiring is a later step).

## Validated, vision-free facts

**Scale:** the vector `<Path>` coordinates are **real millimetres** (red mamad
≈12 m², footprint ≈23 m). Area in m² = pixel count × (mm_per_px/1000)².

**Sheet layout = a left→right sequence of COMPOSITE floor plans (CORRECTED).**
Each drawn plate is a *whole-site composite* showing **all three buildings at one
floor level** — בנין 1 & 2 on the top row and בנין 3 below, in an L — with a north
arrow and a `תכנית קומה N` title. The sequence runs left→right: basement/ground
(sparse), residential floors, the green landscaped site plan, then the roof/amenity
plate (`תכנית קומה ... 4 דירות`). So a "plate" is a **floor**, not a building.
Confirmed visually on the plates that rendered (3 building footprints + floor
titles per plate). This matches the user's note that floors are *similar but not
identical*: each floor is drawn separately, with small per-floor differences
(e.g. upper floors merge two units into a larger free-market apartment).

**Area-fingerprints** (vision-free): the 105 rows collapse to **7 distinct
sorted-area fingerprints** (see table below) — useful to label a plate's floor
once the plate is located, but matching must be done per building because **stack
numbering is per-building** (B1 s1=109, B2 s1=89, B3 s1=110.5).

**Granularity that works:** composite (=floor) → 3 separable building squares →
5 cells each. So matching is: locate the composite's floor, then within each of its
3 building footprints match the 5 cells to that **(building,floor)** area set below.

**Per-(building,floor) area sets** (sorted m², for matching cells inside a square):

| area set (m²) | building/floors |
|---|---|
| 185 | B1F0 |
| 76,79,89,105.4,109 | B1F1–6, B2F1–4 |
| 76,89,109,126,134 | B1F7, B2F5–6 |
| 148,158 | B1F8, B2F7–8, B3F7–8 |
| 76,79,105.4,109.5,110.5 | B3F1–5 |
| 76,79,106 | B3F0 |

Building order is fixed by the **3 `בנין` title markers** + their L-layout
(בנין 1 & 2 top row, בנין 3 below) within each composite.

**Composite anchors:** the 11 room-labelled living rooms sit at content-x
≈ 272197, 319268, 345787, 368720, 395238, 419303, 445834, 467193, 493724,
514437, 540968 — one or two labelled units per composite; usable as seed points.

**Drawing-band x-ranges** (content mm, from black-geometry density) — candidate plates:
`216718–225756, 272552–300632, 320555–329211, 363804–371439, 415472–419975,
460921–469422, 508954–517546, 556607–565379, 608960–618908, …` (10–12 bands).

**Colour legend:** black=walls/dims, **blue #007FFF/#0080FF = apartment boundary**,
**red #FF0000 = mamad + kitchen cabinetry**, greens=landscaping.

## Pipeline (to run in a session with working image display)

1. **Plates:** split the sheet into floor plates via black-geometry x-bands; read
   each plate's `בנין X / קומה Y` title (vision) OR assign by band order + the area
   fingerprint below. (Floor digits do NOT extract as text — glyphs lack
   `UnicodeString` — so titles need vision; fingerprint is the vision-free fallback.)
2. **Segment apartments per plate.** The blue boundary is the right signal but is
   **dashed**, so raw raster flood-fill is unreliable (undercounts area ~10–30%,
   misses units). Options, best first: (a) trace/stitch blue polylines into closed
   loops → shoelace area; (b) raster flood-fill with tuned closing + **vision check**;
   (c) vision segmentation per plate.
3. **Match:** within each plate, assign each cell to a stack by nearest area in that
   building/floor's fingerprint. Disambiguate identical-fingerprint plates (B1 vs B2
   typical; the penthouse) by building boundary + plate order.
4. **Crop** each cell (`tools/crop_plan.py`, content-space bbox) → save
   `app/plans/units/B{b}_F{f}_S{s}.png`; reuse the source crop for floors that
   share a plate.
5. **Facing:** cell centroid vs plate centre → corner → facing via
   `docs/ORIENTATION.md` (page-up=N, right=E: bottom-right=SE best, etc.).
6. Emit `data/parsed/unit_plans.json`: row → {image, measured_area, fingerprint_area,
   facing, plate}.

## Tools in place
- `tools/xps_reader.py` — transform-aware glyph/path reader (absolute coords;
  needed to read title-block text that lives in nested canvases).
- `tools/extract_geometry.py` — path geometry by colour (mm); area helper.
- `tools/crop_plan.py` — crop any content-space bbox to PNG.
- `tools/extract_text.py` — flat glyph reader (room labels, raw coords).

## Status / blocker
Foundations, scale, structure and the matching method are validated numerically.
Remaining work (plate titles, apartment segmentation, crop verification) needs
**image display**, which failed mid-session on this run. Resume in a fresh session.
