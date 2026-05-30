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
