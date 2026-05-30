#!/usr/bin/env python3
"""Resale-profit ranking for the subsidized (מחיר למשתכן) apartments.

Goal: the buyer intends to resell for maximum profit. Each subsidized unit is
bought at a fixed ~15.5–16.2k ₪/m²; its resale value is the open-market price.
We estimate market value from THIS project's own free-market units (a clean,
local anchor) plus standard Israeli resale premiums, then rank by profit.

profit = estimated_market_value − purchase_price

All model assumptions are explicit constants below and documented in
docs/RANKING_MODEL.md. Outputs are decision-support ESTIMATES, not appraisals.
"""
import argparse, csv, json, statistics as st
from pathlib import Path

# --- Purchase-cost model (official מחיר למשתכן price), overrides the spreadsheet ---
# Spreadsheet reverse-engineered exactly to: (15022 × area − 133230) × 1.17  (17% VAT).
OFFICIAL_BASE_PPM = 15022        # ₪/m², before VAT and indexation (per buyer)
PREVAT_FIXED = 133230            # ₪, constant deduction reproducing the sheet (meaning unconfirmed)
VAT = 0.18                       # current Israeli VAT (since 1 Jan 2025)
INDEXATION = 1.06                # ESTIMATE: מדד תשומות הבנייה, tender base → 2026-07-01.
                                 # Needs the tender base-index date to firm up (see docs).
TARGET_DISCOUNT_PCT = 0.20       # מחיר מטרה benefit: 20% off final price...
TARGET_DISCOUNT_CAP = 300000     # ...capped at 300,000 ₪ (whichever is smaller)

def purchase_cost(area):
    gross = (OFFICIAL_BASE_PPM * area - PREVAT_FIXED) * INDEXATION * (1 + VAT)
    discount = min(TARGET_DISCOUNT_CAP, TARGET_DISCOUNT_PCT * gross)
    return round(gross), round(discount), round(gross - discount)

# --- Market model, calibrated to this project's free-market residential units ---
# Observed free-market ₪/m² by floor (large units): f5≈26.2k, f6≈26.3k, f7≈29.3k, f8≈30.2k.
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

def market_ppm(area, floor):
    return MARKET_BASE_PPM * FLOOR_FACTOR.get(floor, 1.0) * size_factor(area)


def rooms_est(area):
    """Approx. room count from area (מחיר למשתכן typical sizing)."""
    if area <= 82:  return "3"
    if area <= 100: return "4"
    return "4–5"

def pros_cons(apt):
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
    # entry price — built-in מחיר למשתכן discount
    if ppm <= 15700:
        pros.append("מחיר כניסה נמוך במיוחד למ\"ר")
    # cross-ventilation — building is 4 corner-units/floor (2 כיווני אוויר)
    pros.append("דירת פינה צפויה (2 כיווני אוויר): אוורור ואור — מבוקש בישראל")
    return pros, cons


def rank(apartments):
    sub = [a for a in apartments if a.get("tier") == "subsidized"]
    out = []
    for a in sub:
        gross, discount, net_cost = purchase_cost(a["area_m2"])
        ppm = market_ppm(a["area_m2"], a["floor"])
        mkt = round(ppm * a["area_m2"])
        profit = mkt - net_cost
        rec = dict(a)
        rec["sheet_price_ref"] = a["price_ils"]          # original spreadsheet price
        rec["gross_price"] = gross                        # official base + VAT + indexation
        rec["target_discount"] = discount                 # 20% / 300k benefit
        rec["purchase_price"] = net_cost                  # what you actually pay
        rec["est_market_ppm"] = round(ppm)
        rec["est_market_value"] = mkt
        rec["est_profit_ils"] = profit
        rec["est_profit_pct"] = round(100 * profit / net_cost, 1)
        rec["liquidity"] = liquidity(a["area_m2"])
        # composite resale score: % return weighted by how easily it sells
        rec["resale_score"] = round(rec["est_profit_pct"] * rec["liquidity"], 1)
        rec["pros"], rec["cons"] = pros_cons(a)
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
        w.writerow(["rank", "building", "floor", "area_m2", "gross_price",
                    "target_discount", "purchase_price", "est_market_value",
                    "est_profit_ils", "est_profit_pct", "liquidity", "resale_score"])
        for r in ranked:
            w.writerow([r["rank"], r["building"], r["floor"], r["area_m2"],
                        r["gross_price"], r["target_discount"], r["purchase_price"],
                        r["est_market_value"], r["est_profit_ils"],
                        r["est_profit_pct"], r["liquidity"], r["resale_score"]])
    print(f"ranked {len(ranked)} subsidized apartments -> {a.out} (+ .csv)")
    print(f"cost model: base {OFFICIAL_BASE_PPM} ₪/m² × idx {INDEXATION} × VAT {1+VAT} "
          f"− min(20%, {TARGET_DISCOUNT_CAP:,})")
    print("\nTOP 10 by resale score:")
    print(f"{'#':>2} {'bld':>3} {'flr':>3} {'m²':>6} {'buy':>9} {'mkt val':>9} "
          f"{'profit':>9} {'%':>5} {'score':>5}")
    for r in ranked[:10]:
        print(f"{r['rank']:>2} {r['building']:>3} {r['floor']:>3} {r['area_m2']:>6.1f} "
              f"{r['purchase_price']/1e6:>8.2f}M {r['est_market_value']/1e6:>8.2f}M "
              f"{r['est_profit_ils']/1e6:>8.2f}M {r['est_profit_pct']:>5.0f} {r['resale_score']:>5.0f}")
