#!/usr/bin/env python3
"""Embed the latest ranking into the static app as app/data.js (works via file://)."""
import json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ranking = json.loads((ROOT / "data/parsed/ranking.json").read_text())
apartments = json.loads((ROOT / "data/parsed/apartments.json").read_text())

free = [a for a in apartments if a.get("tier") == "free_market"]
payload = {
    "generated": datetime.date.today().isoformat(),
    "project": "מגרש 201 — סירקין, פתח תקווה — מחיר מטרה (רם אדרת + רובי קפיטל)",
    "ranked": ranking,                         # 84 subsidized, ranked
    "free_market_count": len(free),
    "meta": {
        "base_ppm": 15022, "vat": 0.18, "indexation": 1.06,
        "discount": "מובנית בחוזה (≈8–12% של מחיר הבסיס; הטבת מחיר מטרה)",
        "lockin": "מכירה חופשית מ~2030 (המוקדם מבין: 7 שנים מהזכייה / 5 שנים מטופס 4)",
    },
}
out = ROOT / "app/data.js"
out.parent.mkdir(exist_ok=True)
data_js = "window.APP_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n"
out.write_text(data_js)
print(f"wrote {out} ({len(ranking)} ranked apartments)")

# Also emit a fully self-contained single file (data inlined) for easy hosting/sharing:
# works via file://, GitHub Pages, githack, etc. with no second request.
index = (ROOT / "app/index.html").read_text()
standalone = index.replace('<script src="data.js"></script>',
                           "<script>" + data_js + "</script>")
(ROOT / "app/standalone.html").write_text(standalone)
print(f"wrote {ROOT/'app/standalone.html'} (single self-contained file)")

