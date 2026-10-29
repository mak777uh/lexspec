"""experiment.py — record one encoding attempt as a machine-readable row, and read the rows back.

Why: the owner's priority is to find *principles* and test them, keeping every test as a dataset for later.
A principle is a regularity with a measurement; a measurement that is not recorded in a fixed shape is an anecdote.
This tool makes the shape fixed and the accumulation automatic.

A row is produced from an existing statement: the checker is run, coverage and codes are read from its report, the
statement and corpus digests are recorded, and the human adds the two things a tool cannot know — how long it took
and what went wrong.

Usage
    python lab/experiment.py add --statement examples/07-gdpr-art17.lex.json \
        --minutes 9 --span-attempts 5 --span-failures 3 --cause "line wrap" \
        --principle P2 --note "carve-out in 17(3) not expressible"

    python lab/experiment.py list
    python lab/experiment.py list --json

Storage: lab/experiments.jsonl — append-only, one JSON object per line. Records are never edited; a correction is a
new row with `corrects` pointing at the old id.

Exit: 0 ok, 1 the statement did not check, 2 usage error. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "lab" / "experiments.jsonl"
CHECKER = ROOT / "tools" / "lexcheck.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checker(statement: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(statement), "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if not proc.stdout.strip():
        raise SystemExit(f"experiment: the checker produced no report\n{proc.stderr[:400]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"experiment: report is not JSON: {exc}") from exc


def next_id(rows: list[dict]) -> str:
    used = [int(r["id"].split("-")[1]) for r in rows if r.get("id", "").startswith("E-")]
    return f"E-{(max(used) + 1) if used else 1:04d}"


def load() -> list[dict]:
    if not STORE.is_file():
        return []
    return [json.loads(line) for line in STORE.read_text(encoding="utf-8").splitlines() if line.strip()]


def add(args: argparse.Namespace) -> int:
    statement = Path(args.statement).resolve()
    if not statement.is_file():
        print(f"experiment: no such statement: {statement}", file=sys.stderr)
        return 2
    report = run_checker(statement)
    doc = json.loads(statement.read_text(encoding="utf-8"))
    corpus = doc.get("corpus", [{}])[0]
    try:
        display = str(statement.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        display = str(statement)

    rows = load()
    row = {
        "id": next_id(rows),
        "date": args.date or date.today().isoformat(),
        "provision": {
            "id": doc.get("id"),
            "jurisdiction": doc.get("jurisdiction", []),
            "kind": doc.get("kind"),
            "article": (doc.get("atoms") or [{}])[0].get("anchor", {}).get("article"),
        },
        "corpus": {"file": corpus.get("text"), "sha256": corpus.get("text_sha256")},
        "statement": {
            "file": display,
            "sha256": sha(statement),
            "atoms": report.get("atoms", {}).get("total"),
            "closed": report.get("atoms", {}).get("closed"),
            "anchored": report.get("atoms", {}).get("anchored"),
            "coverage": report.get("coverage"),
            "verdict": report.get("verdict"),
        },
        "codes": sorted({f["code"] for f in report.get("findings", [])}),
        "unclosed": [
            {"atom": f.get("atom"), "code": f["code"], "detail": f.get("detail", "")[:200]}
            for f in report.get("findings", [])
            if f["code"] in {"OPEN_TERM", "THIN_COVERAGE"}
        ],
        "anchoring": {
            "span_attempts": args.span_attempts,
            "span_failures": args.span_failures,
            "cause": args.cause,
        },
        "timing": {
            "minutes_to_first_verdict": args.minutes,
            "minutes_to_pass": args.minutes_to_pass,
            "by": args.by,
        },
        "principles_touched": args.principle or [],
        "note": args.note or "",
    }
    if args.corrects:
        row["corrects"] = args.corrects

    STORE.parent.mkdir(parents=True, exist_ok=True)
    with STORE.open("a", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")

    print(f"{row['id']}  {row['provision']['id']:<28} coverage={row['statement']['coverage']}  "
          f"verdict={row['statement']['verdict']}  codes={','.join(row['codes']) or '-'}")
    print(f"       recorded in {STORE.relative_to(ROOT)}; total rows: {len(rows) + 1}")
    return 0


def show(args: argparse.Namespace) -> int:
    rows = load()
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("experiment: no rows yet — run `add` with a statement that checks")
        return 0
    print(f"{'id':<7}{'provision':<30}{'atoms':>6}{'closed':>7}{'cov':>6}  {'verdict':<17}{'min':>5}  codes")
    for r in rows:
        s = r["statement"]
        mins = r["timing"]["minutes_to_first_verdict"]
        print(f"{r['id']:<7}{str(r['provision']['id'])[:29]:<30}{s['atoms'] or 0:>6}{s['closed'] or 0:>7}"
              f"{(s['coverage'] if s['coverage'] is not None else 0):>6.3f}  {s['verdict']:<17}"
              f"{(mins if mins is not None else 0):>5}  {','.join(r['codes']) or '-'}")
    print(f"\nrows: {len(rows)}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Record and read encoding experiments.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="run the checker on a statement and append a row")
    a.add_argument("--statement", required=True)
    a.add_argument("--minutes", type=float, help="minutes to the first verdict")
    a.add_argument("--minutes-to-pass", type=float, default=None)
    a.add_argument("--span-attempts", type=int, default=None)
    a.add_argument("--span-failures", type=int, default=None)
    a.add_argument("--cause", default=None, help="why the span attempts failed, in a few words")
    a.add_argument("--principle", action="append", help="principle id this row speaks to (repeatable)")
    a.add_argument("--note", default=None)
    a.add_argument("--by", default="model:deepseek-v4.1-flash@2026-10-29")
    a.add_argument("--date", default=None)
    a.add_argument("--corrects", default=None, help="id of the row this one corrects")
    a.set_defaults(func=add)

    l = sub.add_parser("list", help="print the recorded rows")
    l.add_argument("--json", action="store_true")
    l.set_defaults(func=show)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
