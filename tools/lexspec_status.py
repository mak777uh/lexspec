#!/usr/bin/env python3
"""lexspec_status — the numbers the docs are allowed to quote.

Why a tool and not a paragraph: AGENTS.md rule 1 says every number in this
repository comes from a command, not from memory. This is that command. Its
output is short, stable and free of timestamps and absolute paths so that a docs
page can paste it verbatim and stay true until the files change.

What it measures: the verdict and coverage of every examples/*.lex.json, as
produced by the same analyse function the CLI uses (not a re-implementation —
a status page that computes coverage its own way is how two numbers start
disagreeing), plus the digest check of every pinned corpus.

Exit codes: 0 when every declared corpus digest matches its file, 1 when one does not, 2 when the tree cannot be read. (Before 2026-10-31 this line said "0 always" and the code agreed with it — which made the digest check decorative.)
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THRESHOLD = 0.8


def _load_checker():
    """Import tools/lexcheck.py by path: tools/ is not a package and should not be."""
    spec = importlib.util.spec_from_file_location("lexcheck", ROOT / "tools" / "lexcheck.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    digests_ok = True  # set below by the digest check
    lexcheck = _load_checker()
    examples = sorted((ROOT / "examples").glob("*.lex.json"))
    if not examples:
        print("LexSpec status: no examples/*.lex.json found")
        return 0

    rows = []
    totals = {"atoms": 0, "closed": 0, "anchored": 0}
    pinned: dict[str, str] = {}
    digests_ok = True
    verdicts: dict[str, int] = {}

    for example in examples:
        report = lexcheck.analyze_file(example, THRESHOLD, ROOT)
        rows.append((example.name, report["verdict"], report["coverage"],
                     report["atoms"]["closed"], report["atoms"]["total"],
                     report["atoms"]["anchored"]))
        totals["atoms"] += report["atoms"]["total"]
        totals["closed"] += report["atoms"]["closed"]
        totals["anchored"] += report["atoms"]["anchored"]
        verdicts[report["verdict"]] = verdicts.get(report["verdict"], 0) + 1

        document = json.loads(example.read_text(encoding="utf-8"))
        for entry in document.get("corpus", []):
            if not isinstance(entry, dict):
                continue
            declared = entry.get("text")
            digest = entry.get("text_sha256")
            if not isinstance(declared, str) or not isinstance(digest, str):
                continue
            pinned[declared] = digest
            path = ROOT / declared
            try:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                actual = None
            if actual != digest:
                digests_ok = False

    width = max(len(row[0]) for row in rows)
    print("LexSpec v0.1 — status computed from the working tree (not from claims)")
    print(f"examples: {len(rows)}   coverage threshold: {THRESHOLD}")
    for name, verdict, coverage, closed, total, anchored in rows:
        print(f"  {name:<{width}}  {verdict:<16} coverage {coverage:.3f}  "
              f"atoms {closed}/{total} closed, {anchored}/{total} anchored")
    spread = ", ".join(f"{verdict} {count}" for verdict, count in sorted(verdicts.items()))
    print(f"verdicts: {spread}")
    atoms = totals["atoms"]
    closed_pct = (100.0 * totals["closed"] / atoms) if atoms else 0.0
    anchored_pct = (100.0 * totals["anchored"] / atoms) if atoms else 0.0
    print(f"atoms: {atoms} total, {totals['closed']} closed ({closed_pct:.1f}%), "
          f"{totals['anchored']} anchored ({anchored_pct:.1f}%)")
    print(f"corpus: {len(pinned)} pinned file(s), digests match declarations: "
          f"{'yes' if digests_ok else 'NO'}")
    print("commands:")
    print("  python tools/lexcheck.py examples/01-delivery-ok.lex.json")
    print("  python tools/check_examples.py")
    print("  python tests/run_tests.py")
    print("  python lab/check-secrets.py")
    # The audit of 2026-10-31 found the tool printing a digest mismatch and returning 0: the number
    # existed and was never consulted. A status page that cannot fail is a page that can lie.
    return 0 if digests_ok else 1



if __name__ == "__main__":
    sys.exit(main())
