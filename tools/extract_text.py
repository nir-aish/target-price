#!/usr/bin/env python3
"""Extract text glyphs (with positions) from an XPS FixedPage.fpage inside a DWFx."""
import sys, xml.etree.ElementTree as ET

def local(tag): return tag.rsplit('}', 1)[-1]

def extract(fpage_path):
    out = []
    for event, el in ET.iterparse(fpage_path, events=('end',)):
        if local(el.tag) == 'Glyphs':
            s = el.get('UnicodeString')
            if s is None:
                el.clear(); continue
            out.append({
                'text': s,
                'x': float(el.get('OriginX', 'nan')),
                'y': float(el.get('OriginY', 'nan')),
                'em': float(el.get('FontRenderingEmSize', 'nan')),
            })
            el.clear()
    return out

if __name__ == '__main__':
    rows = extract(sys.argv[1])
    print(f"glyph runs: {len(rows)}", file=sys.stderr)
    for r in rows:
        print(f"{r['x']:.1f}\t{r['y']:.1f}\t{r['em']:.1f}\t{r['text']}")
