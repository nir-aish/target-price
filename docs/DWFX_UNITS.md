# Can we parse the DWFx into a per-apartment understanding?

Investigation of the question: *parse the `.dwfx` to know which apartment sits
where, crop its plan, and extract attributes (rooms, kitchen-vs-living)*.

**Short answer:** Partly — and the limit is the file, not the tooling. The
`.dwfx` is an AutoCAD **ePlot** (a flattened 2D plot). It has vector geometry
(`<Path>`) and positioned text (`<Glyphs>`) but **no semantic room/space
objects**. So "rooms" exist only where the draughtsman *typed a label*, and the
draughtsman labelled exactly **one representative apartment**.

## What's in the floor-plans sheet (page 2, 46 MB fpage)

- ~11 floor plates in a horizontal row — each the **full square building
  footprint** (≈5 apartments around a central stair/lift core). Renderable and
  croppable to any building or any single apartment cell.
- Apartment cells are drawn with **walls, furniture blocks, plumbing fixtures,
  window specs (`H=135 U.K=80`) and cm wall-dimensions**.
- **Exactly one apartment per plate carries room-name + m² text** — and it is the
  *same* unit repeated ~11× (every area value — `43.4, 12.3, 10.1, 8.2, 5.1,
  3.8, 3.7` — appears exactly 11×). The other apartments are geometry only.

### Correction to an earlier assumption
`101 / 102 / 105 / 108` are **wall dimensions in cm**, not apartment IDs. They
recur ~90× across the sheet and at many y-positions inside dimension strings.
There are **no `דירה` / `טיפוס` (apartment/type) identifiers anywhere** in the
text layer of any of the three sheets.

## Goal-by-goal verdict

| Goal | Verdict | Why |
|---|---|---|
| **Crop a specific plan for reference** | ✅ Works | `tools/crop_plan.py` crops any building/apartment in content coords. |
| **Which apartment sits where (geometrically)** | ✅ Works | Plates render; footprint + orientation (`docs/ORIENTATION.md`) place each corner. |
| **Key an apartment to a price-list stack (1–5)** | ❌ Not from this file | No unit IDs in the text layer; the stack↔corner map still needs the מפרט מכר. |
| **Room list + count** | ⚠️ One unit only | Only the single labelled unit yields room names. Others have no room text. |
| **m² per room** | ⚠️ Living only | Living `43.4 m²` is reliable; the other m² values can't be reliably paired to rooms from label positions (balcony/room tags intermix). |
| **Relative layout (N/S/E/W of each room)** | ✅ For the labelled unit | From label x,y + orientation: balconies N, bedrooms/wet-rooms W/SW, living centred. |
| **Kitchen vs. living position** | ❌ Not available | **No `מטבח` label anywhere** — the kitchen is open-plan inside `מגורים`. Only geometry (counter/sink symbols) could hint at it, which is fragile and unreliable. |

## Artifacts produced
- `tools/parse_units.py` → `data/parsed/labeled_unit.json` — the one labelled
  unit's room set, relative layout, living area, and the unassigned m² pool
  (with an explicit caveat instead of a fabricated 1:1 mapping).
- `tools/crop_plan.py` — crop any region of a sheet by content-space bbox.

## "Are there tools online that would do better?"
- **Autodesk Platform Services (APS / former Forge) Model Derivative API**, ODA
  Drawings SDK, etc. extract a real object tree + properties + geometry — **but
  only recover semantics that exist in the *source*.** A DWFx ePlot has already
  discarded them, so these tools would return the same flattened paths/text.
- The real unlock is the **upstream model or sales spec**, in order of value:
  1. **מפרט מכר / sales brochure PDFs** — per-apartment plans with `כיוונים`
     (directions), room schedules, and the kitchen explicitly drawn/called out.
     Fastest authoritative source; also resolves the stack↔corner mapping.
  2. **Original Revit `.rvt`** — rooms, areas, names as first-class objects;
     APS would then yield a clean per-room dataset including the kitchen.
  3. **Original DWG** with layers intact — room text on its own layer plus
     closed wall polylines, enabling per-room polygon reconstruction.

**Bottom line:** from *this* DWFx we can crop and geometrically place apartments,
and describe one representative unit's rooms/layout — but a full per-apartment,
kitchen-aware dataset needs the מפרט מכר or the source RVT/DWG.

---

# Follow-ups (round 2)

## NEW unlock — the geometry is in real millimetres
The `<Path>` coordinate space is **1 unit ≈ 1 mm at 1:1**. Verified two ways:
the red safe-room box measures **2.9 × 3.4 m** (its label reads `12.3 m²`) and the
building footprint comes out **~23 m wide** — both realistic. So *anything we can
bound in the vector data converts to m² by /1000²*. Tool: `tools/extract_geometry.py`
(parses path Data by colour; colour legend documented in the tool header).

## #1 — Pin apartments by their spreadsheet sizes
A **typical floor of building 1 has 5 distinct apartments** (from the price
sheet), and the sizes are well separated, which makes size-matching viable:

| stack | area m² | tier | likely role on the plate |
|---|---|---|---|
| s1 | 109   | subsidised | large corner (3 bed + living) |
| s3 | 105.4 | subsidised | large corner |
| s2 | 89    | subsidised | medium |
| s5 | 79    | subsidised | smaller |
| s4 | 76    | subsidised | smallest |

(Floors 7–8 merge into free-market penthouses: 126/134, then 148/158; ground has a 185 m² unit.)

**Method that works:** each plate shows 4 corner units + 1 mid-facade unit around
the core. We place them by **corner→facing** (see `docs/ORIENTATION.md`,
page-up=N, right=E), then match the 5 known areas to the 5 cells by
**(a) measured footprint size** (geometry, now that scale=mm), **(b) room count
read from the plan**, and **(c) corner**. The sizes anchor it; orientation
disambiguates. **Residual uncertainty:** left↔right *within a side* (which of the
two south corners is 76 vs 79, etc.) — the same gap flagged in ORIENTATION.md.
A clean *automatic* per-cell area needs apartment-polygon tracing (the blue
boundary line is dashed, so it needs stitching) — feasible as a next step, but
the מפרט מכר's כיוונים table resolves it instantly and authoritatively.

## #2 — Can the DWFx be turned into RVT/DWG?
**No — not into a real (parametric/semantic) model.** Autodesk's own guidance:
DWF/DWFx are *digital plot* files holding only "low-intelligence entities," and
**AutoCAD / DWG TrueView / Design Review have no feature to convert DWF→DWG**.
The RVT/DWG you'd want never travels inside a DWF. What you *can* do:
- **Extract dumb 2D geometry** (lines/polylines/text — no layers, no rooms) via
  third-party converters: ODA File Converter (DWG/DXF only — won't read DWFx),
  **reaConverter "DWFx→DWG"**, or the **"DWF to DWG Converter"** Windows app.
  Result is tracing-quality geometry, not an editable building model.
- **For our analysis we don't need any of this** — we already parse the same
  geometry+text directly out of the DWFx (`tools/extract_geometry.py`).
- **To get a true model:** ask the architect/developer for the original
  **Revit `.rvt`** or layered **DWG**, or the **מפרט מכר** PDFs.

## #3 — Read kitchen / living / rooms from the drawing's "pictures" — YES
There are no room-name labels for most units and **no kitchen label anywhere**,
but the furniture/fixture **symbols are unambiguous** and I can read them from a
high-DPI render (legend cross-checked against the two plan-reading guides you
sent). Confirmed on the labelled NW unit (`docs/img/`):

| Symbol on plan | Room |
|---|---|
| sofa + dining table (rectangle w/ chairs) | living/dining `מגורים` |
| **counter run + double-circle sink** (red cabinetry) | **kitchen** (open-plan, against the **east** wall of the living) |
| bed rectangle | bedroom / master `הורים` |
| red-walled square | safe room `ממ"ד` |
| bathtub + WC + basin | bathroom `רחצה` |
| small room, WC only | service WC `שירות` |
| railed/hatched corner | balcony `מרפסת` |

So for **every** apartment (not just the labelled one) we can render its cell and
produce a room-by-room read **including the kitchen's position** — e.g. for the
NW unit: *living centre, kitchen on its east side, master + 2nd bedroom to the
west/north, safe room + bath/WC to the south, balconies at the N/NW corner.*
This is best-effort visual interpretation (high confidence for kitchen/bed/bath;
the exact kitchen extent is approximate), not a labelled dataset.

### Recommended next step
If you want the full per-apartment dataset (all 5 cells × all buildings: rooms,
kitchen position, area, facing, cropped plan), the fastest accurate path is the
**מפרט מכר**. Failing that, I can (a) build the blue-boundary polygon tracer for
automatic per-cell areas, and (b) do the per-cell visual room read for each
apartment of a typical floor and wire the crops + reads into the app.
