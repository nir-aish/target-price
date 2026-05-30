# Resale-profit ranking model

Purpose: the apartments are bought to **resell for profit**. This model ranks the
**84 subsidized (מחיר למשתכן) apartments** by estimated resale profit.

```
profit = estimated_market_value − purchase_price
estimated_market_value = market_₪/m²(area, floor) × area
resale_score = profit_% × liquidity      (rewards quick-selling, in-demand sizes)
```

## Purchase-cost model (דירה בהנחה / מחיר מטרה)

The buyer's price is built explicitly in three steps:

```
displayed (מחיר מוצג) = 15,022 × area × (1 + VAT) × INDEXATION   # incl VAT, indexed to payment
discount              = min(20% × displayed, ₪300,000)          # דירה בהנחה subsidy, lower of the two
purchase_price        = displayed − discount                    # what the buyer pays
```

- **Base rate = 15,022 ₪/m²** (pre-VAT) — the מחיר מטרה rate for this plot.
- **VAT = 18%** (current, since 1 Jan 2025).
- **Subsidy discount = the LOWER of 20% of the displayed (incl-VAT) price or ₪300,000.**
  The ₪300k cap binds from **~89 m² upward** (where 20% of displayed exceeds 300k); below
  that the full 20% applies. Net ₪/m² ≈ **15,000–16,100** (small→large).
- **⚠️ Change vs. earlier model.** Earlier versions reverse-engineered the price list to a
  fixed `(15,022 × area − 133,230) × VAT` form and treated the **−133,230** as the whole
  subsidy (~₪156k, flat). That is **dropped** here: the subsidy is the explicit **20% / 300k**
  rule, which is **larger and price-dependent**. Consequence: the model now diverges from the
  price-list figure by roughly the dropped −133,230 term (see reconciliation note below).
- **⚠️ Open reconciliation.** The price list ("מחיר מכירה כולל מע"מ") sits **below** our new
  *displayed* price by ≈ 133,230 × VAT × idx. So either the listed figure already embeds a
  reduction (and the true מחיר מוצג is our clean 15,022 × area), or the listed figure *is* the
  מחיר מוצג (and the −133,230 should stay). Resolve against the contract / מפרט מכר. The one
  ground-floor garden unit (sheet ₪1,290,604) is also priced from area only, understating its
  cost by ~₪148k.
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

Output fields per apartment: `gross_price` (displayed/מחיר מוצג), `target_discount` (the
20%/300k subsidy), `discount_capped` (is the ₪300k cap binding?), `purchase_price` (net),
plus `sheet_price_ref` (original price-list figure), `facing` and `exposure_factor`.

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
- **Exposure** `exposure_score(facing)` — **currently EXCLUDED from the score**
  (`INCLUDE_EXPOSURE = False`). The multipliers exist (SE 1.10 / E 1.08 / NE 1.06 toward the
  eastern green/park … SW 0.96 / W 0.94 / NW 0.92 / N 0.93 facing neighbours) and per-unit
  facing is still inferred and shown as **information only**, but it does **not** affect
  ranking. **Why excluded:** a sensitivity test shows facing is the *dominant* driver of the
  top order, and it is the *least certain* input — `STACK_FACING` is inferred from the plates
  (not the מפרט), and the left↔right call within a side (SE↔SW, NE↔NW) is genuinely ambiguous.
  Flipping just that ambiguity reshuffles the **entire top-10 (0/10 overlap)** and changes #1.
  We refuse to let an unverified guess decide the pick. **Re-activate** (set `INCLUDE_EXPOSURE
  = True`) once facings are confirmed against the מפרט מכר / brochure. See `docs/ORIENTATION.md`.

## Sensitivity / confidence (what the ranking actually rests on)

Stress-testing the top-10 against each uncertain assumption:

| Perturbation | Top-10 stability | Verdict |
|---|---|---|
| Indexation ×1.00 ↔ ×1.12 | **10/10 unchanged** | order invariant — safe |
| size_factor off | 8/10 | minor |
| liquidity off | 9/10 | minor |
| exposure on/off | 5/10, #1 changes | large — hence excluded |
| **flip inferred L↔R facing** | **0/10, #1 changes** | dominant **and** unverified → excluded |

⇒ With exposure excluded, the ranking depends only on **validated cost + floor + size +
liquidity**, all of which are stable. Confidence in the *order* is now high; confidence in
absolute ₪ depends on the market anchor (conservative) and the unmodelled ~2030 appreciation.

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
3. **Orientation / sun / view** is **deliberately excluded from the score** (unverified and
   dominant — see the exposure note and sensitivity table above). Facing is shown as
   information only. Activate once the per-unit כיוונים are confirmed from the brochure/מפרט.
4. **Floor numbering** (price list ground→8 vs drawings/marketing "9 קומות"; official dira
   = 8 floors) still to confirm with the sales office; affects the floor premium for edge floors.
5. Absolute ₪ profit favours larger/higher units; `resale_score` favours % return ×
   liquidity. Both columns are in the output — choose per your strategy.
