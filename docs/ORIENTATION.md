# Orientation analysis (sun / facing) — for resale value

Orientation strongly affects resale value (sun = premium). Here's what we can and
cannot extract from the DWFx.

## Rendered-plan review — north & green direction visually CONFIRMED ✅

Rendered the plans (`tools/render.py`, sheet 2) and read them directly. Confirms:
- The building footprints are **square with 4 corner apartments + 1 mid-facade unit per
  floor** around a central stair/lift core (matches the price list's **5 stacks** vs the
  **4 corners** — the 5th is the mid-facade unit, seen as the middle of the 3 smaller units
  along the south/bottom facade).
- The **detailed site/landscape plan** shows **green/gardens wrapping the north (top) and
  east (right) edges** — consistent with the eastern park (מגרש 110) lying to **page-right**.
- With **north ≈ 26° up-and-left**, **page-right ≈ east** ⇒ **the right-hand apartments of
  each plate face the eastern green (premium); the left-hand apartments face the neighbours.**

**Now in the app:** each apartment's detail panel shows its **building floor-plate PNG**
(`app/plans/building{1,2,3}.png`) + the site plan, with an orientation legend, so units are
**reviewable visually**. Per-building plate is the right granularity — typical floors repeat,
so every unit in a stack shares the layout.

**Still pending for per-unit facing in the *score*:** the exact **stack → corner** link. The
plate's apartment-number tags (101/102/105/108 — only 4, in circles) don't key to price-list
stacks 1–5, and which of the 5 stacks is the mid-facade unit can't be read unambiguously from
the CAD. So `STACK_FACING` stays empty (exposure neutral) until the מפרט מכר כיוונים table —
or a quick guided confirmation off these now-embedded plate images — resolves it.

## North direction — ROBUST ✅ (independently validated)

Every floor sheet carries a north arrow (`N`, 10 of them). Parsing the XPS Canvas
transforms gives a **consistent rotation of −26.2°** on all of them, and a render of
the arrow confirms it points **up-and-to-the-left**. Therefore:

- **True north ≈ 26° west of "page up".**

**Independent cross-check:** the project's marketing 3D renders are captioned
**"מבט מכוון צפון מזרח" (view facing NE)** and **"מבט מכוון דרום מזרח" (view facing SE)**.
A building whose showcase facades are NE and SE matches the −26.2° derivation exactly
(a square rotated ~26°, with facades toward NE/SE/SW/NW). Two independent sources agree.

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

Each corner apartment has **two exterior facades** (good cross-ventilation — "דירת
2 כיוונים", valued in Israel). Corner → overall facing (sun premium in **bold**):

| Corner on plan | Two facades | Overall | Resale |
|---|---|---|---|
| bottom-right | ESE + SSW | **SSE ≈ South** | **best (sun + showcase SE facade)** |
| bottom-left  | SSW + WNW | **WSW**         | **good (afternoon sun)** |
| top-right    | NNE + ESE | ENE             | ok (morning sun; showcase NE facade) |
| top-left     | WNW + NNE | NNW             | weakest (least sun) |

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

**Wiring status (updated):** `exposure_score(facing)` is now **wired into `market_ppm()`**
in `tools/rank.py` and combines the sun + open-view (eastern green/park) logic. It reads a
`STACK_FACING` map keyed by `(building, stack)`. That map is **deliberately empty** → every
unit gets a **neutral ×1.0**, so no fabricated precision enters the ranking. The moment the
per-apartment כיוונים are known (brochure/מפרט or a guided plan-read — the dira מפרט is not
publicly retrievable; see `docs/SURROUNDINGS.md`), populating `STACK_FACING` activates the
premium/discount for the green-facing (NE/SE) vs building-facing (SW/NW) corners automatically.
