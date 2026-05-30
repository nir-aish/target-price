# Resale-profit ranking model

Purpose: the apartments are bought to **resell for profit**. This model ranks the
**84 subsidized (מחיר למשתכן) apartments** by estimated resale profit.

```
profit = estimated_market_value − purchase_price
estimated_market_value = market_₪/m²(area, floor) × area
resale_score = profit_% × liquidity      (rewards quick-selling, in-demand sizes)
```

## Purchase-cost model (official מחיר מטרה contract price)

The price list **is** the contractual מחיר מטרה price. It reverse-engineers **exactly**
to `(15,022 × area − 133,230) × 1.17` — base **15,022 ₪/m²**, a fixed **133,230 ₪**
benefit (the *embedded* מחיר מטרה discount), at the then-current **17% VAT** and the
tender base index. We update it to current terms:

```
full     = 15,022 × area × INDEXATION × (1 + VAT)      # before the מטרה benefit
benefit  = 133,230 × INDEXATION × (1 + VAT)            # embedded discount (the −133,230 term)
purchase_price = full − benefit
               = (15,022 × area − 133,230) × INDEXATION × (1 + VAT)
```

- **VAT = 18%** (current, since 1 Jan 2025; the list was at 17%).
- **⚠️ Correction vs. earlier model.** The discount is **already inside the price list**
  (the −133,230 term). The previous model subtracted a *further* `min(20%, 300k)` cut on
  top — a **double-count** that understated cost by ~300k/unit and inflated profit% (top
  unit fell from ~124% → ~79% after the fix). There is now a **single** discount: the
  embedded benefit.
- **Validated discount terms (web).** מחיר מטרה / דירה בהנחה is marketed as **14–19% off
  the appraisal (שומה), capped at 300,000 ₪ below market**. Our embedded benefit
  (133,230 × VAT × idx ≈ **₪163k**, i.e. **~8–12%** of the base full-price, well under the
  300k cap) is *smaller* than the headline 14–19%. Two reconcilable reasons: the 14–19%
  is measured off the **appraisal** (higher than the base-formula "full" price), and the
  `133,230` constant's exact official meaning is still unconfirmed. **Net for us: the cap
  never binds at these unit sizes; verify the constant against the contract.**
- **INDEXATION = 1.06** — bounded estimate of מדד תשומות הבנייה, tender base → payment.
  Validated mechanism (replaces the old "≈Jul-2026" hand-wave):
  - The index rises ~5%/yr (**2023 +2.0%, 2024 +2.9%, 2025 +5.1%**, 2026 forecast +5–7%).
  - **Amendment 9 to חוק המכר (in force Jul 2022)** caps the index-linked portion at **40%
    of the price** — so even a +10–12% raw index becomes ~+4–5% effective.
  - A **בג"ץ compromise** splits the law-change differential in thirds (state/contractor/
    buyer); the buyer's add-on is estimated at only **₪4,043–8,206**.
  - Indexation accrues only from the **later of contract-signing / full היתר בנייה** — and
    this project has **no היתר yet**, so little has accrued to date.
  - ⇒ Effective ≈ **×1.04–1.10**; we keep **1.06** as the central estimate. Profit% moves
    ~±10 pts across ×1.00–1.12 but the **ranking order is invariant**.

Output fields per apartment: `gross_price` (full pre-benefit), `target_discount` (embedded
benefit), `purchase_price`, plus `sheet_price_ref` (original price-list figure), `facing`
and `exposure_factor` (see exposure model below).

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

**Cross-check vs. external Petah-Tikva comps (2025, validated on the web):**

| Source | ₪/m² | Note |
|---|---|---|
| PT citywide average (2025) | **~29,064** | +6% YoY |
| PT 4-room, second-hand | ~23,558 | older stock |
| PT 5-room, second-hand | ~24,769 | older stock |
| New-build premium | new 3-rm ₪2.53M vs 2nd-hand ₪2.18M | new commands ~15–20% more |
| In-project free-market (primary anchor) | 26,200–30,200 | same buildings |

Our `MARKET_BASE_PPM = 27,000` sits **between** PT second-hand (~23.5k) and the citywide/
new-build level (~29k), and just below the in-project free-market anchor. For a brand-new,
premium **eastern** quarter (Sirkin), this is a **central-to-mildly-conservative** anchor —
i.e. it likely understates rather than overstates resale value, leaving upside. **No change
to the 27k anchor**; the in-project free-market units remain the cleanest comp.

## Assumptions (explicit, tunable in `tools/rank.py`)

- `MARKET_BASE_PPM = 27,000 ₪/m²` (mid-floor, standard size), calibrated to the
  free-market table above.
- **Floor premium** `FLOOR_FACTOR`: ground 0.92 → floor 8 1.10 (≈+2–3%/floor, top
  floors strongest; ground floor penalised) — consistent with the observed curve.
- **Size factor**: <90 m² ×1.05, 90–115 ×1.00, >115 ×0.97 (smaller flats fetch a
  higher ₪/m²).
- **Liquidity**: 76–95 m² (3–4 rooms) = 1.00 (most in-demand), 95–112 = 0.95,
  larger = 0.88 — reflects how fast/easily a unit resells.
- **Exposure** `exposure_score(facing)`: SE 1.10 / E 1.08 / NE 1.06 (toward the eastern
  green/park) … SW 0.96 / W 0.94 / NW 0.92 / N 0.93 (face neighbouring buildings). **Now
  wired into `market_ppm`**, gated on a per-unit `STACK_FACING` map. That map is **empty**
  (neutral ×1.0 for all 84 units) until the brochure/מפרט מכר supplies each unit's כיוונים
  — so exposure does not yet move the ranking, but activates with one edit. See
  `docs/SURROUNDINGS.md` / `docs/ORIENTATION.md`.

## Important caveats — read before acting

1. **Resale lock-in — VALIDATED (firm rule).** דירה בהנחה / מחיר מטרה bars selling at
   market until the **earlier** of:
   - **5 years from טופס 4** (occupancy certificate), or
   - **7 years from the tender-win date**.

   This project's tender was won in **early 2023**, so **7y-from-win ≈ early 2030** is the
   binding date (occupancy is later, ~2028–2029, +5y ≈ 2033+). ⇒ **The market-resale window
   opens ~2030.** Before then you may only sell to another eligible buyer, with משרד הבינוי
   approval; breaching the terms carries a penalty of **~₪450,000 (index-linked)**. Profit
   is realised **after** this date — it affects *timing*, not the relative ranking. *(Confirm
   the exact win-date and terms in your contract.)*
2. These are **estimates**, not appraisals. Market prices move; finishing level,
   exact view, and demand at sale time all matter. (By the ~2030 window, ~5 more years of
   PT appreciation at ~6%/yr is plausible upside not modelled here.)
3. **Orientation / sun / view** is now *wired* but **neutral** — needs the per-unit
   כיוונים from the brochure/מפרט to activate (east/green = premium). See exposure note above.
4. **Floor numbering** (price list ground→8 vs drawings/marketing "9 קומות"; official dira
   = 8 floors) still to confirm with the sales office; affects the floor premium for edge floors.
5. Absolute ₪ profit favours larger/higher units; `resale_score` favours % return ×
   liquidity. Both columns are in the output — choose per your strategy.
