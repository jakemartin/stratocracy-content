# Stratocracy — Dynamic Content Pipeline (Assignment #4)

A RAG content pipeline for **Stratocracy** (UE5.8 hex turn-based strategy). It reads the
game's own docs before writing, generates three content types the game needs, and runs a
**deterministic consistency critic** that catches and corrects contradictions before any
line ships.

**Run it:** `python run.py` — pure standard library. No API key, no third-party packages,
no network. Outputs land in `out/`.

## The gap this fills

Stratocracy is deliberately systems-forward and art-light — it has rules but almost no
written surface text. The three things a player actually reads are missing: **unit and
terrain codex/tooltips** and the **result screen**. This pipeline generates exactly those,
grounded in the real rules so the flavor never fights the mechanics.

## Knowledge base (Game-Anchored Source)

Everything is retrieved from `kb/`, derived straight from the GDD:

- **`kb/rules.md`** — the ground truth: unit table (stats, Fame cost, who captures),
  terrain table (move/defense/passability), and the victory outcomes. This is both the RAG
  source *and* the critic's reference — one source of truth, so flavor can't drift from rules.
- **`kb/setting.md`** — the thin fiction: a tone bible (terse tactical-briefing voice) and
  two factions, **The Directorate** (cold, doctrinal) and **The Vanguard** (terse, defiant),
  used only for result-screen voice.

## The three outputs (in `out/`)

- **`unit_codex.json`** — 4 units: role + field-manual blurb + the real stats.
- **`terrain_codex.json`** — 5 terrains: move + defense + passability + blurb.
- **`result_screen.json`** — 8 lines: Decisive / Marginal / Draw / Defeat × both factions.

## How it works

For each item the pipeline **retrieves** the relevant KB slices, **generates** a draft, and
**critiques** it against the parsed rules; on a failure it regenerates from the corrected
draft. Generation was done up front by an LLM (Claude, via Cowork) reading the KB — the lean,
no-runtime-model choice — while retrieval and the critic run as local deterministic code, so
the consistency loop is real, runnable, and dependency-free. (A live-regeneration model could
be dropped into `pipeline/generate.py` later; it isn't needed to run or grade this.)

### RAG implementation — one full query → chunk → output

```
QUERY:     unit codex entry for 'tank' — need its stats and the field-manual voice
RETRIEVED  [kb/rules.md]            | Tank | 20 | 5 | 8 | 5 | 1 | 300 | no |
RETRIEVED  [kb/setting.md :: Tone bible]
           - Register: terse tactical briefing ...
           - Length: a codex blurb is <= 40 words.
           - Hard rule: never contradict rules.md. No invented units, abilities, costs ...
OUTPUT     { "unit": "Tank", "role": "Line breaker.", "cost": 300, ...,
             "captures": false, "blurb": "The hammer — soaks hits and punches holes.
             Your flag rides in a Tank variant, so losing it ends the match. Objectives
             are the infantry's job, not the Tank's." }
```

The output's stats come straight from the retrieved `rules.md` row; the voice comes from the
retrieved tone bible. Every item's triple is logged in `out/run_log.md`.

### Consistency checking — a break caught and corrected

The critic is deterministic: it compares each generated field against the parsed KB, so it
cannot hallucinate a pass. Draft 0 of the Tank entry was deliberately wrong:

```
DRAFT 0 (as generated):  cost 250, captures: true,
    blurb: "The hammer — heavy enough to seize towns and factories outright ..."

CRITIC:  BLOCK
  - rule: Tank cost 250 != 300
  - rule: Tank captures=True != False (only Infantry captures)
  - rule: Tank blurb claims capture, but only Infantry captures

ACTION:  regenerate from corrected draft

DRAFT 1 (shipped):  cost 300, captures: false,
    blurb: "... Objectives are the infantry's job, not the Tank's."   →  PASS
```

Three real contradictions — a mispriced unit and a rule-breaking ability claim — caught and
corrected automatically before shipping. The full trace is in `out/run_log.md`.

## Voice judgment (self-assessment)

Do the outputs sound like Stratocracy? Yes — terse, tactical, hardware-over-heroics, and the
two factions read distinctly (the Directorate records outcomes as ledger entries; the Vanguard
speaks from the mud). The critic also enforces the tone bible mechanically: a 40-word cap on
blurbs, a 30-word cap on result lines, and a banned list of melodrama words (*glory, destiny,
honor…*) so nothing drifts into generic fantasy.

**Concrete tweak made to improve game-fit:** the first run's retrieval was pulling the *entire*
`setting.md` for the tone chunk, because the file's H1 title also contained the words "Tone
Bible" and the section matcher latched onto it — imprecise grounding. Renaming the H1 to
"Setting and Voice Guide" made retrieval return only the `## Tone bible` section, so each
generation now gets the tight, relevant context instead of the whole document.

## Rebuilding the GDD's derived files

`Stratocracy_Prototype_GDD.md` is the source. The `.txt` and `.pdf` beside it are
derived, and **all three are expected to move together** — after any merge into
the `.md`, run:

```
python build_docs.py          # both;  --txt / --pdf for one;  --check to locate the tools
```

The route is pandoc → standalone HTML → wkhtmltopdf, and `.txt` via `pandoc -t
plain` — the same one every prior revision was built with. Neither tool is
necessarily on `PATH`, so the script searches the known install locations and, on
failure, prints every place it looked. A non-zero exit means a build failed, and
no output file is replaced unless its own build succeeded.

## Layout

```
build_docs.py        rebuilds Stratocracy_Prototype_GDD.txt and .pdf from the .md
kb/rules.md          ground truth (RAG source + critic reference)
kb/setting.md        tone bible + two factions
pipeline/rules.py    parses rules.md into structured data
pipeline/retrieval.py folder-based RAG (returns query + exact chunks)
pipeline/critic.py   deterministic consistency critic (rules) + voice heuristic
pipeline/generate.py LLM-authored content store (incl. the seeded Tank break)
run.py               orchestrator: retrieve → generate → critique → regenerate; writes out/
out/                 unit_codex.json, terrain_codex.json, result_screen.json, run_log.md
```
