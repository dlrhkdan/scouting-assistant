# Scouting Assistant — U24 Full-backs, K League 1 & 2

Personal scouting assistant that runs inside Claude Code. No web app, no external API.
Reply to the user in Korean.

## Core rules

1. **scout.py does all calculations** (compare, filter, rank, per-90). Never invent,
   estimate, or mentally compute numbers. Always run `python3 scout.py ...` and quote its output.
   If scout.py can't answer a question, say so and propose a change to scout.py.
2. **Python standard library only** (`csv`, `argparse`, etc.). No pip installs, no pandas.
   Run with system `python3`; do not rely on `.venv/`.
3. **Always label the league.** Every player in output shows `K1` or `K2`.
   Never mix K League 1 and K League 2 in one ranking silently — rank them separately
   by default, and if they are combined on request, keep the league column visible and say so.
4. **Small sample.** Players with `league_minutes` below the threshold (default 600,
   `--min-minutes`) are flagged `small sample` and excluded from rankings unless asked
   (`--include-small`). Blank `league_minutes` counts as small sample (minutes unknown).
5. **Primary position** = first entry in `position` (e.g. `CB/LB` → primary `CB`).
   - Specialists only: primary is LB, RB, LWB or RWB (`--specialists`).
   - Include converted players: any FB role anywhere in `position` (default).
   Converted players are marked as such in output.
6. **Identify players by name + team** (e.g. `"Lee Sang-Min @ Suwon Samsung Bluewings"`),
   because names repeat across clubs. If a lookup is ambiguous, ask — don't guess.
7. **Storage.** Watchlist notes: one file per player in `watchlist/`, each entry dated.
   Reports: `reports/`.
8. **Keep the project small.** Explain the plan before writing code.

## scout.py usage

```
python3 scout.py list    [filters]
python3 scout.py rank    --by <metric> [filters] [--top N] [--combine]
python3 scout.py compare "Name@Team" "Name@Team" ... [filters]
python3 scout.py show    "Name@Team"
python3 scout.py note    "Name@Team" "text" [--date YYYY-MM-DD]
python3 scout.py metrics
```
Filters: `--league K1|K2|all`, `--min-minutes 600`, `--include-small`, `--specialists`,
`--side L|R`, `--max-age N`, `--save` (writes to reports/).
No composite score: rankings use one metric at a time. U24 means age 24 and under.
Slash commands: `/compare`, `/report`, `/note` (in `.claude/commands/`).

## Verification

After changing scout.py, run `python3 tests/check_per90.py` (recomputes per-90 values from
the CSV without importing scout.py; exits 1 on any mismatch). Record verification cases in
`docs/verification.md`, with actual results copied from command output only.

## Data notes (data/players.csv)

- Source: FotMob, `as_of_date` per row. Counting stats are season totals; per-90 values
  are computed by scout.py from `league_minutes`.
- 4 rows have blank `league_minutes` (stats are from other competitions or missing) —
  never mix those stats into league comparisons.
- `duels_won_pct` (overall) and `ground_duels_won_pct` are different metrics. Never compare
  one against the other.
- Percentages on tiny samples (e.g. 2/2 crosses = 100%) are unreliable; show the raw count
  next to the percentage.
- `rating_*` columns are empty: reserved for the user's own ratings. Do not fill them.
- The `notes` column holds verification flags ("to verify", loans, contract ends).
  Surface relevant notes in reports; do not treat them as confirmed facts.
