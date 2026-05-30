# Resale-profit ranking model

Purpose: the apartments are bought to **resell for profit**. This model ranks the
**84 subsidized (מחיר למשתכן) apartments** by estimated resale profit.

```
profit = estimated_market_value − purchase_price
estimated_market_value = market_₪/m²(area, floor) × area
resale_score = profit_% × liquidity      (rewards quick-selling, in-demand sizes)
```

## Purchase-cost model (official price, overrides the spreadsheet)

The spreadsheet reverse-engineers **exactly** to `(15,022 × area − 133,230) × 1.17`
— i.e. the buyer's stated base of **15,022 ₪/m²** at **17% VAT**. We recompute cost
from the official base with current terms:

```
gross   = (15,022 × area − 133,230) × INDEXATION × (1 + VAT)
discount = min(20% × gross, 300,000 ₪)          # מחיר מטרה benefit
purchase_price = gross − discount
```

- **VAT = 18%** (current, since 1 Jan 2025).
- **INDEXATION = 1.06** — an *estimate* of מדד תשומות הבנייה from the tender base to
  the assumed first-payment date **1 Jul 2026** (project has no היתר בנייה yet).
  ⚠️ Needs the tender **base-index date** to firm up. Sensitivity: profit% moves
  ~±15 pts across ×1.00–1.12 but the **ranking order is unchanged**.
- **Discount** modelled as 20% capped at 300k (whichever is smaller) — confirm this
  interpretation. Effect: units with gross < 1.5M get the full 20%; larger units are
  capped at 300k (a smaller %), which favours smaller units on profit%.
- `133,230` constant: reproduces the sheet exactly; its official meaning is
  unconfirmed (treated as a fixed deduction).

Output fields per apartment: `gross_price`, `target_discount`, `purchase_price`,
plus `sheet_price_ref` (original spreadsheet figure) for comparison.

Tools: `tools/rank.py` → `data/parsed/ranking.json` + `ranking.csv`.

## Why we can estimate market value well here

This project **sells free-market units in the same buildings**, giving a clean,
local market anchor (no guessing from other projects):

| Floor | Free-market ₪/m² (observed) |
|------|------|
| 5–6 | ~26,200–26,300 |
| 7 | ~29,300 |
| 8 | ~30,200 |

Subsidized units are fixed at **15,525–16,982 ₪/m²** regardless of floor — so the
built-in equity is large, and what differentiates profit between units is **floor,
size/liquidity, and entry ₪/m²**.

## Assumptions (explicit, tunable in `tools/rank.py`)

- `MARKET_BASE_PPM = 27,000 ₪/m²` (mid-floor, standard size), calibrated to the
  free-market table above.
- **Floor premium** `FLOOR_FACTOR`: ground 0.92 → floor 8 1.10 (≈+2–3%/floor, top
  floors strongest; ground floor penalised) — consistent with the observed curve.
- **Size factor**: <90 m² ×1.05, 90–115 ×1.00, >115 ×0.97 (smaller flats fetch a
  higher ₪/m²).
- **Liquidity**: 76–95 m² (3–4 rooms) = 1.00 (most in-demand), 95–112 = 0.95,
  larger = 0.88 — reflects how fast/easily a unit resells.

## Important caveats — read before acting

1. **מחיר למשתכן resale lock-in.** The program restricts selling at market for a
   holding period (commonly several years from occupancy). Profit is realised
   **after** the lock-in — confirm the exact terms in your contract / with the
   sales office. This affects *timing*, not the relative ranking.
2. These are **estimates**, not appraisals. Market prices move; finishing level,
   exact view, and demand at sale time all matter.
3. **Orientation / sun / view not yet included.** Available from the drawings
   (north arrow) and will refine rankings (south/open-view = premium, north-only =
   discount). Next enhancement.
4. **Floor numbering** (price list ground→8 vs drawings 1→9) still to confirm with
   the sales office; affects the floor premium for edge floors.
5. Absolute ₪ profit favours larger/higher units; `resale_score` favours % return ×
   liquidity. Both columns are in the output — choose per your strategy.
