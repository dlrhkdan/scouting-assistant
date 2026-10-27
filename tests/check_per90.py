#!/usr/bin/env python3
"""Check scout.py's per-90 successful passes against values computed straight from the CSV.

Scope: U23 left full-back specialists with 600+ league minutes, K1 and K2.
Does not import scout.py: the filter and the per-90 math are re-done here independently,
and scout.py is only run as a command so its printed table can be compared.

Run: python3 tests/check_per90.py
"""
import csv
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "data", "players.csv")
FB_ROLES = {"LB", "RB", "LWB", "RWB"}
MAX_AGE, MIN_MINUTES = 23, 600
LEAGUES = {"K League 1": "K1", "K League 2": "K2"}
CMD = ["python3", "scout.py", "rank", "--by", "passes", "--side", "L",
       "--max-age", str(MAX_AGE), "--specialists"]


def expected_from_csv():
    """{(league, 'Name @ Team'): (minutes, passes, per90 rounded to 2)} from the raw CSV."""
    out = {}
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            roles = [x.strip() for x in r["position"].split("/")]
            if roles[0] not in FB_ROLES:  # specialists: primary position is a FB role
                continue
            if not any(x in FB_ROLES and x.startswith("L") for x in roles):
                continue
            if not r["age"].strip() or int(r["age"]) > MAX_AGE:
                continue
            if not r["league_minutes"].strip():  # blank minutes = small sample
                continue
            minutes = float(r["league_minutes"])
            if minutes < MIN_MINUTES or not r["successful_passes"].strip():
                continue
            passes = float(r["successful_passes"])
            key = (LEAGUES[r["league"]], f"{r['name']} @ {r['team']}")
            out[key] = (minutes, passes, round(passes * 90 / minutes, 2))
    return out


def actual_from_scout():
    """{(league, 'Name @ Team'): per90} parsed from scout.py's printed ranking tables."""
    res = subprocess.run(CMD, cwd=ROOT, capture_output=True, text=True, check=True)
    out = {}
    for line in res.stdout.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # ranking rows: # | Player | Lg | Pos | Type | League min | value | Flag
        if len(cells) == 8 and cells[0].isdigit():
            out[(cells[2], cells[1])] = float(cells[6])
    return out


def main():
    expected, actual = expected_from_csv(), actual_from_scout()
    print("$ " + " ".join(CMD))
    print(f"Filter: primary LB/RB/LWB/RWB, any L role, age <= {MAX_AGE}, league min >= {MIN_MINUTES}\n")
    print("| Lg | Player | League min | Successful passes (CSV) | CSV per90 | scout.py | Match |")
    print("|---|---|---|---|---|---|---|")
    failures = 0
    for key in sorted(set(expected) | set(actual)):
        lg, pid = key
        if key not in actual:
            m, p, v = expected[key]
            print(f"| {lg} | {pid} | {m:.0f} | {p:.0f} | {v:.2f} | missing | FAIL |")
        elif key not in expected:
            print(f"| {lg} | {pid} | - | - | - | {actual[key]:.2f} | FAIL (not in CSV filter) |")
        else:
            m, p, v = expected[key]
            ok = abs(v - actual[key]) < 0.005
            print(f"| {lg} | {pid} | {m:.0f} | {p:.0f} | {v:.2f} | {actual[key]:.2f} | {'OK' if ok else 'FAIL'} |")
            if ok:
                continue
        failures += 1
    total = len(set(expected) | set(actual))
    print(f"\n{total - failures}/{total} match" + ("" if failures else " - PASS"))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
