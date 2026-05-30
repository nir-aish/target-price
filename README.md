# Target Price — choosing a מחיר למשתכן apartment (Sirkin / סירקין)

Helps decide which apartment to pick, optimised for **resale profit**. It parses the
architectural plans (`.dwfx`) and the developer price list, validates them, ranks the
subsidized apartments by estimated profit, and serves it in a small browser app.

## Run the app

No build step or server needed:

```bash
python3 tools/build_app.py      # embeds the latest ranking into app/data.js
```

Then open **`app/index.html`** in a browser (double-click). Filter by building / floor /
rooms, sort by profit or score, click a row for the full cost breakdown and pros/cons.

## Pipeline

```bash
python3 tools/render.py        data/plans/may-11-25-plans.dwfx out/   # DWFx → PNG
python3 tools/parse_sheet.py   data/plans/may-11-25-plans.dwfx        # plans → rooms/areas
python3 tools/parse_pricelist.py data/pricelists/apartment-sizes-and-prices.xlsx  # catalog
python3 tools/rank.py                                                  # resale-profit ranking
python3 tools/build_app.py                                             # refresh app data
```

## Data (committed)

- `data/parsed/apartments.json` — 105 apartments (84 subsidized + 21 free-market)
- `data/parsed/ranking.json` / `.csv` — 84 subsidized, ranked by resale profit
- `app/` — the static browsing app

## Docs

- `docs/PARSING_FINDINGS.md` — DWFx format + extraction
- `docs/VALIDATION.md` — price list ↔ drawings cross-check
- `docs/MEASUREMENT_REVIEW.md` — Israeli plan-reading compliance
- `docs/RANKING_MODEL.md` — cost (15,022 ₪/m² + VAT + indexation − discount) & market model
- `docs/ISRAELI_PREFERENCES.md` — resale-value drivers behind the pros/cons
- `docs/ORIENTATION.md` — north = ~26° W of up; building facings (validated)

## Validated from the web (May 2026) — see `docs/` for details & sources

- **Project = מגרש 201**, יזם **רם אדרת + רובי קפיטל (ספיר)**, 105 דירות (84 מטרה + 21 שוק
  חופשי), 3 buildings, **8 floors "בצמוד לפארק"**, tender won early 2023.
- **Resale lock-in (firm):** market resale only from the **earlier** of *5y after טופס 4*
  or *7y after the tender win* → **~2030** for us. Breach penalty ~₪450k.
- **Cost model corrected:** the price list already embeds the מחיר מטרה discount (the
  −133,230 term); an earlier model double-subtracted a 20%/300k cut. Fixed → top-unit
  profit ~79% (was an inflated ~124%). VAT updated 17→18%.
- **Indexation:** kept ×1.06 central, now documented via the real mechanism — index ~5%/yr,
  but חוק המכר Amendment 9 caps the indexed portion at 40% and a בג"ץ compromise splits the
  differential in thirds; accrues only from full היתר בנייה (none yet). Effective ≈ ×1.04–1.10.
- **Market anchor validated:** PT 2025 ≈29,064 ₪/m² (+6% YoY); our 27k base is central/
  mildly conservative for a new eastern quarter — unchanged.

## Known open items (for next iteration)

- **Orientation per apartment** — `exposure_score()` is **active**. Orientation read off the
  plan's **north arrow** (the needle points up-left ⇒ up≈North, **right=East/green**), confirmed
  by the site plan (green on the right); corner map: bottom-right=**SE (best)**, top-right=NE,
  bottom-left=SW, top-left=NW, mid=S. Per-unit **stack→corner is best-effort (left↔right flagged
  ⚠)** — each unit shows its building floor-plate; confirm against the מפרט מכר before acting.
  See `docs/ORIENTATION.md`.
- **Embedded discount %** — the −133,230 benefit (~8–12%) is smaller than the headline
  14–19%-off-appraisal; confirm the constant against the contract.
- **Floor numbering** — list (ground→8) vs marketing/drawings ("9 קומות"); confirm with sales office.
- **מגרש 110 zoning** — area plan confirms a low-rise park-edge public/institutional band;
  exact plot-110 designation still by buyer screenshot (statutory PDF not machine-readable).
