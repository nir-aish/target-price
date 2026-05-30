# Area-measurement review — are we reading the plans correctly?

The buyer asked us to verify our parsing follows Israeli plan-reading conventions.
The two reference documents were provided and **have now been read in full**:
- "איך קוראים תוכניות בנייה" (building.org.il) — general plan-reading guide.
- "קריאה והבנת תכניות בנייה" (מצגת 109) — 67-slide course deck.

Verified against them (all ✅ consistent with our parsing): scale **1:100** (1 cm = 1 m),
dimensions in **centimeters**, **internal vs external** dimension chains, **north arrow**
near the legend (→ orientation derivable), **floor-level marks** relative to ground `±0.00`.
Neither document defines שטח עיקרי/שירות — that comes from the area-calc regulation
(תקנות חישוב שטחים), so that section below rests on the regulation, not these decks.

**Bug found via the cm-dimension rule:** apartment-number detection (`^1\d{2}$`) collides
with cm wall dimensions like 142/160/180/190. Fix: classify text by font size
(`em≈13` = area label; `em≈4–5` = dimension / apartment number).

## How these plans encode areas (confirmed from the file)

- Room name and its **net area in m²** are printed together at font size `em≈13`
  (e.g. `מגורים 43.4`, `הורים 12.3`, `ממ"ד 12.3`, `רחצה 5.1`, `מרפסת 8.2`).
- `מגורים` is the **open public space** (living + dining + kitchen as one figure) —
  hence its large value (~43 m²).
- Small text (`em≈4–5`) is **not** areas: `250`, `300` = wall **dimensions in cm**;
  `101/102/108` = **apartment numbers**.
- There is **no embedded area schedule** (`טבלת שטחים`, `עיקרי`/`שירות`/`רישוי`) in the
  drawings; the only authoritative totals are in the price list (`שטח רישוי`).

## Standard rules and our compliance

| Rule (תקנות חישוב שטחים) | Status |
|---|---|
| Room label = net internal area in m² | ✅ read correctly |
| מרפסת (open balcony, ≤12 m²) measured separately, not in עיקרי/שירות | ✅ kept separate |
| Separate cm dimensions / apartment numbers from areas | ✅ (improve: key off font size `em`) |
| Split apartment into **שטח עיקרי** (living, bedrooms, kitchen) vs **שטח שירות** (ממ"ד, bath, WC, storage, circulation) | ❌ not yet done |
| `שטח רישוי` measured to wall center-lines/outer faces incl. walls → net room-sum is ~10–15% lower | ❌ not accounted for (don't equate room-sum to רישוי) |
| Per-apartment totals require segmenting each floor plan into its own unit boundary | ❌ pending (rooms currently pooled per floor plan) |

## Required fixes before trusting per-apartment areas

1. Tag each room as **עיקרי** or **שירות**; report `עיקרי`, `שירות`, `מרפסת`
   separately per apartment.
2. Segment each floor plan into individual apartments (spatial clustering) and sum
   within each unit boundary.
3. Compare net room-sum to the price-list `רישוי` *with* a wall/gross-up allowance,
   not as an exact equality.
4. Use font size (`em`) to classify text: area label (~13) vs dimension/number (~4–5).

## Room → category mapping (residential)

- **עיקרי:** מגורים (living/kitchen/dining), הורים (master), חדר (bedroom)
- **שירות:** ממ"ד, רחצה (bath), שירותים (WC), מבואה (entry), ארונות (closets), מחסן
- **Separate:** מרפסת (balcony), מחסן/חניה when sold as attached units (צמודים)
