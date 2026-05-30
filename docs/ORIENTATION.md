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

### ORIENTATION from the floor-plan NORTH ARROW (read by the arrow's point)

The per-plate legend box ("תוכנית קומה N · קנ"מ 1:100") carries a **north arrow**. Read by where
the **needle POINTS** (the long fine tip — *not* the "N" letter at the opposite, solid end): it
points **UP-and-to-the-LEFT** (~27° west of page-up). So **page-up ≈ North**.

> ⚠️ Note: an intermediate pass mistakenly used the letter "N" (at the solid tail) and flipped
> this 180°. Corrected back per the arrow's point and the site-plan check below.

| Page direction | Bearing | Cardinal |
|---|---|---|
| up    | ~27°  | **North** (מגרש 104) |
| right | ~117° | **East** (the green/park, מגרש 110) |
| down  | ~207° | **South** (מגרש 200) |
| left  | ~297° | **West** (school 101) |

**Cross-check:** the detailed site/landscape plan shows the **green/open space on the right
(east)** side, matching page-right = East. The marketing's showcase NE & SE facades are the
**east-facing (page-right)** corners onto the green.

### Inferred facing — APPLIED to the score (best-effort, review-flagged)

Corner → facing: **bottom-right = SE (best: south sun + east green)**, top-right = NE,
bottom-left = SW, **top-left = NW (weakest)**, bottom-middle = S. Stack → position (best-effort
from plates): the two largest stacks take the top (north) corners; the smaller stacks the
bottom (south), with the middle one as the mid-facade (S).

Resulting map (building, stack → facing):

| Bld | s1 | s2 | s3 | s4 | s5 |
|----|----|----|----|----|----|
| 1 | NE | S | NW | SW | **SE** |
| 2 | NW | NE | S | SW | **SE** |
| 3 | NE | NW | S | SW | **SE** |

**Confidence & soft spots (flagged ⚠ in the app):** the **orientation/corner framework is
high-confidence** (arrow + green-on-right agree); the genuinely uncertain part is **left↔right
within a side** — NE↔NW between the two top units and SE↔SW between the bottom corners — which
flips a unit between best (~1.10) and weak (~0.92). The exact **stack→corner** still wants the
**מפרט מכר כיוונים** to confirm. Each unit's app panel shows its plate for review.

## Building structure — ROBUST ✅

Each floor sheet shows **all 3 buildings** (`בנין 1/2/3`). Each building is a roughly
**square footprint with 4 corner apartments + 1 mid-facade unit (= the 5 price-list stacks)**
around a central stair/lift core; each corner apartment's **balcony sits at the outer corner**
(two exterior facades — "דירת 2 כיוונים", valued in Israel). Corner → overall facing
(page-up = North, page-right = East/green):

| Corner on plan | Faces | Overall | Resale |
|---|---|---|---|
| **bottom-right** | South + East | **SE** | **best (south sun + east green)** |
| top-right        | North + East | **NE** | good (open east/green; morning sun) |
| bottom-left      | South + West | **SW** | ok (south sun; faces school 101) |
| top-left         | North + West | **NW** | weakest (no sun; faces neighbours) |
| bottom-middle    | South        | **S**  | south sun (faces מגרש 200) |

## Per-apartment facing — now inferred (best-effort), with one residual unknown ⚠️

The corner→facing map above is solid. The remaining gap is **which price-list stack (1–5) sits
at which corner** — specifically **left↔right within a side**. The plate's apartment-number tags
(101/102/105/108) don't key to stacks 1–5, and the 5th (mid-facade) stack can't be pinned from
the CAD. Best-effort positions are inferred (largest stacks → top/south corners; smaller →
bottom/north) and applied to the score, flagged ⚠ in the app — but **verify the exact
stack→corner against the מפרט מכר כיוונים** before treating individual picks as final.

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
