#!/usr/bin/env python3
"""Extract vector geometry (by colour) from the DWFx floor-plans fpage.

KEY FACT (verified): the <Path> coordinate space is real **millimetres** — one
content unit ≈ 1 mm at 1:1. Checks: the red safe-room box measures ~2.9 x 3.4 m
(its label says 12.3 m²) and the building footprint ~23 m wide. So any feature
you can bound in content units converts to metres by /1000.

Colour legend observed on the floor-plans sheet:
    #000000            walls, dimensions, most linework
    #007FFF / #0080FF  apartment-boundary line (קו גבול דירה)
    #FF0000 / #FF003F  safe room (ממ"ד) reinforced walls + kitchen cabinetry
    #658E67 #81B97D ..  landscaping / gardens (site plan)

Usage:
    python3 tools/extract_geometry.py FIXEDPAGE COLOR X0 Y0 X1 Y1
prints the point count and bounding box (in metres) of that colour in the
content-space window — handy for measuring a room / unit / footprint.
"""
import sys, re

NUM = r'-?\d+(?:\.\d+)?(?:[eE]-?\d+)?'
PATH = re.compile(r'<Path\b[^>]*?Data="([^"]*)"[^>]*?/>')
ATTR = re.compile(r'(?:Stroke|Fill)="(#[0-9A-Fa-f]+)"')
MM_PER_UNIT = 1.0  # verified: content units are millimetres


def path_points(d):
    """Approximate vertex list from an XPS path Data string (abs+rel M/L/H/V;
    curves/arcs are reduced to their endpoint)."""
    toks = re.findall(r'[MmLlHhVvCcAaZz]|' + NUM, d)
    pts, x, y, i, cmd = [], 0.0, 0.0, 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
        if i >= len(toks):
            break
        if cmd in ('M', 'L'):
            x, y = float(toks[i]), float(toks[i + 1]); i += 2; pts.append((x, y))
        elif cmd in ('m', 'l'):
            x += float(toks[i]); y += float(toks[i + 1]); i += 2; pts.append((x, y))
        elif cmd == 'H':
            x = float(toks[i]); i += 1; pts.append((x, y))
        elif cmd == 'h':
            x += float(toks[i]); i += 1; pts.append((x, y))
        elif cmd == 'V':
            y = float(toks[i]); i += 1; pts.append((x, y))
        elif cmd == 'v':
            y += float(toks[i]); i += 1; pts.append((x, y))
        elif cmd in ('Z', 'z'):
            pass
        else:  # C/c/A/a — skip params to next command
            j = i
            while j < len(toks) and not toks[j].isalpha():
                j += 1
            i = j
    return pts


def collect(fpage, color, win=None):
    data = open(fpage, encoding='utf-8', errors='replace').read()
    color = color.upper()
    out = []
    for m in PATH.finditer(data):
        seg = data[max(0, m.start() - 160):m.start() + 60]
        cols = ATTR.findall(m.group(0)) or ATTR.findall(seg)
        if not cols or color not in [c.upper() for c in cols]:
            continue
        for (x, y) in path_points(m.group(1)):
            if win is None or (win[0] <= x <= win[2] and win[1] <= y <= win[3]):
                out.append((x, y))
    return out


if __name__ == '__main__':
    fpage, color = sys.argv[1], sys.argv[2]
    win = tuple(map(float, sys.argv[3:7])) if len(sys.argv) >= 7 else None
    pts = collect(fpage, color, win)
    print(f"{len(pts)} points of {color}")
    if pts:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        w = (max(xs) - min(xs)) * MM_PER_UNIT / 1000
        h = (max(ys) - min(ys)) * MM_PER_UNIT / 1000
        print(f"bbox {w:.2f} m x {h:.2f} m = {w * h:.1f} m²  "
              f"(content x {min(xs):.0f}-{max(xs):.0f}, y {min(ys):.0f}-{max(ys):.0f})")
