# Data validation — price list vs. drawings

> **Update (revised price list).** The price list was re-uploaded with corrected
> values. The parser (hardened against summary rows) now yields **105 apartments —
> 84 subsidized + 21 free-market**, and matches the file's own `יח"ד מטרה`/`שוק חופשי`
> counts **exactly for all three buildings** (B1 32+5, B2 24+8, B3 28+8). The earlier
> Building-3 count discrepancy is **resolved**. The floor-numbering item below still
> stands.


Comparing the two parsed sources for the Sirkin (סירקין) מחיר למשתכן project:

- **Price list:** `data/pricelists/apartment-sizes-and-prices.xlsx` → `data/parsed/apartments.json`
- **Drawings:** `data/plans/may-11-25-plans.dwfx` → `data/parsed/plans.json`

Goal (per the buyer): apartments are an **investment to resell for maximum profit**,
so the data that matters most is the one driving resale value — floor, orientation,
area/layout, balcony, and entry price relative to market.

## Verdict at a glance

| Check | Result |
|---|---|
| Number of buildings | ✅ Match — 3 buildings in both sources |
| Apartment counts | ✅ Price list internally consistent for B1/B2; ⚠️ B3 off by ~4 |
| Subsidized vs free-market split | ✅ Clear two-tier pricing, matches the file's own totals |
| Price sanity (₪/m²) | ✅ Subsidized ~15.5–16.1k; free-market ~26–31k |
| Floor coverage | ⚠️ Different labeling/range — needs reconciliation |
| Per-apartment areas | 🟡 Ballpark-confirmed (one clean 76.8≈76 m² match); full check needs segmentation |

## What validated cleanly

- **3 buildings** in both the price grid (3 blocks) and the drawings (`בנין 1/2/3`).
- **Tiering:** 91 apartments → **70 subsidized** (מחיר למשתכן, the eligible set) + **21
  free-market**. Subsidized price/m² is tightly clustered at **15,525–16,146 ₪/m²**,
  free-market at **26,425–31,482 ₪/m²**. The spreadsheet's own
  `שטח מטרה`/`שטח שוק חופשי` and `עד 80 / עד 110 / גדולות` category totals confirm the
  split (B1: 12+15 subsidized, B2: 8+12 subsidized — both match the parsed counts).
- **Subsidized apartment types** (licensed m²): 76, 79, 89, 105.4, 109, 109.5, 110.5.
- **Area↔drawing sanity:** room areas read from the drawings land on the right scale;
  the cleanest floor plan sums to **76.8 m² (excl. balcony) ≈ the 76 m² price-list type**,
  with a separate ~8.2 m² balcony — consistent with how licensed area excludes balconies.

## Discrepancies to resolve (possible staleness)

1. **Floor labeling / range.** Price list covers `קרקע`(ground)+floors 1–8 = 9 residential
   levels. Drawings show floor titles **-2, -1, 1, 2–3, 4, 5, 6, 7, 8, 9, roof**. The
   basements (-1,-2) are parking/technical (the drawings show `מתקנים כפולים` car
   stackers there), and the roof is non-residential, so the **9 sellable levels likely
   reconcile** (ground+1..8 ≙ floors 1..9). But the numbering differs — worth confirming
   which scheme the sales office uses, so floor-height scoring is correct.
2. **Building 3 count.** The price grid yields 23 subsidized units for B3, but B3's own
   category totals (`עד 80`=12, `עד 110`=7) imply 19. A 4-unit gap inside the file itself —
   the list may be a slightly older/edited cut.
3. **Room-level pairing is noisy.** Each floor plan drawing contains ~4 apartments, so the
   current "nearest number" room→area pairing crosses apartment boundaries (e.g. a
   recurring `43.4` value attaches to multiple units). Per-apartment **spatial
   segmentation** is needed before per-room areas can be trusted unit-by-unit.

## Recommendation / next step

The price list is **trustworthy for building / floor / area / price / tier** — enough to
build the resale-profit ranking on. Before relying on per-room detail and orientation:

1. **Confirm with the sales office:** is this the current price list, and which floor
   numbering is official? (Resolves discrepancies #1 and #2.)
2. **Build per-apartment segmentation** of the drawings (cluster each floor plan into its
   individual units) to attach room areas + **orientation** + a plan image to each of the
   70 subsidized apartments, and to fully validate areas against the list.
3. Spot-check 2–3 apartments visually against the rendered plans.
