#!/usr/bin/env python3
"""Resale-profit ranking for the subsidized (מחיר מטרה) apartments — plot 201.

Goal: the buyer intends to resell for maximum profit. Each subsidized unit is
bought at the fixed מחיר מטרה contract price (~15.5–16.2k ₪/m²); its resale value
is the open-market price. We estimate market value from THIS project's own
free-market units (a clean, local anchor) plus standard Israeli resale premiums,
then rank by profit.

profit = estimated_market_value − purchase_price

All model assumptions are explicit constants below and documented in
docs/RANKING_MODEL.md. Outputs are decision-support ESTIMATES, not appraisals.
"""
import argparse, csv, json, statistics as st
from pathlib import Path

# --- Purchase-cost model (official מחיר מטרה contract price) ----------------------
# The price list IS the contractual מחיר מטרה price. It reverse-engineers EXACTLY to
#   price_ils = (15022 × area − 133230) × 1.17
# i.e. a base of 15,022 ₪/m² less a fixed 133,230 ₪ benefit (the embedded מחיר מטרה
# discount), at the then-current 17% VAT and the tender base index. We update it to
# today's terms:
#   • VAT 17% → 18% (since 1 Jan 2025).
#   • indexation of מדד תשומות הבנייה from the tender base to payment (bounded; see below).
# The discount is ALREADY inside this price (the −133,230 term). We do NOT subtract an
# additional benefit. (A prior model wrongly applied a further 20% / 300k cut on top —
# a double-count; corrected here.)
OFFICIAL_BASE_PPM = 15022        # ₪/m², before the embedded benefit, VAT and indexation
PREVAT_BENEFIT    = 133230       # ₪, embedded מחיר מטרה discount (fixed pre-VAT deduction)
VAT               = 0.18         # current Israeli VAT (since 1 Jan 2025); list was at 17%
INDEXATION        = 1.06         # מדד תשומות הבנייה, tender base → payment. BOUNDED estimate:
                                 # the index rises ~5%/yr (2023 +2.0%, 2024 +2.9%, 2025 +5.1%),
                                 # BUT (a) Amendment 9 to חוק המכר caps the indexed portion at
                                 # 40% of price, (b) a בג"ץ compromise splits the differential
                                 # in thirds (buyer's add-on ≈ 4,043–8,206 ₪), and (c) indexation
                                 # accrues only from the LATER of contract-signing / full היתר
                                 # בנייה — and this project has no היתר yet. Effective ≈ ×1.04–1.10;
                                 # the RANKING ORDER is invariant to it. See docs/RANKING_MODEL.md.

def purchase_cost(area):
    """Returns (full_price, embedded_benefit, net_purchase_price) at current terms."""
    full    = OFFICIAL_BASE_PPM * area * (1 + VAT) * INDEXATION   # before the מטרה benefit
    benefit = PREVAT_BENEFIT * (1 + VAT) * INDEXATION             # embedded discount
    return round(full), round(benefit), round(full - benefit)

# --- Market model, calibrated to this project's free-market residential units -----
# Observed in-project free-market ₪/m² by floor (large units): f5≈26.2k, f6≈26.3k,
# f7≈29.3k, f8≈30.2k. Cross-checked vs Petah-Tikva resale comps (2025): citywide avg
# ≈29,064 ₪/m² (+6% YoY); 4-room second-hand ≈23.5k; new builds command a premium.
# Sirkin is a brand-new premium eastern quarter, so 27k (mid-floor) is a central,
# mildly conservative anchor — see docs/RANKING_MODEL.md.
MARKET_BASE_PPM = 27000          # ₪/m² at a mid floor, standard-size unit
FLOOR_FACTOR = {                 # resale premium by floor (higher = more valuable)
    0: 0.92, 1: 0.95, 2: 0.97, 3: 0.99, 4: 1.00,
    5: 1.02, 6: 1.04, 7: 1.07, 8: 1.10,
}
def size_factor(area):           # smaller flats fetch a higher ₪/m² on resale
    if area < 90:  return 1.05
    if area < 115: return 1.00
    return 0.97

# Resale liquidity: 3–4 room flats (~76–95 m²) are the most in-demand / fastest to sell.
def liquidity(area):
    if 76 <= area <= 95:  return 1.00     # most liquid
    if 95 < area <= 112:  return 0.95
    return 0.88

# --- Exposure model for plot 201 (sun + surroundings). See docs/SURROUNDINGS.md. ---
# Neighbours: East = open green / park (good); South=bldg 200, West=school 101,
# North=bldg 104. All neighbours ~8 floors (same height) → facing a building is blocked
# at every floor. Combines Israeli sun preference (S best, N worst) with open-view (east
# green). Developer markets the project as "בצמוד לפארק" and showcases the NE/SE facades.
EXPOSURE = {            # facade facing -> desirability multiplier (1.0 = neutral)
    "SE": 1.10, "E": 1.08, "NE": 1.06,     # toward the eastern green / park / sun — best
    "S": 1.00,                              # great sun but faces bldg 200
    "SW": 0.96, "W": 0.94, "NW": 0.92,      # face school/rental, weaker sun
    "N": 0.93,
}
def exposure_score(facing):
    """Multiplier for a unit's facade direction. Returns 1.0 if facing unknown."""
    return EXPOSURE.get(facing, 1.0)

# Per-unit facade direction, keyed by (building, stack). The exposure multiplier flows
# straight into market value as soon as this map is populated.
# POPULATING IT NEEDS the brochure / מפרט מכר (which lists each unit's כיוונים) or a
# guided plan-read: the price list has 5 stacks per building, but the floor plates show
# 4 corners + 1 mid-facade unit, and the plan's apartment numbers (101/102/105/108) do
# not key to price-list stacks 1–5. Left EMPTY → neutral (1.0) for every unit, so the
# ranking is not distorted by guesses. See docs/ORIENTATION.md / docs/SURROUNDINGS.md.
STACK_FACING = {
    # (building, stack): "NE" | "SE" | "SW" | "NW" | "N" | "S" | "E" | "W"
}
def facing_of(apt):
    return STACK_FACING.get((apt["building"], apt["stack"]))

def market_ppm(area, floor, facing=None):
    return (MARKET_BASE_PPM * FLOOR_FACTOR.get(floor, 1.0)
            * size_factor(area) * exposure_score(facing))


def rooms_est(area):
    """Approx. room count from area (מחיר מטרה typical sizing)."""
    if area <= 82:  return "3"
    if area <= 100: return "4"
    return "4–5"

def pros_cons(apt, facing=None):
    """Pros/cons reflecting Israeli resale preferences (see docs/ISRAELI_PREFERENCES.md)."""
    pros, cons = [], []
    f, ar, ppm = apt["floor"], apt["area_m2"], apt["price_per_m2"]
    rooms = rooms_est(ar)
    # floor — higher = light/air/quiet/view (with elevator); ground = weakest
    if f >= 6:   pros.append(f"קומה גבוהה ({f}): אור, אוויר, נוף ושקט — מבוקש")
    elif f >= 3: pros.append(f"קומה אמצעית ({f}): ביקוש רחב ויציב")
    if f == 0:   cons.append("קומת קרקע: פחות אטרקטיבית (פרטיות/אור/נוף)")
    elif f <= 2: cons.append(f"קומה נמוכה ({f}): קרובה לרחוב, פרמיה נמוכה")
    # rooms / liquidity — 3–4 rooms = largest buyer pool, fastest resale
    if rooms in ("3", "4"):
        pros.append(f"~{rooms} חד': הקהל הרחב ביותר — נזיל למכירה חוזרת")
    else:
        cons.append("דירה גדולה/יקרה יחסית: קהל קונים מצומצם יותר")
    # entry price — built-in מחיר מטרה discount
    if ppm <= 15700:
        pros.append("מחיר כניסה נמוך במיוחד למ\"ר")
    # cross-ventilation — building is 4 corner-units/floor (2 כיווני אוויר)
    pros.append("דירת פינה צפויה (2 כיווני אוויר): אוורור ואור — מבוקש בישראל")
    # facing — only when known (from brochure/מפרט)
    if facing in ("SE", "NE", "E"):
        pros.append(f"כיוון {facing}: לכיוון הפארק/הירוק במזרח — נוף פתוח ושמש (חזית ראווה)")
    elif facing in ("SW", "NW", "W", "N"):
        cons.append(f"כיוון {facing}: פונה למבנה שכן (בי\"ס/מבנה מגורים) — נוף חסום")
    return pros, cons


def rank(apartments):
    sub = [a for a in apartments if a.get("tier") == "subsidized"]
    out = []
    for a in sub:
        facing = facing_of(a)
        full, benefit, net_cost = purchase_cost(a["area_m2"])
        ppm = market_ppm(a["area_m2"], a["floor"], facing)
        mkt = round(ppm * a["area_m2"])
        profit = mkt - net_cost
        rec = dict(a)
        rec["sheet_price_ref"] = a["price_ils"]          # original price-list figure (17% VAT, base idx)
        rec["gross_price"] = full                         # full price before the מטרה benefit (18% VAT + idx)
        rec["target_discount"] = benefit                  # embedded מחיר מטרה benefit (the −133,230 term)
        rec["purchase_price"] = net_cost                  # what you actually pay
        rec["facing"] = facing or "—"                     # per-unit facade (— = pending brochure)
        rec["exposure_factor"] = round(exposure_score(facing), 3)
        rec["est_market_ppm"] = round(ppm)
        rec["est_market_value"] = mkt
        rec["est_profit_ils"] = profit
        rec["est_profit_pct"] = round(100 * profit / net_cost, 1)
        rec["liquidity"] = liquidity(a["area_m2"])
        # composite resale score: % return weighted by how easily it sells
        rec["resale_score"] = round(rec["est_profit_pct"] * rec["liquidity"], 1)
        rec["pros"], rec["cons"] = pros_cons(a, facing)
        out.append(rec)
    out.sort(key=lambda r: (-r["resale_score"], -r["est_profit_ils"]))
    for i, r in enumerate(out, 1):
        r["rank"] = i
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("apartments", nargs="?", default="data/parsed/apartments.json")
    ap.add_argument("-o", "--out", default="data/parsed/ranking.json")
    a = ap.parse_args()
    apts = json.load(open(a.apartments))
    ranked = rank(apts)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(ranked, ensure_ascii=False, indent=2))
    # CSV for quick viewing
    csv_path = a.out.replace(".json", ".csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "building", "floor", "stack", "area_m2", "facing", "gross_price",
                    "target_discount", "purchase_price", "est_market_value",
                    "est_profit_ils", "est_profit_pct", "liquidity", "resale_score"])
        for r in ranked:
            w.writerow([r["rank"], r["building"], r["floor"], r["stack"], r["area_m2"],
                        r["facing"], r["gross_price"], r["target_discount"],
                        r["purchase_price"], r["est_market_value"], r["est_profit_ils"],
                        r["est_profit_pct"], r["liquidity"], r["resale_score"]])
    print(f"ranked {len(ranked)} subsidized apartments -> {a.out} (+ .csv)")
    print(f"cost model: base {OFFICIAL_BASE_PPM} ₪/m² × idx {INDEXATION} × VAT {1+VAT} "
          f"− embedded benefit {PREVAT_BENEFIT:,} (no extra discount)")
    known = sum(1 for r in ranked if r["facing"] != "—")
    print(f"per-unit facing populated: {known}/{len(ranked)} "
          f"({'exposure active' if known else 'exposure neutral — awaiting brochure/מפרט'})")
    print("\nTOP 10 by resale score:")
    print(f"{'#':>2} {'bld':>3} {'flr':>3} {'m²':>6} {'buy':>9} {'mkt val':>9} "
          f"{'profit':>9} {'%':>5} {'score':>5}")
    for r in ranked[:10]:
        print(f"{r['rank']:>2} {r['building']:>3} {r['floor']:>3} {r['area_m2']:>6.1f} "
              f"{r['purchase_price']/1e6:>8.2f}M {r['est_market_value']/1e6:>8.2f}M "
              f"{r['est_profit_ils']/1e6:>8.2f}M {r['est_profit_pct']:>5.0f} {r['resale_score']:>5.0f}")
