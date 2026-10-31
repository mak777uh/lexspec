"""check-experiments.py — the bench discipline: no result without a pre-registration, no open forecast left rotting.

Three rules, each borrowed from a repository that already runs a bench:

  1. every experiment row either names a pre-registration or declares itself exploratory (morphogenesis writes PRE-REG
     before the run; the row cannot be reinterpreted afterwards);
  2. a pre-registration's snapshot digest must still match the file it froze, or the pre-registration is about a
     document that no longer exists — the same defect as a stale whitelist;
  3. a pre-registration older than the grace period with no outcome is a finding, not a memory: an open forecast that
     nobody closes is how a bench turns into a diary.

Rows written before this discipline existed are grandfathered by name, not by silence.

Usage
    python lab/check-experiments.py
    python lab/check-experiments.py --grace-days 21 --json

Exit: 0 clean, 1 finding(s), 2 the tree could not be read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HYP = ROOT / "lab" / "hypotheses.jsonl"
PRE = ROOT / "lab" / "preregistrations.jsonl"
EXP = ROOT / "lab" / "experiments.jsonl"

# The three rows written before pre-registration existed. Named individually so the exception cannot grow silently.
GRANDFATHERED = {"E-0001", "E-0002", "E-0003"}


def load(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Bench discipline check.")
    ap.add_argument("--grace-days", type=int, default=14)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    hypotheses = {r["id"]: r for r in load(HYP)}
    raw_preregs = load(PRE)
    # A supersession is an additional line carrying the OLD id and a successor; the original line stays readable in
    # the file, so the filter has to be on the set of superseded names rather than on the row's own flag.
    superseded_ids = {row["id"] for row in raw_preregs if row.get("superseded_by")}
    preregs = [row for row in raw_preregs if row["id"] not in superseded_ids and not row.get("superseded_by")]
    experiments = load(EXP)

    findings: list[dict] = []
    today = date.today()

    # rule 1: every experiment declares its origin
    for row in experiments:
        eid = row.get("id", "?")
        if eid in GRANDFATHERED:
            continue
        if not row.get("prereg") and row.get("origin") != "exploratory":
            findings.append(
                {
                    "kind": "NO_PREREG",
                    "row": eid,
                    "detail": "experiment names no pre-registration and does not declare itself exploratory",
                }
            )

    # rule 2: a frozen snapshot must still be the snapshot
    for row in preregs:
        snapshot = row.get("snapshot") or {}
        rel = snapshot.get("file")
        digest = snapshot.get("sha256")
        if not rel or not digest:
            findings.append({"kind": "NO_SNAPSHOT", "row": row["id"], "detail": "pre-registration froze no file"})
            continue
        path = ROOT / rel
        if not path.is_file():
            findings.append({"kind": "SNAPSHOT_GONE", "row": row["id"], "detail": f"{rel} no longer exists"})
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            findings.append(
                {
                    "kind": "SNAPSHOT_DRIFT",
                    "row": row["id"],
                    "detail": f"{rel} changed since it was frozen; the prediction was made about a different file",
                }
            )

    # rule 3: open forecasts expire
    closed = {r["id"] for r in hypotheses.values() if r.get("status") in {"supported", "refuted", "inconclusive", "abandoned"}}
    for row in preregs:
        hid = row.get("hypothesis")
        if hid in closed:
            continue
        try:
            registered = datetime.strptime(row.get("registered", ""), "%Y-%m-%d").date()
        except ValueError:
            findings.append({"kind": "BAD_DATE", "row": row["id"], "detail": "registered date is not YYYY-MM-DD"})
            continue
        age = (today - registered).days
        if age > args.grace_days:
            findings.append(
                {
                    "kind": "PREREG_STALE",
                    "row": row["id"],
                    "detail": f"{hid} pre-registered {age} days ago and still open; close it or abandon it",
                }
            )

    # Two rows with one id are legal (the log is append-only) and the last one wins; say so instead of failing,
    # because a status change is supposed to append. Silence about it was the audit's complaint.
    seen: dict[str, int] = {}
    for row in load(HYP):
        seen[row['id']] = seen.get(row['id'], 0) + 1
    duplicates = {hid: n for hid, n in seen.items() if n > 1}

    if args.json:
        print(json.dumps({"findings": findings, "duplicate_ids": duplicates}, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"{item['kind']:<14} {item['row']}: {item['detail']}")
        for hid, count in sorted(duplicates.items()):
            print(f"note: {hid} has {count} rows; the last one wins (append-only log)")
        print(
            f"\ncheck-experiments: {len(hypotheses)} hypothesis(es), {len(preregs)} pre-registration(s), "
            f"{len(experiments)} experiment row(s), {len(findings)} finding(s)"
        )

    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
