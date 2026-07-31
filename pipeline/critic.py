"""Consistency Critic — deterministic, no LLM required.

Rule adherence is the core check and it is pure code: a generated entry's stats/costs/
capturer/passability/outcome are compared against the parsed knowledge base. Because it
is deterministic it cannot hallucinate a pass — it is the A#4 analog of A#3's real
compiler gate. A light voice heuristic (length cap + banned melodrama words) enforces the
tone bible; deeper voice judgment is the human/LLM report (see README).
"""
from __future__ import annotations

import re

BANNED = ["destiny", "glory", "honor", "legend", "forever", "epic",
          "heroic", "sacred", "doom"]
# a positive claim of capturing ground (used to catch a non-capturer bragging about it)
CAPTURE_CLAIM = re.compile(r"\b(capture|captures|capturing|seize|seizes|seizing)\b", re.I)


def _voice(text: str, max_words: int) -> list[str]:
    v = []
    wc = len(text.split())
    if wc > max_words:
        v.append(f"voice: {wc} words > cap {max_words}")
    for b in BANNED:
        if re.search(r"\b" + b + r"\b", text, re.I):
            v.append(f"voice: banned melodrama word '{b}'")
    return v


def check_unit(entry: dict, rules: dict) -> list[str]:
    v = []
    name = entry["unit"].lower()
    if name not in rules["units"]:
        return [f"rule: '{entry['unit']}' is not a real unit"]
    u = rules["units"][name]
    if int(entry["cost"]) != u["cost"]:
        v.append(f"rule: {entry['unit']} cost {entry['cost']} != {u['cost']}")
    for stat in ("hp", "atk", "def"):
        if stat in entry and int(entry[stat]) != u[stat]:
            v.append(f"rule: {entry['unit']} {stat} {entry[stat]} != {u[stat]}")
    if bool(entry.get("captures", False)) != u["captures"]:
        v.append(f"rule: {entry['unit']} captures={entry.get('captures')} "
                 f"!= {u['captures']} (only Infantry captures)")
    if not u["captures"] and CAPTURE_CLAIM.search(entry["blurb"]):
        v.append(f"rule: {entry['unit']} blurb claims capture, but only Infantry captures")
    v += _voice(entry["blurb"], 40)
    return v


def check_terrain(entry: dict, rules: dict) -> list[str]:
    v = []
    name = entry["terrain"].lower()
    if name not in rules["terrain"]:
        return [f"rule: '{entry['terrain']}' is not a real terrain"]
    t = rules["terrain"][name]
    if int(entry["defense"]) != t["defense"]:
        v.append(f"rule: {entry['terrain']} defense {entry['defense']} != {t['defense']}")
    if str(entry["move"]) != str(t["move"]):
        v.append(f"rule: {entry['terrain']} move {entry['move']} != {t['move']}")
    if "passable" in entry and sorted(entry["passable"]) != t["passable"]:
        v.append(f"rule: {entry['terrain']} passable {sorted(entry['passable'])} != {t['passable']}")
    v += _voice(entry["blurb"], 40)
    return v


def check_result(entry: dict, rules: dict) -> list[str]:
    v = []
    out = entry["outcome"].lower()
    if out not in rules["outcomes"]:
        return [f"rule: '{entry['outcome']}' is not a defined outcome"]
    kws = rules["outcomes"][out]["keywords"]
    if not any(k in entry["line"].lower() for k in kws):
        v.append(f"rule: {out} line references none of its triggers {kws}")
    v += _voice(entry["line"], 30)
    return v


CHECKERS = {"unit": check_unit, "terrain": check_terrain, "result": check_result}


def critique(kind: str, entry: dict, rules: dict) -> list[str]:
    return CHECKERS[kind](entry, rules)
