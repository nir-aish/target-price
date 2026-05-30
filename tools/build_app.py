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
    "project": "סירקין (Sirkin) — מחיר למשתכן",
    "ranked": ranking,                         # 84 subsidized, ranked
    "free_market_count": len(free),
    "meta": {
        "base_ppm": 15022, "vat": 0.18, "indexation": 1.06,
        "discount": "20% עד 300,000 ₪",
    },
}
out = ROOT / "app/data.js"
out.parent.mkdir(exist_ok=True)
out.write_text("window.APP_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n")
print(f"wrote {out} ({len(ranking)} ranked apartments)")
