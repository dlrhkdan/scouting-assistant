---
description: Build a scouting report from scout.py rankings and save it to reports/
argument-hint: <criteria, e.g. "K2 LB specialists">
---
Make a scouting report for: $ARGUMENTS

1. Turn the criteria into scout.py options (--league, --side, --specialists, --max-age,
   --min-minutes, --include-small). If the criteria are unclear, ask first.
2. Run `python3 scout.py list ... --save` and `python3 scout.py rank --by <metric> ... --save` for the
   metrics that fit the criteria (`python3 scout.py metrics` lists them). Keep K1 and K2 separate.
3. Run `python3 scout.py show "Name@Team"` for the top candidates to pick up data notes and watchlist notes.
4. Write the summary in Korean to `reports/<YYYY-MM-DD>_report_<slug>.md`: criteria, shortlist by league,
   strengths and concerns, small-sample exclusions, and items flagged "to verify" in the notes.
   Use only numbers from scout.py output, and list the commands you ran at the end.
