"""Parse kb/rules.md into structured ground truth.

The knowledge base is the single source of truth: the RAG step retrieves raw rows from
rules.md, and the critic checks generated content against the SAME file parsed here. If
the two ever disagree, the doc wins.
"""
from __future__ import annotations

from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "kb"


def _parse_tables(md_text: str):
    """Return a list of (headers, rows) for every markdown table in the text."""
    tables = []
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        sep_ok = (i + 1 < len(lines)
                  and set(lines[i + 1].strip()) <= set("|-: ")
                  and "-" in lines[i + 1])
        if line.startswith("|") and sep_ok:
            headers = [c.strip() for c in line.strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
                j += 1
            tables.append((headers, rows))
            i = j
        else:
            i += 1
    return tables


def load_rules(kb_dir: Path = KB) -> dict:
    md = (kb_dir / "rules.md").read_text(encoding="utf-8")
    units, terrain, outcomes = {}, {}, {}
    for headers, rows in _parse_tables(md):
        if "Unit" in headers and "HP" in headers:
            for r in rows:
                units[r["Unit"].lower()] = {
                    "hp": int(r["HP"]), "move": int(r["Move"]), "atk": int(r["Atk"]),
                    "def": int(r["Def"]), "range": r["Range"], "cost": int(r["Cost"]),
                    "captures": r["Captures"].lower() == "yes",
                }
        elif "Terrain" in headers and "MoveCost" in headers:
            for r in rows:
                terrain[r["Terrain"].lower()] = {
                    "move": r["MoveCost"], "defense": int(r["Defense"]),
                    "passable": sorted(p.strip() for p in r["Passable"].split(",")),
                    "capturable": r["Capturable"].lower() == "yes",
                }
        elif "Outcome" in headers and "Trigger" in headers:
            for r in rows:
                outcomes[r["Outcome"].lower()] = {
                    "trigger": r["Trigger"],
                    "keywords": [k.strip().lower() for k in r["Keywords"].split(",")],
                }
    return {"units": units, "terrain": terrain, "outcomes": outcomes}
