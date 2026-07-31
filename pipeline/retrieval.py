"""RAG retrieval — pull the relevant slices of the knowledge base before generating.

At course scale no vector DB is needed (per Class 5): the docs fit in context, so
retrieval is "load the specific rows/sections this item needs." Every call returns the
query and the exact chunks used, so the pipeline can log query -> chunk -> output.
"""
from __future__ import annotations

from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "kb"


def _rules_row(key: str) -> str:
    """The raw markdown table row from rules.md whose first cell == key."""
    for line in (KB / "rules.md").read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("|"):
            first = s.strip("|").split("|")[0].strip().lower()
            if first == key.lower():
                return s
    return ""


def _section(md_file: str, title: str) -> str:
    """The markdown section whose heading contains `title`, up to the next same/higher heading."""
    lines = (KB / md_file).read_text(encoding="utf-8").splitlines()
    out, capture, level = [], False, 99
    for line in lines:
        if line.startswith("#"):
            hlevel = len(line) - len(line.lstrip("#"))
            if title.lower() in line.lower():
                capture, level = True, hlevel
                out.append(line)
                continue
            if capture and hlevel <= level:
                break
        if capture:
            out.append(line)
    return "\n".join(out).strip()


def retrieve(kind: str, key):
    """Return (query, chunks) where chunks is a list of (source_label, text)."""
    tone = _section("setting.md", "Tone bible")
    if kind in ("unit", "terrain"):
        q = f"{kind} codex entry for '{key}' — need its stats and the field-manual voice"
        chunks = [("kb/rules.md", _rules_row(key)),
                  ("kb/setting.md :: Tone bible", tone)]
    elif kind == "result":
        outcome, faction = key["outcome"], key["faction"]
        q = (f"result-screen line for a '{outcome}' outcome in the {faction} voice — "
             f"need the outcome trigger, the faction voice, and the tone bible")
        fac_title = "Faction A" if faction == "Directorate" else "Faction B"
        chunks = [("kb/rules.md", _rules_row(outcome)),
                  (f"kb/setting.md :: {fac_title}", _section("setting.md", fac_title)),
                  ("kb/setting.md :: Tone bible", tone)]
    else:
        raise ValueError(f"unknown kind {kind}")
    return q, chunks
