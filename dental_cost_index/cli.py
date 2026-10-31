"""Command line interface for dental-cost-index."""

import argparse
import csv
import json
import sys

from .data import EDITION, STATES, STUDY_URL

FIELDS = list(STATES[0].keys())

SOURCES = (
    "Income and population: US Census Bureau, ACS 2024 1-year.\n"
    "Oral surgeon and dentist counts: KFF, via an ADA Health Policy Institute\n"
    "  special data request.\n"
    "Tooth loss among adults 65+: CDC BRFSS 2020, NOHSS indicator ADT1_3,\n"
    "  crude prevalence. Self-reported; the module last ran in 2020.\n"
    "Medicaid adult dental benefit rating: CareQuest Institute / ADA HPI /\n"
    "  Center for Health Care Strategies rubric, as of 31 December 2024.\n"
    "Implant cost: dentalimplantcalc.com cost model, 2026 edition.\n"
    "\n"
    "Per-capita rates, ranks, cost-as-a-share-of-income figures and the\n"
    "quadrant classification are derived from those inputs, not published\n"
    "figures in their own right.\n"
    "\n"
    "The cost model carries one geographic adjustment, a major-metro premium,\n"
    "so 44 of 50 states share a single sticker price and only the income\n"
    "denominator varies. No sourced figure for a lower-cost-market discount\n"
    "was found, and the model does not invent one.\n"
    "\n"
    "Nothing here is a price quote or clinical advice.\n"
    f"Full method and limitations: {STUDY_URL}"
)


def find(token):
    """Look a state up by USPS code or by name, case-insensitively."""
    t = token.strip().lower()
    for row in STATES:
        if row["usps"].lower() == t or row["state"].lower() == t:
            return row
    matches = [r for r in STATES if r["state"].lower().startswith(t)]
    if len(matches) == 1:
        return matches[0]
    if matches:
        names = ", ".join(r["state"] for r in matches)
        raise SystemExit(f"'{token}' matches more than one state: {names}")
    raise SystemExit(f"No state called '{token}'. Try --list.")


def usd(n):
    return f"${n:,.0f}"


def report(row):
    name = row["state"]
    rule = "=" * len(name)
    out = [name, rule, ""]

    if row["single_low"] == row["single_high"]:
        single = usd(row["single_low"])
    else:
        single = f"{usd(row['single_low'])} to {usd(row['single_high'])}"
    out += [
        "Cost",
        f"  Single implant, post to crown    {single}",
        f"  One arch, All-on-4 standard      {usd(row['arch_low'])} to {usd(row['arch_high'])}",
        "",
        "Against what households earn",
        f"  Median household income          {usd(row['income'])}  (+/- {usd(row['income_moe'])})",
        f"  Single implant                   {row['single_pct']}% of a year's income",
        f"  One arch                         {row['arch_pct']}% of a year's income",
        "",
        "Against what households aged 65+ earn",
        f"  Median household income, 65+     {usd(row['income_65plus'])}  (+/- {usd(row['income_65plus_moe'])})",
        f"  That is                          {row['senior_income_gap_pct']}% against all ages",
        f"  Single implant                   {row['single_pct_65plus']}% of a year's income",
        f"  One arch                         {row['arch_pct_65plus']}% of a year's income",
        "",
        "Who is there to do the work",
        f"  Oral and maxillofacial surgeons  {row['oral_surgeons']:,}",
        f"  Per 100,000 residents            {row['oral_per_100k']}  (rank {row['oral_rank']} of 50)",
        f"  Per 100,000 residents aged 65+   {row['oral_per_100k_65plus']}",
        f"  All dentists per 100,000         {row['dentists_per_100k']}  (rank {row['dentist_rank']} of 50)",
        "",
        "Tooth loss",
        f"  Adults 65+ with no natural teeth {row['edentulism_65plus']}%"
        f"  (95% CI {row['edentulism_ci_low']}-{row['edentulism_ci_high']},"
        f" rank {row['edentulism_rank']} of 50, 1 = worst)",
        "",
        "Medicaid",
        f"  Extensive adult dental benefit   {'yes' if row['medicaid_extensive'] else 'no'}",
        "  Note: the rubric behind that rating scores fourteen service",
        "  categories and stops at dentures. Implants are in none of them,",
        "  so 'extensive' does not mean implants are covered.",
        "",
        f"Quadrant: {row['quadrant']}",
    ]
    if row["quadrant"] == "double bind":
        out.append("  Below the 50-state median on surgeon supply and above it on cost burden.")
    return "\n".join(out)


def table(rows, sort_key, reverse):
    rows = sorted(rows, key=lambda r: r[sort_key], reverse=reverse)
    head = f"{'State':<22}{'$/implant':>11}{'% income':>10}{'% 65+ inc':>11}{'OS/100k':>9}{'65+ no teeth':>14}"
    lines = [head, "-" * len(head)]
    for r in rows:
        lines.append(
            f"{r['state']:<22}"
            f"{usd(r['single_low']):>11}"
            f"{r['single_pct']:>9.2f}%"
            f"{r['single_pct_65plus']:>10.2f}%"
            f"{r['oral_per_100k']:>9.2f}"
            f"{r['edentulism_65plus']:>13.1f}%"
        )
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="dental-cost-index",
        description=(
            "What a dental implant costs in each US state, against what people "
            "there earn and how many oral surgeons are around to place it."
        ),
        epilog=f"Data edition {EDITION}. CC BY 4.0. {STUDY_URL}",
    )
    p.add_argument("state", nargs="?", help="state name or USPS code, e.g. WY or Wyoming")
    p.add_argument("--list", action="store_true", help="table of all 50 states")
    p.add_argument("--double-bind", action="store_true",
                   help="only the 15 states short on surgeons and heavy on cost")
    p.add_argument("--worst-tooth-loss", type=int, metavar="N",
                   help="the N states with the highest tooth loss among adults 65+")
    p.add_argument("--sort", default="state",
                   choices=["state", "single_pct", "single_pct_65plus",
                            "oral_per_100k", "edentulism_65plus", "income"],
                   help="column to sort a table by (default: state)")
    p.add_argument("--json", action="store_true", help="JSON instead of text")
    p.add_argument("--csv", action="store_true", help="CSV of every state and column")
    p.add_argument("--sources", action="store_true", help="where the numbers come from")
    p.add_argument("--version", action="version",
                   version=f"dental-cost-index data edition {EDITION}")
    args = p.parse_args(argv)

    if args.sources:
        print(SOURCES)
        return 0

    if args.csv:
        w = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(STATES)
        return 0

    rows = STATES
    if args.double_bind:
        rows = [r for r in rows if r["quadrant"] == "double bind"]
    if args.worst_tooth_loss:
        rows = sorted(rows, key=lambda r: -r["edentulism_65plus"])[: args.worst_tooth_loss]

    if args.state:
        row = find(args.state)
        print(json.dumps(row, indent=2) if args.json else report(row))
        return 0

    if args.list or args.double_bind or args.worst_tooth_loss:
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            descending = args.sort != "state"
            print(table(rows, args.sort, descending))
            print(f"\n{len(rows)} states. Data edition {EDITION}. "
                  f"Run with --sources for where this comes from.")
        return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
