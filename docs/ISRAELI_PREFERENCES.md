# Israeli home-buyer preferences — resale-value drivers

Basis for the pros/cons and weighting in `tools/rank.py`. Since the goal is **resale
for profit**, these are the attributes that drive demand and price in the Israeli
second-hand market (Gush Dan / center, where Sirkin/Petah-Tikva sits).

> Note: compiled from market knowledge (external web access is blocked in this
> environment). Treat as a sensible default to refine with a local agent's input.

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
| Cross-ventilation (corner) | ⏳ framework ready | drawings (4 corners/bldg) |
| Sun orientation (S/SE) | ⏳ framework ready (`docs/ORIENTATION.md`) | north arrow + renders |
| Parking / storage / view | ❌ no per-unit data | needs brochure / מפרט |

⏳ = logic exists, waiting on the per-apartment stack→corner mapping (brochure or a
guided pass) before injecting into the score, to avoid fabricated precision.
