# Per-apartment extraction — plan + validated findings

Goal: crop each apartment's plan from the floor-plans sheet, match it to a row in
`data/parsed/apartments.json` (building/floor/stack), and infer its facing.

Decisions (agreed): match floors by **area-fingerprint** (vision-free); emit **one
crop per apartments.json row** (105 rows — repeated typical floors reuse the same
source plate, so their pixels are identical); deliver **crops + a matching JSON**
(app wiring is a later step).

## Validated, vision-free facts

**Scale:** the vector `<Path>` coordinates are **real millimetres** (red mamad
≈12 m², footprint ≈23 m). Area in m² = pixel/þ count × (mm_per_px/1000)².

**The sheet is NOT one plate per floor.** The 105 apartments collapse to **13
distinct area-fingerprints**, i.e. ~11–13 *representative* floor plates are drawn,
each reused by every floor that shares its apartment mix. Black-geometry density
gives ~10–12 drawing bands and there are exactly **11 room-labelled units** — all
consistent. So repeated typical floors will (correctly) share one source crop.

**Stack numbering is per-building** (NOT a physical position):
`B1 s1=109, B2 s1=89, B3 s1=110.5`. So matching must be done *within* a building.

**Area-fingerprints → floors** (sorted m²):

| fingerprint (m²) | building/floors |
|---|---|
| 185 | B1F0 |
| 76,79,89,105.4,109 | **B1F1–6** and **B2F1–4** (same areas — disambiguate by plate order/building) |
| 76,89,109,126,134 | B1F7 and B2F5–6 |
| 148,158 | B1F8, B2F7–8, B3F7–8 (penthouse plate, reused) |
| 76,79,105.4,109.5,110.5 | B3F1–5 |
| 76,79,106 (+…) | B3F0 |

Building order is fixed by the **3 `בנין` title markers** + left→right plate order.

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
