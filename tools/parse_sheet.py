#!/usr/bin/env python3
"""Parse the floor-plan sheet of the Sirkin DWFx into structured drawings.

Pipeline:
  1. Locate the "תכניות" (plans) section in the DWFx package.
  2. Extract text glyph runs (Unicode + position) from its FixedPage.fpage.
  3. Apply the Canvas 0.08 RenderTransform to get page-unit coordinates.
  4. Split the (single-row) layout into individual drawings by vertical
     whitespace gaps in X.
  5. For each drawing: reconstruct RTL Hebrew text lines, classify it
     (floor plan / unit / site plan / 3D view), and pair room labels with
     their nearest numeric label (candidate areas).

Output: JSON list of drawings with reconstructed text and room/number pairs.
"""
import argparse, json, math, re, shutil, sys, tempfile, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

CANVAS_SCALE = 0.08            # FixedPage Canvas RenderTransform
XGAP = 650                     # min horizontal whitespace (page units) between drawings
ROOM_WORDS = ["מגורים", "הורים", "ממ", "רחצה", "שירות", "מרפסת",
              "מטבח", "חדר", "כביסה", "ארונות", "מבואה", "חדרון"]
ROOM_LABEL = {"מגורים": "living", "הורים": "master bed", "ממ": "safe room (ממ\"ד)",
              "רחצה": "bath", "שירות": "WC", "מרפסת": "balcony", "מטבח": "kitchen",
              "כביסה": "laundry", "ארונות": "closets", "מבואה": "entry",
              "חדר": "room", "חדרון": "small room"}
FLOOR_TITLE = re.compile(r"תוכנית\s*קומה.*?(-?\d+)|גג\s*עליון")
AREA = re.compile(r"^\d{1,2}\.\d$")          # room area, e.g. 12.3, 5.1
APT_NO = re.compile(r"^1\d{2}$")               # apartment number, 100-199


def local(t): return t.rsplit("}", 1)[-1]


def find_plans_fpage(zf):
    """Return (fpage_bytes) for the section named 'תכניות'."""
    for name in zf.namelist():
        if name.endswith("descriptor.xml") and "ePlot_" in name:
            xml = zf.read(name)
            if b"DWF-ePlot" in xml:
                root = ET.fromstring(xml)
                if root.get("name") == "תכניות":
                    base = name.rsplit("/", 1)[0]
                    return zf.read(f"{base}/FixedPage.fpage")
    raise SystemExit("plans section ('תכניות') not found")


def extract_runs(fpage_bytes):
    runs = []
    for _, el in ET.iterparse(_bytes_io(fpage_bytes), events=("end",)):
        if local(el.tag) == "Glyphs":
            s = el.get("UnicodeString")
            if s and s.strip():
                runs.append((
                    float(el.get("OriginX", 0)) * CANVAS_SCALE,
                    float(el.get("OriginY", 0)) * CANVAS_SCALE,
                    float(el.get("FontRenderingEmSize", 0)) * CANVAS_SCALE,
                    s,
                ))
            el.clear()
    return runs


def _bytes_io(b):
    import io
    return io.BytesIO(b)


def split_columns(runs):
    """Split into drawings by big X gaps. Returns list of run-lists."""
    runs = sorted(runs, key=lambda r: r[0])
    cols, cur, last_x = [], [], None
    for r in runs:
        if last_x is not None and r[0] - last_x > XGAP:
            cols.append(cur); cur = []
        cur.append(r); last_x = r[0]
    if cur:
        cols.append(cur)
    return cols


def reconstruct_lines(runs):
    """Group runs into text lines (by Y), read RTL (X descending)."""
    lines, cur, cy = [], [], None
    for x, y, em, t in sorted(runs, key=lambda r: (round(r[1], 0), -r[0])):
        if cy is None or abs(y - cy) <= max(em * 0.7, 5):
            cur.append((x, t)); cy = y if cy is None else cy
        else:
            lines.append(cur); cur = [(x, t)]; cy = y
    if cur:
        lines.append(cur)
    return ["".join(t for _, t in sorted(l, key=lambda xt: -xt[0])) for l in lines]


def pair_rooms(runs):
    """Pair each room-word run with its nearest AREA (decimal) run."""
    rooms = [(x, y, t) for x, y, em, t in runs
             if any(t.strip() == w or t.strip().startswith(w) for w in ROOM_WORDS)]
    areas = [(x, y, t) for x, y, em, t in runs if AREA.match(t.strip())]
    out = []
    for rx, ry, rt in rooms:
        best, bd = None, 1e9
        for nx, ny, nt in areas:
            d = math.hypot(rx - nx, ry - ny)
            if d < bd:
                bd, best = d, nt
        key = next((w for w in ROOM_WORDS if rt.strip().startswith(w)), rt.strip())
        out.append({"room": ROOM_LABEL.get(key, key), "he": rt.strip(),
                    "area_m2": float(best) if best and bd < 40 else None,
                    "dist": round(bd, 1)})
    return out


def apartment_numbers(runs):
    seen = []
    for x, y, em, t in runs:
        if APT_NO.match(t.strip()) and t.strip() not in seen:
            seen.append(t.strip())
    return seen


def classify(text):
    if "מבט" in text:
        return "3d_view"
    if "גינון" in text or "מתקנים כפולים" in text or "פינוי" in text:
        return "site_plan"
    m = FLOOR_TITLE.search(text)
    if m:
        return "floor_plan"
    if any(w in text for w in ROOM_WORDS):
        return "unit_plan"
    return "other"


def parse(dwfx):
    with zipfile.ZipFile(dwfx) as zf:
        fpage = find_plans_fpage(zf)
    runs = extract_runs(fpage)
    drawings = []
    for i, col in enumerate(split_columns(runs)):
        xs = [r[0] for r in col]; ys = [r[1] for r in col]
        lines = reconstruct_lines(col)
        text = " ".join(lines)
        kind = classify(text)
        fm = FLOOR_TITLE.search(text)
        floor = None
        if fm:
            floor = fm.group(1) if fm.group(1) else "roof"
        drawings.append({
            "id": i,
            "kind": kind,
            "floor": floor,
            "bbox": [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))],
            "n_runs": len(col),
            "apartment_numbers": apartment_numbers(col) if kind in ("unit_plan", "floor_plan") else [],
            "rooms": pair_rooms(col) if kind in ("unit_plan", "floor_plan") else [],
            "lines": lines,
        })
    return {"source": str(dwfx), "n_drawings": len(drawings), "drawings": drawings}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dwfx")
    ap.add_argument("-o", "--out", default="out/plans.json")
    a = ap.parse_args()
    result = parse(a.dwfx)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"{result['n_drawings']} drawings -> {a.out}")
    from collections import Counter
    c = Counter(d["kind"] for d in result["drawings"])
    print("by kind:", dict(c))
    print("floors found:", [d["floor"] for d in result["drawings"] if d["floor"]])
