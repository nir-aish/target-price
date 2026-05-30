# Surroundings & exposure — plot 201 (our project)

Source: the project map on dira.moch.gov.il (buyer screenshots), validated against web
sources (Aug 2025). **Our project = מגרש 201** — מחיר מטרה, יזם **רם אדרת + רובי קפיטל
(ספיר)**, **105 דירות** (**84 מחיר מטרה + 21 שוק חופשי** ✅ matches our catalog), **3
buildings**. Land payment ₪32.3M + development ₪11.5M; won the tender in **early 2023**.

**Floor count — validated, with a caveat.** The official dira listing and the local
coverage say **"שלושה בניינים בני 8 קומות בצמוד לפארק"** (3 buildings, **8 floors**,
**adjacent to a park**). The developer's own site says **"9 קומות"**, and our drawings run
to floor "9" + roof. Most likely reconciliation: **8 residential floors above ground**
(ground + 1…8 = 9 sellable levels), basements = parking. Confirm with the sales office.

> **Web finding that strengthens the east-aspect thesis:** the developer markets the
> project literally as **"בצמוד לפארק"** (adjacent to a park) and the marketing showcases
> the **NE/SE** facades — independent confirmation that the desirable side opens onto the
> eastern green/open space (see "Combined desirability" below).

## Immediate neighbours (north-up map)

| Direction from 201 | Neighbour | Effect on view |
|---|---|---|
| **East** | **green buffer**, then מגרש 110 — future **8-floor public institution** (חינוך/מוסדות ציבור, use TBD), set back, surrounded by green | **most open aspect**: green foreground + a setback, low-key, landscaped institution. Not a permanent park, but far better than an abutting wall. |
| **South** | מגרש 200 — 8-floor rental bldg (יזם רייסדור, 70 דירות), **abuts us** | blocked view |
| **West** | מגרש 101 — 8-floor public school, abuts us | blocked view |
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

- **Eastern green / מגרש 110 — area-zoning confirmed, plot-level still by screenshot.**
  The statutory plan **410-0671826 "סירקין מזרח"** (deposited 2020, approved 2021) confirms
  the quarter mixes **residential + public buildings & educational institutions (מבני
  ציבור/מוסדות חינוך) + parks/open space**, with **graduated heights**: up to 24 floors on
  the central transit axis, **stepping down to 4–8 floors at the edges** toward the park/
  Nahal Shilo and Kfar Sirkin — and **our plot sits in that low-rise park-edge band** (8
  floors, "בצמוד לפארק"). This is fully consistent with our model that מגרש 110 to the east
  is a **setback ~8-floor public institution beyond a green buffer**, not a high-rise.
  ⚠️ The *specific* plot-110 designation/floors/setback still rests on the buyer's
  project-map screenshot — the public תקנון PDF and tab"a viewers are not machine-readable,
  so this exact plot was not independently re-verified. The east aspect remains the best
  regardless (green foreground + low-key setback institution + the developer's "park" framing).
- **Floor count:** project page says 8 floors; our drawings showed plans to "9" + roof —
  reconcile the numbering (affects which floor is the true top).
- **Per-apartment facing** is still the missing key to apply this per unit — see below.

## What's needed to apply this to each of the 84 units

We have the *direction → desirability* map, and **`exposure_score(facing)` is now wired
into `market_ppm()`** in `tools/rank.py` (multipliers SE 1.10 … NW 0.92). It is gated on a
`STACK_FACING` map keyed by `(building, stack)` that is **currently empty → neutral ×1.0**
for all 84 units, so it does not yet move the ranking.

To activate it we still need **which (building, stack) sits on which corner**. Status of
sources tried (web now on):
- **מפרט מכר / brochure** — *not publicly retrievable.* The dira project page is a JS SPA
  (returns an empty shell); its API is locked (HTTP 473); the developer's project page
  lists no כיוונים/חניה/מחסן and no spec PDF.
- **CAD plans** — the unit-plan drawings *do* carry apartment numbers as vector text
  (**101 / 102 / 105 / 108**, 4 per floor-plate), but (a) the price list has **5 stacks**
  per building vs **4 corners + 1 mid-facade** on the plate, and (b) those numbers don't key
  to price-list stacks 1–5. So a *reliable* stack→corner map can't be derived from the CAD alone.

⇒ **Remaining input:** the buyer's own contract/brochure כיוונים table, **or** a guided
plan-read (we zoom the plate together, you confirm which stack/number is on the green-facing
NE/SE corner). One edit to `STACK_FACING` then flows straight into every score.
