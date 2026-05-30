# Surroundings & exposure — plot 201 (our project)

Source: the project map on dira.moch.gov.il (buyer screenshots). **Our project = מגרש
201** — מחיר מטרה, יזם **רם אדרת**, **105 דירות**, 8 floors. (105 matches our parsed
catalog exactly: 84 subsidized + 21 free-market ✅.)

## Immediate neighbours (north-up map)

| Direction from 201 | Neighbour | Effect on view |
|---|---|---|
| **East** | open **green space / park** | **open view — the good side** |
| **South** | מגרש 200 — 8-floor rental bldg (יזם רייסדור, 70 דירות), abuts us | blocked view |
| **West** | מגרש 101 — 8-floor public school | blocked view |
| **North** | מגרש 104 — 8-floor residential+public (100 דירות) | blocked view |

All neighbours are **~8 floors**, same height as ours — so a unit facing a neighbour
is **blocked at essentially every floor** (you don't clear them). View is therefore
driven mainly by **direction**, not floor. Only the **east** side looks onto open space.

## Two factors the buyer wants scored

1. **Sun / orientation** (Israel, N. hemisphere): **South best**, SE/SW good, East =
   morning sun, West = afternoon (hot), **North worst**. (Buyer's intuition confirmed.)
2. **View / surroundings**: facing **open space (east green) ≫ facing another building**
   (south 200 / west 101 / north 104).

## Combined desirability by facade (building is rotated ~26°, corners ≈ NE/SE/SW/NW)

| Corner facing | Sun | View | Verdict |
|---|---|---|---|
| **SE** (toward green + south) | high | **open (green)** | **BEST — sun + open view** |
| **NE** (toward green + north) | morning | **open (green)** | **very good — open view** |
| SW (toward 200/101) | afternoon | blocked (buildings) | weak |
| NW (toward 104/101) | low | blocked (buildings) | **worst** |

**Corroboration:** the marketing 3D renders are captioned **"מבט מכוון צפון מזרח" (NE)**
and **"מבט מכוון דרום מזרח" (SE)** — the developer showcases exactly the **east-facing
facades onto the green**. The nice side faces the park.

## Strategic takeaway

→ **Prioritise NE/SE-facing units (the eastern side onto the green space).** They get the
open view *and* sun, and are the developer's showcase facades. SW/NW units (facing the
school and the rental building) are the weakest regardless of floor.

## Open questions (confirm before finalising)

- **Is the eastern green permanent?** If מגרש 110 (further east) becomes a tall building,
  the open-view premium for east units shrinks. Worth checking its zoning.
- **Floor count:** project page says 8 floors; our drawings showed plans to "9" + roof —
  reconcile the numbering (affects which floor is the true top).
- **Per-apartment facing** is still the missing key to apply this per unit — see below.

## What's needed to apply this to each of the 84 units

We have the *direction → desirability* map; we still need **which apartment number sits
on which corner**. Best source: the **מפרט מכר / brochure** (usually lists each unit's
כיוונים) — fetchable now that web access is on. Then `exposure_score(facing)` in
`tools/rank.py` plugs straight into the ranking.
