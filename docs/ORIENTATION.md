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

### ⚠️ ORIENTATION CORRECTED via the floor-plan NORTH ARROW (was flipped 180°)

The per-plate legend box ("תוכנית קומה N · קנ"מ 1:100") carries a **north arrow**. Read at max
zoom, its **solid needle + "N" label point DOWN-and-to-the-RIGHT** (~27° right of straight
down). So the earlier "north ≈ 26° up-left" reading was **inverted**. Corrected mapping:

| Page direction | Bearing | Cardinal |
|---|---|---|
| up    | ~207° | **South** |
| left  | ~117° | **East** (the green/park, מגרש 110) |
| right | ~297° | **West** (school 101) |
| down  | ~27°  | **North** (מגרש 104) |

**Three independent cross-checks all agree** (and contradict the old reading):
- **Sun balconies/terraces** (loungers) are drawn on the **TOP** of every plate → south-facing
  (N-hemisphere) → **top = south**.
- The **green tree** beside building 1's **top-left** unit sits on the **LEFT** → **east/green
  = page-left**.
- The marketing's showcase **"מבט צפון-מזרח" / "דרום-מזרח"** facades are the two **LEFT (east)**
  corners — the side onto the green.

### Inferred facing — APPLIED to the score (best-effort, review-flagged)

Corner → facing (corrected): **top-left = SE (best: south sun + east green)**, top-right = SW,
**bottom-left = NE**, bottom-right = NW (worst), bottom-middle = N. Stack → position
(best-effort from plates): the two largest stacks take the top (south) corners; the smaller
stacks the bottom (north), with the middle one as the mid-facade.

Resulting map (building, stack → facing):

| Bld | s1 | s2 | s3 | s4 | s5 |
|----|----|----|----|----|----|
| 1 | SW | N | **SE** | NE | NW |
| 2 | **SE** | SW | N | NE | NW |
| 3 | SW | **SE** | N | NW | NE |

**Confidence & soft spots (flagged ⚠ in the app):** the **orientation/corner framework is now
high-confidence**; the genuinely uncertain part is **left↔right within a side** — SE↔SW between
the two top (south) units and NE↔NW between the bottom corners — which flips a unit between best
(~1.10) and worst (~0.92). The exact **stack→corner** still wants the **מפרט מכר כיוונים** to
confirm. Each unit's app panel shows its plate + the inferred direction for review.

## North direction — corrected (read off the plan's own north arrow)

> ⚠️ **Supersedes an earlier error.** A first pass parsed the XPS arrow-glyph transform as
> −26.2° and called it "up-and-to-the-left" (north). Reading the **actual rendered north
> arrow** (the legend box on each plate, "N" at the solid tip) shows it points **DOWN-and-to-
> the-RIGHT** — i.e. the previous reading was **inverted 180°**. The marketing "NE/SE" cross-
> check is still satisfied (those facades exist), but they're the **left (east)** corners, not
> the right. The three checks in the section above (north arrow, south-facing sun terraces on
> top, east-green tree on the left) are mutually consistent and authoritative.

Corrected cardinal mapping (bearing of each page direction):

| Page direction | Compass bearing | ≈ |
|---|---|---|
| up      | ~207° | **South** |
| right   | ~297° | **West** |
| down    | ~27°  | **North** |
| left    | ~117° | **East** |

## Building structure — ROBUST ✅

Each floor sheet shows **all 3 buildings** (`בנין 1/2/3`). Each building is a roughly
**square footprint with 4 corner apartments + 1 mid-facade unit (= the 5 price-list stacks)**
around a central stair/lift core; each corner apartment's **balcony sits at the outer corner**
(two exterior facades — "דירת 2 כיוונים", valued in Israel). Corner → overall facing:

| Corner on plan | Faces | Overall | Resale |
|---|---|---|---|
| **top-left**  | South + East | **SE** | **best (south sun + east green)** |
| bottom-left   | North + East | **NE** | good (open east/green; morning sun) |
| top-right     | South + West | **SW** | ok (south sun; faces school 101) |
| bottom-right  | North + West | **NW** | weakest (no sun; faces neighbours) |
| bottom-middle | North        | **N**  | weak (faces מגרש 104) |

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
