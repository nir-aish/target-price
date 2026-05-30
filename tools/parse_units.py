#!/usr/bin/env python3
"""Extract per-apartment structure from the DWFx floor-plans sheet.

WHAT THIS CAN AND CANNOT DO (see docs/DWFX_UNITS.md for the full investigation):

* The .dwfx is an AutoCAD *ePlot* — a flattened 2D plot. It carries vector
  geometry (<Path>) and positioned text (<Glyphs>), but NO semantic room/space
  objects. So "rooms" only exist where the draughtsman typed a room-name label.

* On the floor-plans sheet exactly ONE representative apartment per floor plate
  is labelled with room names + m2 areas (the same unit repeated ~11x, once per
  level). Every other apartment on the plate is drawn as walls+furniture+cm
  dimensions only — no room-name text. The recurring 3-digit numbers
  (101/102/105/108/250/300...) are WALL DIMENSIONS in cm, not apartment IDs.

This tool therefore:
  1. clusters the room-name glyphs of that labelled unit,
  2. attaches the nearest m2 area to each room,
  3. emits a relative layout (N/S/E/W) using page-up=North, larger-x=East,
     larger-y=South (per docs/ORIENTATION.md).

Usage: python3 tools/parse_units.py /path/to/FixedPage.fpage > out.json
"""
import sys, json, xml.etree.ElementTree as ET

ROOM_LABELS = {
    "מגורים": "living (open-plan, incl. kitchen)",
    "הורים": "master bedroom",
    'ממ': 'safe room (mamad)',
    "רחצה": "bathroom",
    "שירות": "WC / service",
    "מרפסת": "balcony",
    "תלייתכביסה": "laundry / service balcony",
}


def local(t):
    return t.rsplit('}', 1)[-1]


def glyphs(fpage):
    out = []
    for _, el in ET.iterparse(fpage, events=('end',)):
        if local(el.tag) == 'Glyphs':
            s = el.get('UnicodeString')
            if s is not None:
                out.append((float(el.get('OriginX', 'nan')),
                            float(el.get('OriginY', 'nan')),
                            float(el.get('FontRenderingEmSize', 'nan')), s))
            el.clear()
    return out


def is_area(s):
    try:
        float(s)
        return '.' in s
    except ValueError:
        return False


def compass(dx, dy):
    # dx>0 = East (larger x = page-right = East); dy>0 = South (larger y = down = South)
    ns = 'N' if dy < -300 else ('S' if dy > 300 else '')
    ew = 'E' if dx > 300 else ('W' if dx < -300 else '')
    return (ns + ew) or 'center'


def main(fpage):
    g = glyphs(fpage)
    big = [(x, y, s) for (x, y, em, s) in g if em >= 140]
    rooms = [(x, y, s) for (x, y, s) in big if s in ROOM_LABELS]
    areas = [(x, y, float(s)) for (x, y, em, s) in g if em >= 140 and is_area(s)]
    # take the first labelled unit (smallest x cluster of room glyphs)
    if not rooms:
        json.dump({"error": "no room labels found"}, sys.stdout)
        return
    x0 = min(r[0] for r in rooms)
    unit = [r for r in rooms if r[0] - x0 < 12000]
    # living room as the anchor
    liv = next((r for r in unit if r[2] == 'מגורים'), unit[0])
    cx, cy = liv[0], liv[1]
    # area labels belonging to this unit (within the cluster window)
    unit_areas = sorted({round(a[2], 1) for a in areas if abs(a[0] - cx) < 12000},
                        reverse=True)
    # ROBUST part: room labels + relative layout. We do NOT force a 1:1
    # area->room mapping (label positions intermix balcony/room areas, so any
    # pairing beyond the living room is a guess). Living = the largest area,
    # centred on the only central label -> the one safe assignment.
    result = []
    seen = set()
    for (rx, ry, name) in sorted(unit, key=lambda r: (r[1], -r[0])):
        key = (name, round(rx / 1000), round(ry / 1000))
        if key in seen:
            continue
        seen.add(key)
        result.append({
            "label_he": name,
            "label_en": ROOM_LABELS[name],
            "rel_to_living": compass(rx - cx, ry - cy),
        })
    out = {
        "note": "ONE representative apartment (the only text-labelled unit on the "
                "sheet; repeated ~11x across floors). Other apartments have geometry "
                "only. Kitchen has no label (open-plan into 'living').",
        "orientation": "page-up=North, larger-x=East, larger-y=South",
        "rooms": result,
        "living_area_m2": max(unit_areas) if unit_areas else None,
        "areas_m2_on_unit_unassigned": unit_areas,
        "area_mapping_caveat": "Only the living area is reliably keyed (largest, "
                "central). The remaining m2 values cannot be reliably paired to "
                "specific rooms from the plot's text positions alone.",
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == '__main__':
    main(sys.argv[1])
