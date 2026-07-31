# Stratocracy — Rules Knowledge Base (ground truth)

Source of truth extracted from the GDD (§2.3 terrain, §2.4 units, §2.7 economy,
§2.8 victory). The content pipeline retrieves from this file, and the consistency
critic checks every generated line against the tables below. If a number here is
wrong, fix it here — nothing downstream should contradict it.

Values marked **[unpinned]** are open in the GDD (an example or a range, with a
change request filed). Do not generate a specific number for them.

## Units (§2.4)

| Unit | HP | Move | Atk | Def | Range | Cost | Captures |
|---|---|---|---|---|---|---|---|
| Infantry | 10 | 3 | 4 | 2 | 1 | 100 | yes |
| Tank | 20 | 5 | 8 | 5 | 1 | 300 | no |
| Artillery | 8 | 3 | 10 | 1 | 2-3 | 200 | no |
| Recon | 12 | 7 | 5 | 3 | 1 | 150 | no |

Notes: **Only Infantry captures** towns/factories. The **Flag Unit is a Tank variant**
(not producible); its death ends the match. Artillery is the only ranged unit (2-3) and
takes no counter when it strikes from outside melee. §2.4 labels the Recon row
**Recon/Air**; it ignores some terrain cost.

**The triangle is positional, not a counter chart:** Artillery beats Tank (range 2-3, no
melee counter), Recon beats Artillery (move 7 runs it down), Tank beats Recon (wins the
range-1 fight). Infantry sits outside the triangle as the capture unit. The
type-effectiveness multiplier ships **defaulted to 1.0 everywhere**.

## Terrain (§2.3)

Prototype set: **6 movement terrains + the capturable Factory tile.**

| Terrain | MoveCost | Defense | Passable | Capturable |
|---|---|---|---|---|
| Plains | 1 | 0 | land,air | no |
| Woods | 2 | +20 | land,air | no |
| Mountains | 3 | +40 | land (slow),air | no |
| Water | - | 0 | sea,air | no |
| Town | 1 | +10 | land,air | yes |
| Bridge | 1 | -10 | land,air | no |
| Factory | 1 | +15 | land,air | yes |

Notes: Move cost is **per movement class**; Recon ignores some terrain cost. Defense is a
percent bonus to a unit standing on the hex. **Water is not land-passable** (sea/air
only), and **no sea unit ships in the prototype** — so **Bridge is the only hex a land
unit crosses Water on**, making bridges chokepoints. Bridge defense is **negative**
(-10%): a unit caught mid-crossing is exposed, not safe. **Both Town and Factory are
capturable** (by Infantry only). **Factory** is also the build/spawn point and a repair
point (§2.7).

## Economy — Fame (§2.7)

Fame is a **single currency**: production points, combat rewards, and the win-score are
one pool, not three.

- **Starting Fame: 200** per side, plus home-factory income from turn 1.
- Factory held: **+100 Fame/turn**. Town held: **+25 Fame/turn**.
- Build costs equal the unit Cost column above (Infantry 100 / Recon 150 / Artillery 200 / Tank 300).
- **Spawn:** a built unit appears on the factory hex if free, otherwise an adjacent free
  hex; if the factory is boxed in, the build waits.
- Destroying an enemy unit pays **~half its cost** (a Tank kill = +150) **[unpinned:
  exact per-unit award]**; an **undamaged strike** (attacker takes no counter) pays a
  small bonus **[unpinned]**; destroying the enemy **flag pays +500 and ends the match**.
- **Capture:** move an Infantry onto a town/factory and hold to capture over **N turns
  (start N=1-2)**; a captured objective flips its income. **[unpinned: exact N — the
  shipped scenario assumes N=1, but this is an assumption in force, not a rule; also
  unpinned is what happens to progress if the Infantry leaves or dies mid-capture]**
- **Repair:** a unit ending its turn on an **owned Town or Factory** and **not adjacent to
  any enemy** heals **+25% of max HP** (rounded down, min 1, capped at max) at the start of
  its next turn — free. The not-adjacent clause is the anti-fortress lock: a unit must
  break contact to repair. Repairing earns zero combat Fame, so a repair-turtle still
  loses the cap tiebreak.
- **Map layout:** a home factory per side (owned at start) plus **two or more neutral**
  factories; a typical small skirmish map has **~4 factories total**.
- **Difficulty** is a starting-Fame handicap (§2.9), not a stat change.

## Victory & outcomes (§2.8)

| Outcome | Trigger | Keywords |
|---|---|---|
| decisive | enemy flag unit destroyed | flag |
| decisive | **territorial domination** — control every factory on the map at the start of your turn | domination, factories, backstop |
| marginal | led the attrition tiebreak at the turn cap without a flag kill | cap, attrition, tiebreak |
| draw | cap resolved to a tie, or mutual passivity (both sides zero combat Fame) | draw, tie, stalemate |
| defeat | your own flag unit destroyed, or the enemy dominates all factories | flag, domination |

Territorial domination is **factories only** — towns do not count — and it ranks as a
**Decisive** win, equal to a flag kill. It ends the match immediately.

**Turn cap:** **per-scenario data**, stored in the scenario file's `turnCap` field. The
shipped scenario (*Ferrum Crossing*) ships **20 turns**. Do not describe the cap as a
global constant.

**Cap resolution, in order:**

1. **Mutual-passivity guard** — if *both* sides' combat Fame is zero, the match is an
   immediate **draw**. It does not fall through to the keys below.
2. **Lexicographic comparison**, higher wins at the first key that differs:
   **combat Fame earned → objectives held (X of N) → surviving HP.**
3. All three keys equal → **draw**.

**Combat Fame** counts only kills and undamaged-strike bonuses. It **excludes passive
factory and town income** — counting income would restore the turtle exploit. The +500
flag bonus can never appear in a capped tally (a flag kill ends the match).

**Objectives held** counts factories *and* captured towns, by ownership only — a capture
in progress counts for nobody until the objective flips.

Tiers rank **categorically**: a decisive win always outranks a marginal win, regardless
of Fame totals. Combat Fame is the sort key *inside* the tiebreak, never the grade.
