#!/usr/bin/env python3
"""Render a DWFx package's sheets to PNG.

DWFx is an XPS-based OPC (zip) package. mupdf/mutool can render it, but it
misdetects the `.dwfx` extension as PDF, so we hand it a `.xps` copy.

Usage:
    python3 tools/render.py data/plans/may-11-25-plans.dwfx out/ --dpi 90

Requires: mutool (apt-get install mupdf-tools).
"""
import argparse, pathlib, shutil, subprocess, sys, tempfile


def render(dwfx: str, out_dir: str, dpi: int = 90):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        xps = pathlib.Path(tmp) / "doc.xps"
        shutil.copy(dwfx, xps)
        pattern = str(out / "sheet%d.png")
        subprocess.run(
            ["mutool", "draw", "-o", pattern, "-r", str(dpi), str(xps)],
            check=True,
        )
    pngs = sorted(out.glob("sheet*.png"))
    print(f"rendered {len(pngs)} sheet(s) -> {out}/")
    for p in pngs:
        print("  ", p)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dwfx")
    ap.add_argument("out_dir")
    ap.add_argument("--dpi", type=int, default=90)
    a = ap.parse_args()
    if not shutil.which("mutool"):
        sys.exit("mutool not found: apt-get install -y mupdf-tools")
    render(a.dwfx, a.out_dir, a.dpi)
