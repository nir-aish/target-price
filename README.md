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

## Known open items (for next iteration)

- **Orientation per apartment** — framework ready; needs the brochure/מפרט or a guided
  pass to map each unit (stack) to its corner/facing.
- **Indexation** — using ×1.06 estimate to 1 Jul 2026; firm up with the tender base index.
- **Discount** — modelled as 20% capped at 300k; confirm interpretation.
- **Floor numbering** — list (ground→8) vs drawings (1→9); confirm with sales office.
