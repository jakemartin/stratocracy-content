#!/usr/bin/env python3
"""Stratocracy Dynamic Content Pipeline (Assignment #4).

    python run.py

Pure standard library — no API key, no third-party packages, no network. For each content
item it: RETRIEVES the relevant knowledge-base slices, GENERATES a draft (LLM-authored up
front, see pipeline/generate.py), and CRITIQUES it against the parsed rules; on a failure it
logs the violation and regenerates from the corrected draft. Emits three JSON files plus a
full run log (out/) that shows every query -> retrieved chunk -> output and the caught break.
"""
from __future__ import annotations

import json
from pathlib import Path

from pipeline import retrieval, critic, generate
from pipeline.rules import load_rules

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
_log: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    _log.append(msg)


def _key_label(kind, key):
    return key if kind != "result" else f"{key['outcome']}/{key['faction']}"


def produce(kind, key, rules) -> dict:
    """Retrieve -> generate -> critique -> (regenerate on failure). Return the passing entry."""
    query, chunks = retrieval.retrieve(kind, key)
    log(f"\n--- {kind}: {_key_label(kind, key)} ---")
    log(f"  QUERY:    {query}")
    for src, text in chunks:
        first = text.splitlines()[0] if text else "(empty)"
        log(f"  RETRIEVED [{src}]: {first}")

    candidates = generate.drafts(kind, key)
    for attempt, entry in enumerate(candidates):
        violations = critic.critique(kind, entry, rules)
        if not violations:
            log(f"  CRITIC:   PASS (draft {attempt})")
            log(f"  OUTPUT:   {json.dumps(entry, ensure_ascii=False)}")
            return entry
        log(f"  CRITIC:   BLOCK (draft {attempt}) — " + "; ".join(violations))
        if attempt + 1 < len(candidates):
            log(f"  ACTION:   regenerate from corrected draft {attempt + 1}")
    # ran out of drafts without a pass — emit the last with a warning (never silently ship)
    log("  CRITIC:   STILL FAILING after all drafts — flagged, not shipped clean")
    return {**candidates[-1], "_critic": "FAILED", "_violations": violations}


def main() -> int:
    rules = load_rules()
    log("Stratocracy Dynamic Content Pipeline — RAG generate + deterministic critic")
    log(f"Knowledge base: kb/rules.md ({len(rules['units'])} units, "
        f"{len(rules['terrain'])} terrains, {len(rules['outcomes'])} outcomes) + kb/setting.md")

    units = [produce("unit", u, rules) for u in ("infantry", "tank", "artillery", "recon")]
    terrain = [produce("terrain", t, rules)
               for t in ("plains", "woods", "mountains", "water", "town")]
    results = [produce("result", {"outcome": o, "faction": f}, rules)
               for o in ("decisive", "marginal", "draw", "defeat")
               for f in ("Directorate", "Vanguard")]

    (OUT / "unit_codex.json").write_text(json.dumps(units, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "terrain_codex.json").write_text(json.dumps(terrain, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "result_screen.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    blocked = sum(1 for line in _log if "CRITIC:   BLOCK" in line)
    log(f"\nDone. {len(units)} units, {len(terrain)} terrains, {len(results)} result lines emitted.")
    log(f"Critic caught and corrected {blocked} consistency break(s) during the run.")
    log("Outputs in out/: unit_codex.json, terrain_codex.json, result_screen.json")

    (OUT / "run_log.md").write_text(
        "# Content pipeline — run log\n\n```\n" + "\n".join(_log) + "\n```\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
