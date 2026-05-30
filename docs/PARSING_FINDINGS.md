# Parsing findings — Sirkin (סירקין) מחיר למשתכן plans

Source file: `data/plans/may-11-25-plans.dwfx` (23 MB), exported from AutoCAD 2022.
Project title embedded in the file: **"הגשה מלאה סירקין 05.05.2025"** (Full submission, Sirkin).

## File format

`.dwfx` is **DWFx** — an XPS-based OPC package, i.e. a ZIP. It unzips to a
standard XPS `FixedDocumentSequence` with one `FixedPage.fpage` per sheet.
No proprietary decoding needed.

```
[Content_Types].xml
FixedDocumentSequence.fdseq
dwf/documents/<GUID>/sections/com.autodesk.dwf.ePlot_<GUID>/
    FixedPage.fpage      <- vector content (Glyphs = text, Path = geometry)
    descriptor.xml       <- sheet name, paper size, units, AutoCAD metadata
    *.png  *.odttf       <- raster images, embedded (obfuscated) fonts
```

## Sheets (3)

| plotOrder | Name (Hebrew)        | Meaning              | Paper (mm)   |
|-----------|----------------------|----------------------|--------------|
| 1         | דף 1                 | cover sheet          | 7000 × 910   |
| 2         | תכניות               | floor plans          | 17000 × 900  |
| 3         | חתכים חזיתות         | sections & elevations| 8330 × 900   |

The **תכניות** sheet (the important one) is a 17 m-wide plot containing, left→right:
a site/development plan, per-floor plans (floors **-2, -1, 1–9, roof**),
apartment unit plans, and 3D building renderings
(`מבט מכוון צפון מזרח` = view NE, `מבט מכוון דרום מזרח` = view SE).

## Text extraction — WORKS

Text is stored as readable Unicode in the `UnicodeString` attribute of XPS
`<Glyphs>` elements (Hebrew as XML char entities). **No OCR, no font
de-obfuscation needed.** The plans sheet has 2105 text runs.

Caveats found:
- Text is **fragmented into many short positioned runs** — e.g. the m² marker
  `מ"ר` is split into three runs `מ` + `"` + `ר`; words split per token.
  Reassembly must group runs by position.
- Hebrew is **right-to-left**: within a line, sort runs by X descending.
- The sheet holds many sub-drawings side by side, so simple row-grouping merges
  unrelated drawings. **2D spatial clustering** (cluster runs by X+Y proximity)
  is required to isolate one apartment/floor at a time.

Room labels confirmed present: `מגורים` (living), `הורים` (master),
`ממ"ד` (safe room), `רחצה` (bath), `שירות` (WC), `מרפסת` (balcony),
`תליית כביסה` (laundry), with adjacent numbers (areas / dimensions — exact
meaning to be confirmed per unit).

Tool: `tools/extract_text.py <FixedPage.fpage>` → TSV of `x  y  emSize  text`.

## Rendering — WORKS

`mutool` (mupdf) renders the package if given a `.xps` extension (it misdetects
`.dwfx` as PDF). See `tools/render.py`.

## Open questions before building structured output

1. Meaning of the numeric labels next to rooms (m² vs. cm dimensions).
2. Which decision attributes matter (rooms, total m², floor, direction, price…).
3. Whether an official price list / apartment table exists for clean tabular data.
