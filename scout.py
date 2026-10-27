#!/usr/bin/env python3
"""Scouting assistant for U24 full-backs in K League 1 and 2.

Every number shown to the user comes from this script. Standard library only.

    python3 scout.py list [filters]
    python3 scout.py rank --by tackles [filters] [--top N] [--combine]
    python3 scout.py compare "Name@Team" "Name@Team" ...
    python3 scout.py show "Name@Team"
    python3 scout.py note "Name@Team" "text"
"""
import argparse
import csv
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "players.csv")
WATCHLIST = os.path.join(ROOT, "watchlist")
REPORTS = os.path.join(ROOT, "reports")

FB_ROLES = {"LB", "RB", "LWB", "RWB"}
LEAGUES = {"K League 1": "K1", "K League 2": "K2"}

# key: (label, kind, columns, count column for pct)
# kind: "raw" = value as is, "p90" = sum of columns per 90 league minutes, "pct" = percentage
METRICS = {
    "rating": ("Avg rating", "raw", ["avg_rating"], None),
    "tackles": ("Tackles /90", "p90", ["tackles"], None),
    "interceptions": ("Interceptions /90", "p90", ["interceptions"], None),
    "recoveries": ("Recoveries /90", "p90", ["recoveries"], None),
    "passes": ("Successful passes /90", "p90", ["successful_passes"], None),
    "crosses": ("Successful crosses /90", "p90", ["successful_crosses"], None),
    "ga": ("Goals+assists /90", "p90", ["goals", "assists"], None),
    "pass_acc": ("Pass accuracy", "pct", ["pass_acc_pct"], "successful_passes"),
    "cross_acc": ("Cross accuracy", "pct", ["crosses_acc_pct"], "successful_crosses"),
    "duels": ("Duels won (overall)", "pct", ["duels_won_pct"], None),
    "ground_duels": ("Ground duels won", "pct", ["ground_duels_won_pct"], None),
    "aerial": ("Aerial duels won", "pct", ["aerial_duels_won_pct"], None),
}


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def num(s):
    s = (s or "").strip()
    return float(s) if s else None


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load():
    players = []
    with open(DATA, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            roles = [r.strip() for r in row["position"].split("/") if r.strip()]
            minutes = num(row["league_minutes"])
            row.update(
                id=f"{row['name']} @ {row['team']}",
                lg=LEAGUES.get(row["league"], row["league"]),
                roles=roles,
                primary=roles[0] if roles else "",
                converted=not roles or roles[0] not in FB_ROLES,
                minutes=int(minutes) if minutes is not None else None,
            )
            players.append(row)
    return players


def is_small(p, min_minutes):
    return p["minutes"] is None or p["minutes"] < min_minutes


def sample_flag(p, min_minutes):
    if p["minutes"] is None:
        return "small sample (league minutes unknown)"
    if p["minutes"] < min_minutes:
        return "small sample"
    return ""


def kind_label(p):
    return f"converted ({p['primary']})" if p["converted"] else "specialist"


def apply_filters(players, args):
    out = []
    for p in players:
        if args.league != "all" and p["lg"] != args.league:
            continue
        if args.specialists and p["converted"]:
            continue
        if args.side and not any(r in FB_ROLES and r.startswith(args.side) for r in p["roles"]):
            continue
        if args.max_age is not None and (num(p["age"]) is None or num(p["age"]) > args.max_age):
            continue
        out.append(p)
    return out


def metric_value(p, key):
    """Metric value from league stats, or None. Rows without league minutes have
    stats from other competitions, so they never get a value."""
    _, kind, cols, _ = METRICS[key]
    if p["minutes"] is None:
        return None
    vals = [num(p[c]) for c in cols]
    if any(v is None for v in vals):
        return None
    if kind == "p90":
        return sum(vals) * 90 / p["minutes"] if p["minutes"] > 0 else None
    return vals[0]


def fmt_metric(p, key):
    v = metric_value(p, key)
    if v is None:
        return "-"
    _, kind, _, count_col = METRICS[key]
    if kind != "pct":
        return f"{v:.2f}"
    s = f"{v:.1f}%"
    count = num(p[count_col]) if count_col else None
    if count is not None and v > 0:
        s += f" ({int(count)}/{round(count * 100 / v)})"
    return s


def fmt_value(p):
    v = num(p["market_value_eur"])
    if v is None:
        return "-"
    return f"€{v / 1e6:.2f}M" if v >= 1e6 else f"€{v / 1e3:.0f}K"


def fmt_minutes(p):
    return "unknown" if p["minutes"] is None else str(p["minutes"])


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return lines


def filter_desc(args):
    parts = [f"league={args.league}", f"min minutes={args.min_minutes}"]
    parts.append("specialists only" if args.specialists else "incl. converted")
    if args.side:
        parts.append(f"side={args.side}")
    if args.max_age is not None:
        parts.append(f"max age={args.max_age}")
    if args.include_small:
        parts.append("small samples included")
    return ", ".join(parts)


def resolve(players, query):
    """Find one player from 'Name@Team' or 'Name' (partial, case-insensitive)."""
    name_q, _, team_q = query.partition("@")
    name_q, team_q = norm(name_q), norm(team_q)
    hits = [p for p in players if name_q in norm(p["name"]) and team_q in norm(p["team"])]
    if len(hits) > 1:
        exact = [p for p in hits if norm(p["name"]) == name_q]
        if len(exact) == 1:
            hits = exact
    if not hits:
        die(f"No player matches '{query}'.")
    if len(hits) > 1:
        die(f"'{query}' is ambiguous; use Name@Team:\n" + "\n".join(f"  {p['id']} ({p['lg']})" for p in hits))
    return hits[0]


def cmd_list(players, args):
    ps = apply_filters(players, args)
    ps.sort(key=lambda p: (p["lg"], -(p["minutes"] or -1)))
    lines = [f"## Player list ({filter_desc(args)})", ""]
    for lg in ("K1", "K2"):
        group = [p for p in ps if p["lg"] == lg]
        if not group:
            continue
        rows = [[p["id"], p["lg"], p["position"], kind_label(p), p["age"], fmt_minutes(p),
                 fmt_value(p), sample_flag(p, args.min_minutes)] for p in group]
        lines += [f"### {lg} ({len(group)} players)", ""]
        lines += table(["Player", "Lg", "Pos", "Type", "Age", "League min", "Value", "Flag"], rows)
        lines.append("")
    return lines, f"list_{args.league}"


def cmd_rank(players, args):
    label = METRICS[args.by][0]
    ps = apply_filters(players, args)
    groups = [("K1+K2", ps)] if args.combine else [(lg, [p for p in ps if p["lg"] == lg]) for lg in ("K1", "K2")]
    lines = [f"## Ranking: {label} ({filter_desc(args)})", ""]
    if args.combine:
        lines += ["> K League 1 and K League 2 combined on request; league levels differ.", ""]
    for name, group in groups:
        if not group:
            continue
        small = [p for p in group if is_small(p, args.min_minutes)]
        pool = group if args.include_small else [p for p in group if not is_small(p, args.min_minutes)]
        ranked = [p for p in pool if metric_value(p, args.by) is not None]
        no_data = [p for p in pool if metric_value(p, args.by) is None]
        ranked.sort(key=lambda p: metric_value(p, args.by), reverse=True)
        if args.top:
            ranked = ranked[:args.top]
        rows = [[i, p["id"], p["lg"], p["position"], kind_label(p), fmt_minutes(p),
                 fmt_metric(p, args.by), sample_flag(p, args.min_minutes)]
                for i, p in enumerate(ranked, 1)]
        lines += [f"### {name}", ""]
        lines += table(["#", "Player", "Lg", "Pos", "Type", "League min", label, "Flag"], rows)
        if small and not args.include_small:
            lines += ["", f"Excluded as small sample (<{args.min_minutes} min): " + ", ".join(p["id"] for p in small)]
        if no_data:
            lines += ["", "No data for this metric: " + ", ".join(p["id"] for p in no_data)]
        lines.append("")
    return lines, f"rank_{args.by}_{args.league}"


def cmd_compare(players, args):
    ps = [resolve(players, q) for q in args.players]
    if len({p["id"] for p in ps}) < len(ps):
        die("The same player was given twice.")
    rows = [
        ["League"] + [p["league"] for p in ps],
        ["Position"] + [p["position"] for p in ps],
        ["Type"] + [kind_label(p) for p in ps],
        ["Age"] + [p["age"] or "-" for p in ps],
        ["Foot"] + [p["foot"] or "-" for p in ps],
        ["Height"] + [p["height_cm"] or "-" for p in ps],
        ["Value"] + [fmt_value(p) for p in ps],
        ["Apps / starts"] + [f"{p['league_apps'] or '-'} / {p['league_starts'] or '-'}" for p in ps],
        ["League min"] + [fmt_minutes(p) for p in ps],
        ["Sample"] + [sample_flag(p, args.min_minutes) or "ok" for p in ps],
    ]
    rows += [[METRICS[k][0]] + [fmt_metric(p, k) for p in ps] for k in METRICS]
    lines = [f"## Comparison (min minutes={args.min_minutes})", ""]
    lines += table(["", *[p["id"] for p in ps]], rows)
    warnings = []
    if len({p["lg"] for p in ps}) > 1:
        warnings.append("Players are from different leagues (K1 vs K2); numbers are not like-for-like.")
    duel_types = {("overall" if metric_value(p, "duels") is not None else
                   "ground" if metric_value(p, "ground_duels") is not None else None) for p in ps} - {None}
    if len(duel_types) > 1:
        warnings.append("Duel % types differ (overall vs ground-only); do not compare those rows.")
    for p in ps:
        if is_small(p, args.min_minutes):
            warnings.append(f"{p['id']}: {sample_flag(p, args.min_minutes)} ({fmt_minutes(p)} league min).")
    if warnings:
        lines += ["", "**Warnings**", ""] + [f"- {w}" for w in warnings]
    lines += ["", "**Data notes**", ""] + [f"- {p['id']}: {p['notes'] or '-'}" for p in ps]
    return lines, "compare_" + "_vs_".join(slug(p["name"]) for p in ps)[:80]


def watchlist_path(p):
    return os.path.join(WATCHLIST, f"{slug(p['name'])}__{slug(p['team'])}.md")


def cmd_show(players, args):
    p = resolve(players, args.player)
    lines = [f"## {p['id']} ({p['lg']})", ""]
    info = [
        ["League", p["league"]], ["Position", f"{p['position']} — {kind_label(p)}"],
        ["Born", f"{p['birth_date']} (age {p['age']})"], ["Foot", p["foot"] or "-"],
        ["Height", p["height_cm"] or "-"], ["Value", fmt_value(p)],
        ["Apps / starts", f"{p['league_apps'] or '-'} / {p['league_starts'] or '-'}"],
        ["League min", fmt_minutes(p)], ["All-comps min", p["all_minutes"] or "-"],
        ["Goals / assists", f"{p['goals'] or '-'} / {p['assists'] or '-'}"],
        ["Sample", sample_flag(p, args.min_minutes) or "ok"],
    ]
    info += [[METRICS[k][0], fmt_metric(p, k)] for k in METRICS]
    info += [["Source", f"{p['source']} (as of {p['as_of_date']})"], ["Data notes", p["notes"] or "-"]]
    lines += table(["Field", "Value"], info)
    path = watchlist_path(p)
    lines += ["", "### Watchlist notes", ""]
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            lines += [l.rstrip("\n") for l in f if not l.startswith("# ")]
    else:
        lines.append("(none)")
    return lines, f"show_{slug(p['name'])}_{slug(p['team'])}"


def cmd_note(players, args):
    p = resolve(players, args.player)
    date = args.date or datetime.date.today().isoformat()
    path = watchlist_path(p)
    os.makedirs(WATCHLIST, exist_ok=True)
    text = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
    headers = re.findall(r"^## (.+)$", text, re.M)
    with open(path, "a", encoding="utf-8") as f:
        if not text:
            f.write(f"# {p['id']} ({p['lg']})\n")
        if not headers or headers[-1].strip() != date:
            f.write(f"\n## {date}\n")
        f.write(f"- {args.text}\n")
    print(f"Note added for {p['id']} ({p['lg']}) on {date}: {os.path.relpath(path, ROOT)}")


def filter_slug(args):
    """Non-default filters as a filename suffix, e.g. '_sideL_age23_spec'."""
    parts = []
    if args.side:
        parts.append(f"side{args.side}")
    if args.max_age is not None:
        parts.append(f"age{args.max_age}")
    if args.specialists:
        parts.append("spec")
    if args.min_minutes != 600:
        parts.append(f"min{args.min_minutes}")
    if args.include_small:
        parts.append("small")
    if getattr(args, "top", None):
        parts.append(f"top{args.top}")
    if getattr(args, "combine", False):
        parts.append("combined")
    return "".join("_" + p for p in parts)


def save_report(lines, name, args):
    os.makedirs(REPORTS, exist_ok=True)
    date = datetime.date.today().isoformat()
    base = os.path.join(REPORTS, f"{date}_{name}{filter_slug(args)}")
    path, n = base + ".md", 2
    while os.path.exists(path):  # never overwrite an earlier save
        path, n = f"{base}_{n}.md", n + 1
    cmdline = "python3 scout.py " + " ".join(f'"{a}"' if " " in a else a for a in sys.argv[1:])
    with open(path, "x", encoding="utf-8") as f:
        f.write(f"<!-- generated {date}: {cmdline} -->\n\n" + "\n".join(lines) + "\n")
    print(f"\nSaved: {os.path.relpath(path, ROOT)}")


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--league", choices=["K1", "K2", "all"], default="all")
    common.add_argument("--min-minutes", type=int, default=600)
    common.add_argument("--include-small", action="store_true", help="keep small-sample players in rankings")
    common.add_argument("--specialists", action="store_true", help="primary position LB/RB/LWB/RWB only")
    common.add_argument("--side", choices=["L", "R"], help="players with a left/right full-back role")
    common.add_argument("--max-age", type=int)
    common.add_argument("--save", action="store_true", help="also save output to reports/")

    parser = argparse.ArgumentParser(description="U24 full-back scouting, K League 1 & 2")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", parents=[common], help="list players matching filters")
    rank = sub.add_parser("rank", parents=[common], help="rank by one metric, per league")
    rank.add_argument("--by", choices=list(METRICS), required=True)
    rank.add_argument("--top", type=int)
    rank.add_argument("--combine", action="store_true", help="rank K1 and K2 together (labeled)")
    cmp_ = sub.add_parser("compare", parents=[common], help="side-by-side comparison")
    cmp_.add_argument("players", nargs="+", metavar="Name@Team")
    show = sub.add_parser("show", parents=[common], help="one player's full profile")
    show.add_argument("player", metavar="Name@Team")
    note = sub.add_parser("note", help="add a dated watchlist note")
    note.add_argument("player", metavar="Name@Team")
    note.add_argument("text")
    note.add_argument("--date", help="YYYY-MM-DD (default: today)")
    sub.add_parser("metrics", help="list metric keys for rank --by")
    args = parser.parse_args()

    players = load()
    if args.cmd == "note":
        return cmd_note(players, args)
    if args.cmd == "metrics":
        for k, (label, kind, cols, _) in METRICS.items():
            print(f"{k:14} {label} [{kind}: {'+'.join(cols)}]")
        return
    if args.cmd == "compare" and len(args.players) < 2:
        die("compare needs at least two players.")
    lines, name = {"list": cmd_list, "rank": cmd_rank, "compare": cmd_compare, "show": cmd_show}[args.cmd](players, args)
    print("\n".join(lines))
    if args.save:
        save_report(lines, name, args)


if __name__ == "__main__":
    main()
