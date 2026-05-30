#!/usr/bin/env python3
"""Transform-aware reader for the XPS/DWFx FixedPage.

Walks the Canvas tree accumulating the current transform matrix (CTM) so every
Glyphs run and Path gets ABSOLUTE content-space coordinates (real mm). The flat
extractor missed this: title-block text (בנין / קומה) lives in translated
sub-canvases and otherwise reports origin 0,0.

API:
    glyphs(fpage) -> [ {text,x,y,em} ... ]   absolute coords
    paths(fpage)  -> [ {color,pts:[(x,y)...]} ... ]   absolute coords
"""
import re, xml.etree.ElementTree as ET

NUM = r'-?\d+(?:\.\d+)?(?:[eE]-?\d+)?'


def _local(t):
    return t.rsplit('}', 1)[-1]


def _mat(s):
    """'a,b,c,d,e,f' -> (a,b,c,d,e,f)"""
    v = [float(x) for x in s.replace(' ', ',').split(',') if x != '']
    return tuple(v[:6]) if len(v) >= 6 else (1, 0, 0, 1, 0, 0)


def _mul(m, n):
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + c * b2, b * a2 + d * b2,
            a * c2 + c * d2, b * c2 + d * d2,
            a * e2 + c * f2 + e, b * e2 + d * f2 + f)


def _apply(m, x, y):
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def _path_pts(d):
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
        else:
            j = i
            while j < len(toks) and not toks[j].isalpha():
                j += 1
            i = j
    return pts


def _walk(fpage, want_glyphs, want_paths):
    gly, pth = [], []
    stack = [(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)]  # CTM per open Canvas
    tags = []                                  # element-tag stack for parent lookup
    for ev, el in ET.iterparse(fpage, events=('start', 'end')):
        tag = _local(el.tag)
        if ev == 'start':
            tags.append(tag)
            if tag == 'Canvas':
                # tentative: inherit parent CTM; a child MatrixTransform may refine it
                rt = el.get('RenderTransform')
                stack.append(_mul(stack[-1], _mat(rt)) if rt else stack[-1])
            continue
        # end events
        tags.pop()
        parent = tags[-1] if tags else ''
        if tag == 'Canvas':
            stack.pop()
        elif tag == 'MatrixTransform':
            # apply a Canvas's child RenderTransform to the current canvas CTM
            mat = _mat(el.get('Matrix', '1,0,0,1,0,0'))
            if parent == 'Canvas.RenderTransform':
                stack[-1] = _mul(stack[-1], mat)
            el.clear()
        elif tag == 'Glyphs' and want_glyphs:
            s = el.get('UnicodeString')
            if s is not None:
                m = stack[-1]
                rt = el.get('RenderTransform')
                if rt:
                    m = _mul(m, _mat(rt))
                x, y = _apply(m, float(el.get('OriginX', 0)),
                              float(el.get('OriginY', 0)))
                em = float(el.get('FontRenderingEmSize', 0)) * abs(m[0])
                gly.append({'text': s, 'x': x, 'y': y, 'em': em})
            el.clear()
        elif tag == 'Path' and want_paths:
            d = el.get('Data')
            if d:
                col = el.get('Stroke') or el.get('Fill') or '#000000'
                m = stack[-1]
                pts = [_apply(m, px, py) for (px, py) in _path_pts(d)]
                if pts:
                    pth.append({'color': col.upper(), 'pts': pts})
            el.clear()
    return gly, pth


def glyphs(fpage):
    return _walk(fpage, True, False)[0]


def paths(fpage):
    return _walk(fpage, False, True)[1]


if __name__ == '__main__':
    import sys
    g = glyphs(sys.argv[1])
    print(f"{len(g)} glyphs (absolute coords)")
    for r in g:
        if r['text'] in ('בנין', 'קומה') or r['em'] > 400:
            print(f"  x={r['x']:.0f} y={r['y']:.0f} em={r['em']:.0f}  {r['text']}")
