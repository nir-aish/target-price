#!/usr/bin/env python3
"""Crop a region of a DWFx sheet to PNG, in the fpage's own content coordinates.

The floor-plans sheet (page 2) maps content coords -> pixels by a single
isotropic scale = rendered_width / content_x_max (content_x_max ~= 691204).
So you can crop a building footprint or a single apartment cell by giving the
content-space bbox you read off tools/extract_text.py.

Usage:
  python3 tools/crop_plan.py DWFX PAGE X0 Y0 X1 Y1 OUT.png [--dpi 100] [--zoom 3]
Example (first building's footprint on the floor-plans sheet):
  python3 tools/crop_plan.py data/plans/may-11-25-plans.dwfx 2 \
      263000 2500 289000 14000 out/bldg1.png --dpi 100
"""
import argparse, pathlib, shutil, subprocess, sys, tempfile

CONTENT_X_MAX = 691204.0  # text-extent of the floor-plans sheet content space


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dwfx"); ap.add_argument("page", type=int)
    ap.add_argument("x0", type=float); ap.add_argument("y0", type=float)
    ap.add_argument("x1", type=float); ap.add_argument("y1", type=float)
    ap.add_argument("out")
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--zoom", type=int, default=3)
    a = ap.parse_args()
    if not shutil.which("mutool"):
        sys.exit("mutool not found: apt-get install -y mupdf-tools")
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    with tempfile.TemporaryDirectory() as tmp:
        xps = pathlib.Path(tmp) / "doc.xps"; shutil.copy(a.dwfx, xps)
        full = pathlib.Path(tmp) / "page.png"
        subprocess.run(["mutool", "draw", "-o", str(full), "-r", str(a.dpi),
                        str(xps), str(a.page)], check=True)
        im = Image.open(full); W, _ = im.size
        s = W / CONTENT_X_MAX
        box = (int(a.x0 * s), int(a.y0 * s), int(a.x1 * s), int(a.y1 * s))
        crop = im.crop(box)
        if a.zoom != 1:
            crop = crop.resize((crop.width * a.zoom, crop.height * a.zoom))
        pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        crop.save(a.out)
        print(f"wrote {a.out} {crop.size} (scale {s:.5f} px/unit, box {box})")


if __name__ == "__main__":
    main()
