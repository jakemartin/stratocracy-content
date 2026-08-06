"""The Generator — grounded content authored by an LLM (Claude, via Cowork).

Design choice (lean, no runtime model): the generation was done by an LLM up front,
reading the knowledge base, and the results are stored here. The pipeline still exercises
the full loop at runtime — retrieve, generate (draw a draft), critique, and regenerate on
failure — so the consistency check is real, runnable, and dependency-free.

To DEMONSTRATE the critic catching and correcting a break, the Tank codex entry ships two
drafts: draft 0 is deliberately wrong (claims Tank captures ground and misprices it), and
draft 1 is the corrected version. Every other item has a single, correct draft. The runner
tries drafts in order and keeps the first that passes the critic — exactly like the A#3
crew's block-then-fix loop, but for content.
"""
from __future__ import annotations

# --- Unit codex (neutral field-manual voice) --------------------------------------
_UNITS = {
    "infantry": [dict(
        unit="Infantry", role="Line holder — the only unit that takes ground.",
        cost=100, hp=10, atk=4, **{"def": 2}, captures=True,
        blurb=("Cheap boots that move slow. The only unit that can plant a flag on a "
               "town or factory, so screen it with armor and let Recon find the lane."))],
    "tank": [
        # draft 0 — DELIBERATELY BROKEN (wrong cost; claims it captures)
        dict(unit="Tank", role="Line breaker.",
             cost=250, hp=20, atk=8, **{"def": 5}, captures=True,
             blurb=("The hammer — heavy enough to seize towns and factories outright as "
                    "it rolls through the line.")),
        # draft 1 — corrected
        dict(unit="Tank", role="Line breaker.",
             cost=300, hp=20, atk=8, **{"def": 5}, captures=False,
             blurb=("The hammer — soaks hits and punches holes. Your flag rides in a Tank "
                    "variant, so losing it ends the match. Objectives are the infantry's "
                    "job, not the Tank's.")),
    ],
    "artillery": [dict(
        unit="Artillery", role="Standoff gun.",
        cost=200, hp=8, atk=10, **{"def": 1}, captures=False,
        blurb=("Glass with reach. Fires two to three hexes out and takes no reply at that "
               "range. Caught adjacent it dies fast — keep it behind the line."))],
    "recon": [dict(
        unit="Recon", role="Fast eyes.",
        cost=150, hp=12, atk=5, **{"def": 3}, captures=False,
        blurb=("Fast eyes. Outruns everything and ignores the worst terrain cost. Thin "
               "armor, light punch — it finds the fight and screens the flank."))],
}

# --- Terrain codex (neutral field-manual voice) -----------------------------------
_TERRAIN = {
    "plains": [dict(terrain="Plains", move=1, defense=0, passable=["land", "air"],
                    blurb=("Open ground. One move to cross and nothing to hide behind — "
                           "every hit lands clean, for you and against you."))],
    "woods": [dict(terrain="Woods", move=2, defense=20, passable=["land", "air"],
                   blurb=("Cover at a price. Two move to enter, but anything standing in "
                          "it is twenty percent harder to kill."))],
    "mountains": [dict(terrain="Mountains", move=3, defense=40, passable=["land", "air"],
                       blurb=("The wall. Three move to climb and forty percent defense at "
                              "the top — slow ground you pay to hold."))],
    "water": [dict(terrain="Water", move="-", defense=0, passable=["air", "sea"],
                   blurb=("A moat. Land units cannot cross it; only sea and air move "
                          "through. Use it to anchor a flank."))],
    "town": [dict(terrain="Town", move=1, defense=10, passable=["land", "air"],
                  blurb=("Held ground. Light cover, and the one tile infantry can take "
                         "for a small stream of Fame."))],
}

# --- Result-screen text (faction-flavored) ----------------------------------------
_RESULTS = {
    ("decisive", "Directorate"): [dict(outcome="decisive", faction="Directorate",
        line="Enemy flag destroyed. Order is restored. The Directorate endures.")],
    ("decisive", "Vanguard"): [dict(outcome="decisive", faction="Vanguard",
        line="Their flag is down. We didn't ask permission — we took the field.")],
    ("marginal", "Directorate"): [dict(outcome="marginal", faction="Directorate",
        line="No flag fell, but the cap ledger favors us. A win by attrition is a win.")],
    ("marginal", "Vanguard"): [dict(outcome="marginal", faction="Vanguard",
        line="Nobody's flag fell. We bled them harder by the cap. Mark it a win.")],
    ("draw", "Directorate"): [dict(outcome="draw", faction="Directorate",
        line="The line held on both sides. Record it a draw. Regroup and re-task.")],
    ("draw", "Vanguard"): [dict(outcome="draw", faction="Vanguard",
        line="Nobody broke. Call it a draw. We settle it next time.")],
    ("defeat", "Directorate"): [dict(outcome="defeat", faction="Directorate",
        line="Our flag has fallen. The Directorate does not dwell on it. Withdraw and re-form.")],
    ("defeat", "Vanguard"): [dict(outcome="defeat", faction="Vanguard",
        line="Flag's gone. We scatter, we regroup, we come back.")],
}


def drafts(kind: str, key):
    """Return the ordered list of candidate drafts for one content item."""
    if kind == "unit":
        return _UNITS[key.lower()]
    if kind == "terrain":
        return _TERRAIN[key.lower()]
    if kind == "result":
        return _RESULTS[(key["outcome"], key["faction"])]
    raise ValueError(kind)
