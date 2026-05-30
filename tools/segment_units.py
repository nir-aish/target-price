#!/usr/bin/env python3
"""Segment the floor-plans sheet into per-apartment crops and match to the list.

Pipeline (all geometry in real mm — verified, see docs/APARTMENT_EXTRACTION.md):

  1. Parse the floor-plans FixedPage into coloured point clouds
     (black walls, blue apartment boundary, red mamad/kitchen).
  2. Find COMPOSITE floor plans: each composite is one floor showing all 3
     buildings. We seed composites from the room-labelled living rooms and/or
     from x-gaps in the wall density, then within each composite find the
     building-square blocks via 2-D connected components on the linework mask.
  3. Within each building square, split into the 5 apartment cells
     (4 corners + 1 mid-facade) and flood-fill each cell using ALL linework as
     barriers (black+blue+red) — this closes the dashed blue boundary far better
     than blue alone — to MEASURE each cell's floor area in m².
  4. MATCH: the composite's (building,floor) is identified by its measured area
     multiset against the per-(building,floor) area sets from apartments.json;
     within the square each cell is assigned to the stack with the nearest area.
  5. FACING: cell centroid vs square centre -> corner -> facing via ORIENTATION
     (page-up=N, right=E; bottom-right=SE best ... top-left=NW weakest).
  6. CROP each cell from a high-DPI render and emit data/parsed/unit_plans.json.

This module is intentionally split into pure-geometry steps (no image display
needed) and a thin rendering/crop step, so the matching can be validated purely
numerically and re-run headless.
"""
import argparse, json, sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).parent))
import xps_reader as X  # noqa: E402

# --- colour buckets -------------------------------------------------------
BLACK = {'#000000'}
BLUE = {'#007FFF', '#0080FF'}
RED = {'#FF0000', '#FF003F'}


def load_points(fpage):
    """Return dict of Nx2 float arrays: black/blue/red linework in content mm."""
    buckets = {'black': [], 'blue': [], 'red': []}
    for p in X.paths(fpage):
        c = p['color']
        k = 'black' if c in BLACK else 'blue' if c in BLUE else 'red' if c in RED else None
        if k:
            buckets[k].extend(p['pts'])
    return {k: np.array(v, np.float32) if v else np.zeros((0, 2), np.float32)
            for k, v in buckets.items()}


# --- area sets per (building,floor) from the price/area list --------------
def area_sets(apartments_json):
    apts = json.load(open(apartments_json))
    bf = {}
    for a in apts:
        bf.setdefault((a['building'], a['floor']), []).append(a)
    return apts, bf


# --- building-square detection within a window ----------------------------
def find_squares(pts_xy, res=50.0, dil=4, min_m=11, max_m=34):
    """2-D connected components on a linework mask -> square bboxes (content mm)."""
    if len(pts_xy) == 0:
        return []
    x0, y0 = pts_xy[:, 0].min(), pts_xy[:, 1].min()
    W = int((pts_xy[:, 0].max() - x0) / res) + 4
    H = int((pts_xy[:, 1].max() - y0) / res) + 4
    img = np.zeros((H, W), np.uint8)
    img[((pts_xy[:, 1] - y0) / res).astype(int),
        ((pts_xy[:, 0] - x0) / res).astype(int)] = 1
    lbl, n = ndi.label(ndi.binary_dilation(img, iterations=dil))
    out = []
    for sl in ndi.find_objects(lbl):
        if sl is None:
            continue
        ys, xs = sl
        w = (xs.stop - xs.start) * res / 1000.0
        h = (ys.stop - ys.start) * res / 1000.0
        if min_m < w < max_m and min_m < h < max_m:
            out.append({
                'x0': float(x0 + xs.start * res), 'x1': float(x0 + xs.stop * res),
                'y0': float(y0 + ys.start * res), 'y1': float(y0 + ys.stop * res),
                'w_m': round(w, 1), 'h_m': round(h, 1),
                'cx': float(x0 + (xs.start + xs.stop) / 2 * res),
                'cy': float(y0 + (ys.start + ys.stop) / 2 * res)})
    return out


# --- measure apartment cells inside one square ----------------------------
def measure_cells(all_pts, sq, res=20.0, pad=300.0):
    """Flood-fill enclosed regions inside a square using all linework as walls.

    Returns list of {area_m2, cx, cy} for apartment-sized enclosed regions.
    """
    x0, y0, x1, y1 = sq['x0'] - pad, sq['y0'] - pad, sq['x1'] + pad, sq['y1'] + pad
    m = ((all_pts[:, 0] >= x0) & (all_pts[:, 0] <= x1) &
         (all_pts[:, 1] >= y0) & (all_pts[:, 1] <= y1))
    pts = all_pts[m]
    if len(pts) == 0:
        return []
    W = int((x1 - x0) / res) + 2
    H = int((y1 - y0) / res) + 2
    img = np.zeros((H, W), np.uint8)
    img[((pts[:, 1] - y0) / res).astype(int),
        ((pts[:, 0] - x0) / res).astype(int)] = 1
    img = ndi.binary_closing(ndi.binary_dilation(img, iterations=1), iterations=3)
    lbl, n = ndi.label(~img)
    border = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]])))
    cnt = np.bincount(lbl.ravel())
    com = ndi.center_of_mass(np.ones_like(lbl), lbl, range(1, n + 1))
    cells = []
    for i in range(1, n + 1):
        if i in border:
            continue
        a = cnt[i] * (res / 1000.0) ** 2
        if 25 < a < 320:
            cy, cx = com[i - 1]
            cells.append({'area_m2': round(a, 1),
                          'cx': float(x0 + cx * res), 'cy': float(y0 + cy * res)})
    return cells


# --- facing from corner position (ORIENTATION: up=N, right=E) --------------
def facing(cx, cy, sq):
    mx, my = (sq['x0'] + sq['x1']) / 2, (sq['y0'] + sq['y1']) / 2
    ew = 'E' if cx > mx + 1500 else 'W' if cx < mx - 1500 else ''
    ns = 'N' if cy < my - 1500 else 'S' if cy > my + 1500 else ''
    return (ns + ew) or 'C'


RESALE = {'SE': 'best (south sun + east green)', 'NE': 'good (east green, AM sun)',
          'S': 'south sun', 'SW': 'ok (south sun, faces school)',
          'NW': 'weakest (no sun, faces neighbours)', 'N': 'north', 'E': 'east',
          'W': 'west', 'C': 'mid-facade'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fpage')
    ap.add_argument('--apartments', default='data/parsed/apartments.json')
    ap.add_argument('--out', default='data/parsed/unit_plans.json')
    a = ap.parse_args()
    pts = load_points(a.fpage)
    allp = np.vstack([pts['black'], pts['blue'], pts['red']])
    apts, bf = area_sets(a.apartments)
    squares = find_squares(allp)
    report = {'n_squares': len(squares), 'squares': []}
    for sq in squares:
        cells = measure_cells(allp, sq)
        for c in cells:
            c['facing'] = facing(c['cx'], c['cy'], sq)
            c['resale'] = RESALE.get(c['facing'], '')
        report['squares'].append({**sq, 'n_cells': len(cells), 'cells': cells})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(report, open(a.out, 'w'), ensure_ascii=False, indent=1)
    # numeric summary (display-independent)
    print(f"squares={len(squares)}")
    for i, s in enumerate(report['squares']):
        areas = sorted(c['area_m2'] for c in s['cells'])
        print(f"  sq{i} cx={s['cx']:.0f} cy={s['cy']:.0f} {s['w_m']}x{s['h_m']}m "
              f"cells={s['n_cells']} areas={areas}")


if __name__ == '__main__':
    main()
