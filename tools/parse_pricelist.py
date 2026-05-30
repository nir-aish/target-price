#!/usr/bin/env python3
"""Flatten the developer's price/area spreadsheet into a per-apartment catalog.

Layout (per the Sirkin file): three vertical blocks = three buildings.
Each block is a grid:
    cols A-E  -> apartment-stack licensed area (m², "שטח רישוי")
    col  F    -> floor  (8..1, or "קרקע" = ground)
    cols H-L  -> sale price incl. VAT, aligned with area cols A-E
A new block starts at each "שטח דירות - רישוי" header row.
"""
import argparse, json
from pathlib import Path
import openpyxl

AREA_COLS = [0, 1, 2, 3, 4]      # A-E
FLOOR_COL = 5                     # F
PRICE_COLS = [7, 8, 9, 10, 11]   # H-L (aligned to AREA_COLS)
HEADER = "שטח דירות"


def norm_floor(v):
    if isinstance(v, str):
        return 0 if "קרקע" in v else None
    if isinstance(v, (int, float)):
        return int(v)
    return None


def parse(xlsx):
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    ws = wb.active
    apartments, building = [], 0
    for row in ws.iter_rows(values_only=True):
        a0 = row[0]
        if isinstance(a0, str) and HEADER in a0:
            building += 1
            continue
        floor = norm_floor(row[FLOOR_COL]) if len(row) > FLOOR_COL else None
        if building == 0 or floor is None:
            continue
        for stack, (ac, pc) in enumerate(zip(AREA_COLS, PRICE_COLS), start=1):
            area = row[ac] if len(row) > ac else None
            price = row[pc] if len(row) > pc else None
            if not isinstance(area, (int, float)):
                continue
            rec = {
                "building": building,
                "floor": floor,
                "stack": stack,
                "area_m2": round(float(area), 2),
                "price_ils": round(float(price)) if isinstance(price, (int, float)) else None,
            }
            rec["price_per_m2"] = (round(rec["price_ils"] / rec["area_m2"])
                                   if rec["price_ils"] else None)
            # subsidized מחיר למשתכן units price ~15.5-16k ₪/m²; free-market ~26k+
            rec["tier"] = ("subsidized" if rec["price_per_m2"] and rec["price_per_m2"] < 20000
                           else "free_market" if rec["price_per_m2"] else None)
            apartments.append(rec)
    return apartments


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("-o", "--out", default="data/parsed/apartments.json")
    a = ap.parse_args()
    apts = parse(a.xlsx)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(apts, ensure_ascii=False, indent=2))
    print(f"{len(apts)} apartments -> {a.out}")
    by_b = {}
    for x in apts:
        by_b.setdefault(x["building"], []).append(x)
    for b, lst in sorted(by_b.items()):
        areas = [x["area_m2"] for x in lst]
        prices = [x["price_ils"] for x in lst if x["price_ils"]]
        ppm = [x["price_per_m2"] for x in lst if x["price_per_m2"]]
        print(f"  Building {b}: {len(lst)} apts | area {min(areas):.0f}-{max(areas):.0f} m² | "
              f"price {min(prices)/1e6:.2f}-{max(prices)/1e6:.2f}M ₪ | "
              f"{min(ppm)}-{max(ppm)} ₪/m²")
