# Area-measurement review — are we reading the plans correctly?

The buyer asked us to verify our parsing follows Israeli apartment-measurement
conventions. NOTE: the two reference documents provided could not be opened from
this environment (outbound web is firewalled). This review is therefore based on
the standard rules (תקנות התכנון והבנייה — חישוב שטחים) and on what is actually
printed in the DWFx. **Re-verify against the source docs** — easiest path: upload
the PDF into the repo (`docs/refs/`) and we'll check against it directly.

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
