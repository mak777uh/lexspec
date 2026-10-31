"""hypothesis.py — pre-register a hypothesis, then record what happened.

Taken from the family's bench practice (`morphogenesis/experiments/journal.jsonl` writes a PRE-REG event before the
run; `VecDHT/lab/hypotheses/H-*.md` and `lab/experiments/E-*.md` are the two-card form). The defect that practice
avoids is the one every honest person commits: deciding after the fact what the experiment was about.

Three files, append-only, one JSON object per line:

  lab/hypotheses.jsonl        {id, claim, falsifier, principles[], status}
  lab/preregistrations.jsonl  {id, hypothesis, prediction, snapshot{file,sha256}, registered}
  lab/experiments.jsonl       existing rows; a row may name `prereg`

A hypothesis is stated so that it can be wrong: `falsifier` says what observation would refute it. A pre-registration
is written *before* the run and carries the digest of the file it is about, so the claim it made cannot be quietly
re-pointed at a different version. An experiment either names a pre-registration or declares itself exploratory.

Usage
    python lab/hypothesis.py add "claim" --falsifier "…" --principle P7
    python lab/hypothesis.py prereg H-0001 "prediction" --about examples/12-….lex.json
    python lab/hypothesis.py close H-0001 --status refuted --note "…"
    python lab/hypothesis.py list

Precedence, stated because a log with two rows per id is ambiguous otherwise: **the last row for an id wins**,
and `close` appends rather than edits. A reader of the file alone cannot know that, so `list` prints one line
per id and `lab/check-experiments.py` says how many rows each id has.

Exit: 0 written, 1 refused (unknown id, missing file), 2 usage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HYP = ROOT / "lab" / "hypotheses.jsonl"
PRE = ROOT / "lab" / "preregistrations.jsonl"


def load(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def next_id(rows: list[dict], prefix: str) -> str:
    used = [int(r["id"].split("-")[1]) for r in rows if r.get("id", "").startswith(prefix + "-")]
    return f"{prefix}-{(max(used) + 1) if used else 1:04d}"


def cmd_add(args) -> int:
    rows = load(HYP)
    row = {
        "id": next_id(rows, "H"),
        "claim": args.claim,
        "falsifier": args.falsifier,
        "principles": args.principle or [],
        "status": "open",
        "registered": date.today().isoformat(),
    }
    append(HYP, row)
    print(f"{row['id']}  {args.claim[:70]}")
    return 0


def cmd_prereg(args) -> int:
    hypotheses = {r["id"] for r in load(HYP)}
    if args.hypothesis not in hypotheses:
        print(f"hypothesis.py: no such hypothesis {args.hypothesis!r}", file=sys.stderr)
        return 1
    about = Path(args.about).resolve() if args.about else None
    if about and not about.is_file():
        print(f"hypothesis.py: no such file {about}", file=sys.stderr)
        return 1
    rows = load(PRE)
    row = {
        "id": next_id(rows, "PR"),
        "hypothesis": args.hypothesis,
        "prediction": args.prediction,
        "registered": date.today().isoformat(),
        "snapshot": (
            {"file": str(about.relative_to(ROOT)).replace("\\", "/"),
             "sha256": hashlib.sha256(about.read_bytes()).hexdigest()}
            if about and about.is_relative_to(ROOT)
            else {"file": str(about) if about else None, "sha256": None}
        ),
    }
    append(PRE, row)
    print(f"{row['id']}  {args.hypothesis}  {args.prediction[:60]}")
    if args.supersedes:
        # a tombstone, not an edit: the old prediction stays readable, and it names what replaced it
        append(
            PRE,
            {
                "id": args.supersedes,
                "superseded_by": row["id"],
                "note": f"the file it froze changed; replaced by {row['id']} against the current version",
            },
        )
        print(f"{args.supersedes} superseded by {row['id']}")
    return 0


def cmd_close(args) -> int:
    rows = load(HYP)
    match = [r for r in rows if r["id"] == args.hypothesis]
    if not match:
        print(f"hypothesis.py: no such hypothesis {args.hypothesis!r}", file=sys.stderr)
        return 1
    # append-only: a status change is a new line, not an edit
    row = dict(match[-1])
    row.update(status=args.status, note=args.note or "", closed=date.today().isoformat())
    append(HYP, row)
    print(f"{args.hypothesis} -> {args.status}")
    return 0


def cmd_list(argv) -> int:
    latest: dict[str, dict] = {}
    for row in load(HYP):
        latest[row["id"]] = row
    preregs: dict[str, list[dict]] = {}
    for row in load(PRE):
        if row.get("superseded_by"):
            continue
        preregs.setdefault(row["hypothesis"], []).append(row)
    print(f"{'id':<8}{'status':<10}{'prereg':<8}{'claim':<60}")
    for hid in sorted(latest):
        row = latest[hid]
        print(f"{hid:<8}{row.get('status','?'):<10}{len(preregs.get(hid, [])):<8}{row['claim'][:58]}")
    print(f"\nhypotheses: {len(latest)}, pre-registrations: {sum(len(v) for v in preregs.values())}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Pre-register hypotheses and close them with a status.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("claim")
    a.add_argument("--falsifier", required=True, help="what observation would refute this")
    a.add_argument("--principle", action="append")
    a.set_defaults(func=cmd_add)

    p = sub.add_parser("prereg")
    p.add_argument("hypothesis")
    p.add_argument("prediction")
    p.add_argument("--about", help="the file the prediction is about; its digest is frozen here")
    p.add_argument("--supersedes", help="id of a pre-registration this one replaces (its file changed)")
    p.set_defaults(func=cmd_prereg)

    c = sub.add_parser("close")
    c.add_argument("hypothesis")
    c.add_argument("--status", required=True, choices=["supported", "refuted", "inconclusive", "abandoned"])
    c.add_argument("--note", default="")
    c.set_defaults(func=cmd_close)

    l = sub.add_parser("list")
    l.set_defaults(func=cmd_list)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
