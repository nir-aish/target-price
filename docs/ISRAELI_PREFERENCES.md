# Israeli home-buyer preferences — resale-value drivers

Basis for the pros/cons and weighting in `tools/rank.py`. Since the goal is **resale
for profit**, these are the attributes that drive demand and price in the Israeli
second-hand market (Gush Dan / center, where Sirkin/Petah-Tikva sits).

> Note: compiled from market knowledge and **validated against current web sources
> (May 2026)** — the ranking drivers below (cross-ventilation, sun/open-view, 3–4-room
> liquidity, floor, parking/storage) are all corroborated by current Israeli market
> commentary and Petah-Tikva pricing data. Still worth a final sanity-check with a local agent.

## Validated against Petah-Tikva data (2025)

- **Price level / appreciation:** PT citywide average **~29,064 ₪/m²**, **+6% YoY** — a
  rising market, supporting resale upside by the ~2030 sale window (see `RANKING_MODEL.md`).
- **New-build premium is real:** a new 3-room flat (~₪2.53M) vs second-hand (~₪2.18M) ≈
  **+15–20%** — our subsidized units resell as nearly-new stock, so they sit at the upper
  half of the local range.
- **Room mix:** by-room ₪/m² (2nd-hand) is 4-rm ~23.6k / 5-rm ~24.8k / 6+ ~23.2k — larger
  units do **not** command a higher ₪/m², consistent with our liquidity penalty on big flats.

## What Israeli buyers pay a premium for (high → low impact)

1. **כיווני אוויר (cross-ventilation / exposures).** Apartments open to **2+ directions**
   (corner units) are strongly preferred for light and airflow. A single-direction
   ("דירת כיוון אחד") unit is a known negative. → *All corner units here qualify.*
2. **כיוון השמש (sun orientation).** **South / South-East = premium** (sun, warmth,
   light). East = morning sun (good). West = afternoon heat (mixed). **North = least
   desirable.**
3. **מרפסת שמש (sun balcony).** Near-essential in new builds; adds clear value. → present.
4. **קומה (floor).** Mid-to-high preferred (light, air, quiet, view) **with elevator**.
   **Ground floor** in a tower = weakest (privacy/noise/light) unless a private garden.
   Top floor = mixed (view vs. heat/roof). Penthouses priced separately.
5. **מספר חדרים.** **3–4 rooms = the largest buyer pool** (young families, couples) →
   most liquid / fastest resale. 5+ rooms = smaller market, slower.
6. **חניה + מחסן.** Private/deeded **parking** is highly valued in the center; **storage**
   a plus. *(No per-unit data in our sources yet.)*
7. **נוף ופרטיות.** Open view (park/garden) beats facing a neighboring building; privacy
   matters. *(Per-unit data pending.)*
8. **רעש.** Quiet side (away from a main road) preferred.
9. **ממ"ד.** Expected/standard in new builds; doubles as a room. → present.
10. **מצב/חדש.** New construction + the מחיר למשתכן discount = built-in equity.

## How this maps to our data

| Preference | In ranking now | Source |
|---|---|---|
| 3–4 rooms most liquid | ✅ `liquidity` + pros | price-list area |
| Higher floor premium | ✅ `FLOOR_FACTOR` + pros | price-list floor |
| Low entry ₪/m² | ✅ pros | price list |
| Cross-ventilation (corner) | ✅ pros (all corner units) | drawings (4 corners/bldg) |
| Sun orientation (S/SE) + open-view | 🔌 **wired but neutral** (`exposure_score`) | north arrow + renders |
| Parking / storage / view | ❌ no per-unit data | needs brochure / מפרט |

🔌 = `exposure_score()` is wired into `market_ppm()` but reads an **empty** per-unit facing
map (neutral ×1.0), so it does not yet move scores — awaiting the brochure/מפרט כיוונים (the
dira מפרט is not publicly retrievable) or a guided plan-read. See `docs/SURROUNDINGS.md`.
