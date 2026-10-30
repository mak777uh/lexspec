"""lexcheck_twin.py — an independent recomputation of the quantity layer, for comparing with the checker.

Why this exists, and why it is not a duplication: `ADR-0002` promised a Python twin so that substrate neutrality would
be measured rather than asserted, and `docs/27` §6 made it an acceptance test. Reading LongTails on 2026-10-30 made
the reason sharper — their audit is a **separate program** written by other people against the same contract
(`leanprover/comparator`), because a checker written by the hand that wrote the claim shares its blind spots.

So this file deliberately does the arithmetic a different way than `tools/lexcheck.py`:

  * the checker computes with `Decimal` and `quantize(Decimal(1), ROUND_HALF_UP)`;
  * the twin computes with integers only: `q, r = divmod(num, den)`, then `q += 1 if 2*r >= den`.

Same semantics, different code path. If the two agree on every segment and on the total, that is evidence. If they
disagree, the difference is a finding about one of them, and it is cheaper to find it here than in a court filing.

Usage
    python tools/lexcheck_twin.py examples/10-gk-rf-395-quantified.lex.json
    python tools/lexcheck_twin.py examples/10-… --json

Exit: 0 the twin and the checker agree, 1 they disagree, 2 the statement has no quantities to check.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "tools" / "lexcheck.py"


def load_series(statement: dict, root: Path) -> dict[str, list[tuple[str, int]]]:
    """Read the pinned series files, verifying the digest independently of the checker."""
    out: dict[str, list[tuple[str, int]]] = {}
    for entry in statement.get("series", []):
        path = root / entry["path"]
        blob = path.read_bytes()
        actual = hashlib.sha256(blob).hexdigest()
        if actual != entry["digest"]:
            raise SystemExit(f"twin: series {entry['id']!r} does not match its digest")
        data = json.loads(blob.decode("utf-8"))
        out[entry["id"]] = sorted((p["date"], int(p["value_bp"])) for p in data["points"])
    return out


def is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def day_ordinal(date: str) -> int:
    y, m, d = (int(x) for x in date.split("-"))
    return dt.date(y, m, d).toordinal()


def next_day(date: str) -> str:
    y, m, d = (int(x) for x in date.split("-"))
    return (dt.date(y, m, d) + dt.timedelta(days=1)).isoformat()


def previous_day(date: str) -> str:
    y, m, d = (int(x) for x in date.split("-"))
    return (dt.date(y, m, d) - dt.timedelta(days=1)).isoformat()


def half_up_div(num: int, den: int) -> int:
    """Half-up rounding in pure integers — the twin's whole point is not to share the checker's arithmetic."""
    q, r = divmod(num, den)
    return q + 1 if 2 * r >= den else q


def segments_for(points: list[tuple[str, int]], period: dict, payments: list[dict]) -> list[dict]:
    start, end = period["from"], period["to"]
    cuts = {start}
    for date, _bp in points:
        if start < date <= end:
            cuts.add(date)
    for payment in payments:
        effective = next_day(payment["date"])
        if start < effective <= end:
            cuts.add(effective)
    if period.get("day_count") == "actual/actual":
        year = int(start[:4])
        while f"{year + 1}-01-01" <= end:
            if is_leap(year) != is_leap(year + 1):
                cuts.add(f"{year + 1}-01-01")
            year += 1
    ordered = sorted(cuts)
    out = []
    for i, begin in enumerate(ordered):
        stop = previous_day(ordered[i + 1]) if i + 1 < len(ordered) else end
        rate = None
        for date, bp in points:
            if date <= begin:
                rate = bp
        out.append({"from": begin, "to": stop, "days": day_ordinal(stop) - day_ordinal(begin) + 1, "value_bp": rate})
    return out


def recompute(statement: dict, root: Path) -> dict:
    series = load_series(statement, root)
    results = {}
    for quantity in statement.get("quantities", []):
        if quantity.get("kind") != "rate_of":
            continue
        points = series[quantity["series"]]
        payments = quantity.get("payments", [])
        base_spec = quantity.get("base_amount") or {}
        base = int(base_spec.get("value", 0))
        segments = segments_for(points, quantity["period"], payments)
        total = 0
        for segment in segments:
            effective_base = base
            for payment in payments:
                if payment["date"] < segment["from"]:
                    effective_base -= int(payment["value"])
            year = int(segment["from"][:4])
            days_in_year = 366 if is_leap(year) else 365
            numerator = effective_base * segment["days"] * segment["value_bp"]
            denominator = 100  # percent -> fraction
            denominator *= 10000  # value_bp -> percent
            denominator *= days_in_year
            interest = half_up_div(numerator, denominator)
            segment["base_minor"] = effective_base
            segment["interest"] = interest
            total += interest
        results[quantity["id"]] = {"segments": segments, "total_minor": total}
    return results


def checker_report(path: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(path), "--json", "--root", str(ROOT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if not proc.stdout.strip():
        raise SystemExit(f"twin: the checker produced no report for {path.name}")
    return json.loads(proc.stdout)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Recompute the quantity layer independently and compare.")
    ap.add_argument("statement", help="path to a .lex.json statement")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--allow-empty",
        action="store_true",
        help="exit 0 when the statement carries no quantities (for a loop over all examples)",
    )
    args = ap.parse_args(argv)

    path = Path(args.statement).resolve()
    document = json.loads(path.read_text(encoding="utf-8"))
    if not document.get("quantities"):
        if args.allow_empty:
            return 0
        print("twin: this statement has no quantities", file=sys.stderr)
        return 2

    mine = recompute(document, ROOT)
    report = checker_report(path)
    theirs = report.get("quantities", {})

    problems: list[str] = []
    for qid, result in mine.items():
        other = theirs.get(qid) or {}
        if other.get("total_minor") != result["total_minor"]:
            problems.append(f"{qid}: total differs — twin {result['total_minor']}, checker {other.get('total_minor')}")
        other_segments = other.get("segments") or []
        if len(other_segments) != len(result["segments"]):
            problems.append(f"{qid}: {len(result['segments'])} segments in the twin, {len(other_segments)} in the checker")
            continue
        for mine_seg, their_seg in zip(result["segments"], other_segments):
            if mine_seg["from"] != their_seg["from"] or mine_seg["days"] != their_seg["days"]:
                problems.append(
                    f"{qid}: segment boundary differs — twin {mine_seg['from']}..{mine_seg['to']} "
                    f"({mine_seg['days']} d), checker {their_seg['from']}..{their_seg['to']} ({their_seg['days']} d)"
                )
                break
            if str(mine_seg["interest"]) != str(their_seg.get("interest")):
                problems.append(
                    f"{qid}: interest differs at {mine_seg['from']} — twin {mine_seg['interest']}, "
                    f"checker {their_seg.get('interest')}"
                )
                break

    if args.json:
        print(json.dumps({"twin": mine, "problems": problems}, ensure_ascii=False, indent=2))
    else:
        for qid, result in mine.items():
            print(f"{qid}: {len(result['segments'])} segments, total {result['total_minor']} minor units")
        for problem in problems:
            print(f"DISAGREE {problem}")

    if problems:
        print(f"\nlexcheck_twin: {len(problems)} disagreement(s) between two independent implementations")
        return 1
    print("\nlexcheck_twin: the twin and the checker agree on every segment and on the total")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
