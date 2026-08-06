# Content pipeline — run log

```
Stratocracy Dynamic Content Pipeline — RAG generate + deterministic critic
Knowledge base: kb/rules.md (4 units, 7 terrains, 4 outcomes) + kb/setting.md

--- unit: infantry ---
  QUERY:    unit codex entry for 'infantry' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Infantry | 10 | 3 | 4 | 2 | 1 | 100 | yes |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"unit": "Infantry", "role": "Line holder — the only unit that takes ground.", "cost": 100, "hp": 10, "atk": 4, "def": 2, "captures": true, "blurb": "Cheap boots that move slow. The only unit that can plant a flag on a town or factory, so screen it with armor and let Recon find the lane."}

--- unit: tank ---
  QUERY:    unit codex entry for 'tank' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Tank | 20 | 5 | 8 | 5 | 1 | 300 | no |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   BLOCK (draft 0) — rule: Tank cost 250 != 300; rule: Tank captures=True != False (only Infantry captures); rule: Tank blurb claims capture, but only Infantry captures
  ACTION:   regenerate from corrected draft 1
  CRITIC:   PASS (draft 1)
  OUTPUT:   {"unit": "Tank", "role": "Line breaker.", "cost": 300, "hp": 20, "atk": 8, "def": 5, "captures": false, "blurb": "The hammer — soaks hits and punches holes. Your flag rides in a Tank variant, so losing it ends the match. Objectives are the infantry's job, not the Tank's."}

--- unit: artillery ---
  QUERY:    unit codex entry for 'artillery' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Artillery | 8 | 3 | 10 | 1 | 2-3 | 200 | no |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"unit": "Artillery", "role": "Standoff gun.", "cost": 200, "hp": 8, "atk": 10, "def": 1, "captures": false, "blurb": "Glass with reach. Fires two to three hexes out and takes no reply at that range. Caught adjacent it dies fast — keep it behind the line."}

--- unit: recon ---
  QUERY:    unit codex entry for 'recon' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Recon | 12 | 7 | 5 | 3 | 1 | 150 | no |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"unit": "Recon", "role": "Fast eyes.", "cost": 150, "hp": 12, "atk": 5, "def": 3, "captures": false, "blurb": "Fast eyes. Outruns everything and ignores the worst terrain cost. Thin armor, light punch — it finds the fight and screens the flank."}

--- terrain: plains ---
  QUERY:    terrain codex entry for 'plains' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Plains | 1 | 0 | land,air | no |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"terrain": "Plains", "move": 1, "defense": 0, "passable": ["land", "air"], "capturable": false, "blurb": "Open ground. One move to cross and nothing to hide behind — every hit lands clean, for you and against you."}

--- terrain: woods ---
  QUERY:    terrain codex entry for 'woods' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Woods | 2 | +20 | land,air | no |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"terrain": "Woods", "move": 2, "defense": 20, "passable": ["land", "air"], "capturable": false, "blurb": "Cover at a price. Two move to enter, but anything standing in it is twenty percent harder to kill."}

--- terrain: mountains ---
  QUERY:    terrain codex entry for 'mountains' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Mountains | 3 | +40 | land (slow),air | no |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   BLOCK (draft 0) — rule: Mountains passable ['air', 'land'] != ['air', 'land (slow)']
  ACTION:   regenerate from corrected draft 1
  CRITIC:   PASS (draft 1)
  OUTPUT:   {"terrain": "Mountains", "move": 3, "defense": 40, "passable": ["land (slow)", "air"], "capturable": false, "blurb": "The wall. Three move to climb and forty percent defense at the top. Land units grind across it — slow ground you pay to hold."}

--- terrain: water ---
  QUERY:    terrain codex entry for 'water' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Water | - | 0 | sea,air | no |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"terrain": "Water", "move": "-", "defense": 0, "passable": ["air", "sea"], "capturable": false, "blurb": "A moat. Land units cannot cross it; only sea and air move through. Use it to anchor a flank."}

--- terrain: town ---
  QUERY:    terrain codex entry for 'town' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Town | 1 | +10 | land,air | yes |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"terrain": "Town", "move": 1, "defense": 10, "passable": ["land", "air"], "capturable": true, "blurb": "Held ground. Light cover, and the one tile infantry can take for a small stream of Fame."}

--- terrain: bridge ---
  QUERY:    terrain codex entry for 'bridge' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Bridge | 1 | -10 | land,air | no |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"terrain": "Bridge", "move": 1, "defense": -10, "passable": ["land", "air"], "capturable": false, "blurb": "The only hex armor crosses Water on. One move, and ten percent off your defense while you stand on it. Contest it, do not park on it."}

--- terrain: factory ---
  QUERY:    terrain codex entry for 'factory' — need its stats and the field-manual voice
  RETRIEVED [kb/rules.md]: | Factory | 1 | +15 | land,air | yes |
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"terrain": "Factory", "move": 1, "defense": 15, "passable": ["land", "air"], "capturable": true, "blurb": "Builds units and repairs them. Fifteen percent cover, and infantry can take it — hold one and it pays a hundred Fame a turn."}

--- result: decisive/Directorate ---
  QUERY:    result-screen line for a 'decisive' outcome in the Directorate voice — need the outcome trigger, the faction voice, and the tone bible
  RETRIEVED [kb/rules.md]: | decisive | enemy flag unit destroyed | flag |
  RETRIEVED [kb/setting.md :: Faction A]: ## Faction A — The Directorate
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"outcome": "decisive", "faction": "Directorate", "line": "Enemy flag destroyed. Order is restored. The Directorate endures."}

--- result: decisive/Vanguard ---
  QUERY:    result-screen line for a 'decisive' outcome in the Vanguard voice — need the outcome trigger, the faction voice, and the tone bible
  RETRIEVED [kb/rules.md]: | decisive | enemy flag unit destroyed | flag |
  RETRIEVED [kb/setting.md :: Faction B]: ## Faction B — The Vanguard
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"outcome": "decisive", "faction": "Vanguard", "line": "Their flag is down. We didn't ask permission — we took the field."}

--- result: marginal/Directorate ---
  QUERY:    result-screen line for a 'marginal' outcome in the Directorate voice — need the outcome trigger, the faction voice, and the tone bible
  RETRIEVED [kb/rules.md]: | marginal | led the attrition tiebreak at the turn cap without a flag kill | cap, attrition, tiebreak |
  RETRIEVED [kb/setting.md :: Faction A]: ## Faction A — The Directorate
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"outcome": "marginal", "faction": "Directorate", "line": "No flag fell, but the cap ledger favors us. A win by attrition is a win."}

--- result: marginal/Vanguard ---
  QUERY:    result-screen line for a 'marginal' outcome in the Vanguard voice — need the outcome trigger, the faction voice, and the tone bible
  RETRIEVED [kb/rules.md]: | marginal | led the attrition tiebreak at the turn cap without a flag kill | cap, attrition, tiebreak |
  RETRIEVED [kb/setting.md :: Faction B]: ## Faction B — The Vanguard
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"outcome": "marginal", "faction": "Vanguard", "line": "Nobody's flag fell. We bled them harder by the cap. Mark it a win."}

--- result: draw/Directorate ---
  QUERY:    result-screen line for a 'draw' outcome in the Directorate voice — need the outcome trigger, the faction voice, and the tone bible
  RETRIEVED [kb/rules.md]: | draw | cap resolved to a tie, or mutual passivity (both sides zero combat Fame) | draw, tie, stalemate |
  RETRIEVED [kb/setting.md :: Faction A]: ## Faction A — The Directorate
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"outcome": "draw", "faction": "Directorate", "line": "The line held on both sides. Record it a draw. Regroup and re-task."}

--- result: draw/Vanguard ---
  QUERY:    result-screen line for a 'draw' outcome in the Vanguard voice — need the outcome trigger, the faction voice, and the tone bible
  RETRIEVED [kb/rules.md]: | draw | cap resolved to a tie, or mutual passivity (both sides zero combat Fame) | draw, tie, stalemate |
  RETRIEVED [kb/setting.md :: Faction B]: ## Faction B — The Vanguard
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"outcome": "draw", "faction": "Vanguard", "line": "Nobody broke. Call it a draw. We settle it next time."}

--- result: defeat/Directorate ---
  QUERY:    result-screen line for a 'defeat' outcome in the Directorate voice — need the outcome trigger, the faction voice, and the tone bible
  RETRIEVED [kb/rules.md]: | defeat | your own flag unit destroyed, or the enemy dominates all factories | flag, domination |
  RETRIEVED [kb/setting.md :: Faction A]: ## Faction A — The Directorate
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"outcome": "defeat", "faction": "Directorate", "line": "Our flag has fallen. The Directorate does not dwell on it. Withdraw and re-form."}

--- result: defeat/Vanguard ---
  QUERY:    result-screen line for a 'defeat' outcome in the Vanguard voice — need the outcome trigger, the faction voice, and the tone bible
  RETRIEVED [kb/rules.md]: | defeat | your own flag unit destroyed, or the enemy dominates all factories | flag, domination |
  RETRIEVED [kb/setting.md :: Faction B]: ## Faction B — The Vanguard
  RETRIEVED [kb/setting.md :: Tone bible]: ## Tone bible (applies to ALL generated content)
  CRITIC:   PASS (draft 0)
  OUTPUT:   {"outcome": "defeat", "faction": "Vanguard", "line": "Flag's gone. We scatter, we regroup, we come back."}

Done. 4 units, 7 terrains, 8 result lines emitted.
Critic caught and corrected 2 consistency break(s) during the run.
Outputs in out/: unit_codex.json, terrain_codex.json, result_screen.json
```
