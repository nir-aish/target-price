# Orientation analysis (sun / facing) — for resale value

Orientation strongly affects resale value (sun = premium). Here's what we can and
cannot extract from the DWFx.

## North direction — ROBUST ✅

Every floor sheet carries a north arrow (`N`, 10 of them). Parsing the XPS Canvas
transforms gives a **consistent rotation of −26.2°** on all of them, and a render of
the arrow confirms it points **up-and-to-the-left**. Therefore:

- **True north ≈ 26° west of "page up".**
- Cardinal mapping on the plans (bearing of each page direction):

| Page direction | Compass bearing | ≈ |
|---|---|---|
| up      | 26°  | NNE |
| right   | 116° | ESE |
| down    | 206° | SSW |
| left    | 296° | WNW |

## Building structure — ROBUST ✅

Each floor sheet shows **all 3 buildings** (`בנין 1/2/3`). Each building is a roughly
**square footprint with 4 apartments — one per corner — around a central stair/lift
core**, and each apartment's **balcony sits at the building's outer corner**.

Quadrant → facing (sun premium in **bold**):

| Corner on plan | Faces | Resale |
|---|---|---|
| bottom-right | **SE → S** | **best (sun + likely view)** |
| bottom-left  | **SW**     | **good (afternoon sun)** |
| top-right    | NE → E     | ok (morning sun) |
| top-left     | N → NW     | weakest (least sun) |

## What we CANNOT reliably extract ⚠️

- **Per-apartment facing for all 84 units.** Detailed room labels exist on only a few
  representative apartments (≈11 living-room labels on the whole sheet), and the
  per-unit **apartment numbers on the building plans are below OCR resolution** at any
  render we can produce. So we cannot auto-map each price-list apartment (building +
  floor + stack 1–5) to a specific corner/facing from the CAD alone.
- Note: the price list has up to **5 stacks** per building but the plan shows **4
  corners**, so at least one unit is a non-corner (mid-facade) — mapping is not 1:1.

## How to complete orientation (recommended)

1. **Sales brochure / מפרט מכר** — for מחיר למשתכן these almost always state each
   apartment's **כיוונים (facing directions)** explicitly. Fastest, authoritative.
2. **Guided mapping** — read each building's 4–5 apartment numbers off the plan
   together (we zoom in, you confirm the digits), then attach the quadrant facing.

Until then, orientation is **not** injected into the ranking (no per-apartment data),
to avoid fabricated precision. The north constant and quadrant logic are ready to wire
in as soon as the stack→corner mapping exists.
