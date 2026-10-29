"""check-prose-numbers.py — every number in the prose must come out of the tree.

The rule `AGENTS.md` states ("a number without a command is not a result") was, until now, a rule we asserted and
did not check: `tools/lexspec_status.py` recomputes the status from the working tree, but nothing compared its output
with the numbers written in the documents. The first repository walk
([docs/30](../docs/30-REPO-WALK.md) §2) made the gap concrete: an external contour called `xcheck` checks exactly
"numbers in prose against the tree" across the family of repositories, and it would have found our drift before we
did.

This script is that check, on our side, before anyone else runs it.

Design, deliberately narrow: a claim is a (file, pattern, resolver) triple written down by hand. Only a claim we have
recorded is checked, because a general "find the numbers" pass cannot tell a count from a date or an article number,
and a checker that guesses produces noise that teaches people to ignore it. Adding a claim is a one-line act.

Usage
    python lab/check-prose-numbers.py            # check the registered claims
    python lab/check-prose-numbers.py --list     # show what is registered and how it resolves
    python lab/check-prose-numbers.py --json

Exit: 0 every claim agrees with the tree, 1 a mismatch (printed with both numbers and the command), 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = ROOT          # where the prose is read from; a shadow copy for the self-test
PY = sys.executable


# ---------------------------------------------------------------- resolvers: each one is a command, not a guess

def refusal_codes() -> int:
    """Count the documented codes: one table row per code in docs/11."""
    text = (DOCS_ROOT / "docs" / "11-REFUSAL-CODES.md").read_text(encoding="utf-8")
    return len(re.findall(r"^\| `[A-Z0-9_]+`", text, re.M))


TEST_COUNT_OVERRIDE: int | None = None


def test_count() -> int:
    """The suite's own count, unless a caller measured it once already in the same run."""
    if TEST_COUNT_OVERRIDE is not None:
        return TEST_COUNT_OVERRIDE
    return _run_test_suite()


def _run_test_suite() -> int:
    """Run the suite and read the real number, because a test count is whatever runs."""
    proc = subprocess.run([PY, str(ROOT / "tests" / "run_tests.py")], capture_output=True, text=True, encoding="utf-8")
    match = re.search(r"Ran (\d+) tests?", proc.stderr + proc.stdout)
    if not match:
        raise SystemExit("check-prose-numbers: could not read the test count from the runner")
    return int(match.group(1))


def status_numbers() -> dict:
    """Parse tools/lexspec_status.py, which computes everything from example files rather than from prose."""
    proc = subprocess.run([PY, str(ROOT / "tools" / "lexspec_status.py")], capture_output=True, text=True, encoding="utf-8")
    out = proc.stdout
    atoms = re.search(r"atoms: (\d+) total, (\d+) closed", out)
    examples = re.search(r"examples: (\d+)", out)
    verdicts = re.search(r"verdicts: (.+)", out)
    if not (atoms and examples):
        raise SystemExit("check-prose-numbers: could not parse the status output")
    return {
        "examples": int(examples.group(1)),
        "atoms": int(atoms.group(1)),
        "closed": int(atoms.group(2)),
        "verdict_line": verdicts.group(1).strip() if verdicts else "",
    }


# ---------------------------------------------------------------- claims: file, pattern, resolver, label

CLAIMS = [
    {
        "file": "docs/25-TRUTH-AND-BOUNDS.md",
        "pattern": r"(\d+) codes;",
        "resolve": lambda ctx: refusal_codes(),
        "label": "refusal codes documented in docs/11",
        "command": "python lab/check-prose-numbers.py --list",
    },
    {
        "file": "docs/25-TRUTH-AND-BOUNDS.md",
        "pattern": r"(\d+) tests pass",
        "resolve": lambda ctx: test_count(),
        "label": "tests in tests/run_tests.py",
        "command": "python tests/run_tests.py",
    },
    {
        "file": "docs/30-REPO-WALK.md",
        "pattern": r"\((\d+) tests, (\d+) examples, (\d+) atoms\)",
        "resolve": lambda ctx: {"tests": test_count(), **status_numbers()},
        "label": "status triple quoted in the walk",
        "command": "python tests/run_tests.py && python tools/lexspec_status.py",
        "multi": True,
        "keys": ["tests", "examples", "atoms"],
    },
]

# Phrases that must not appear, each with the decision that killed it. A stale description is drift too, and this
# is the cheapest place to catch it.
FORBIDDEN = [
    {
        "pattern": r"coverage is below threshold",
        "why": "ADR-0010: the threshold is a reporting metric; CHECKED is caused by a declared escape, not by coverage",
        "files": ["README.md", "docs/10-SPEC-v0.1.md"],
    },
]


def scan_forbidden() -> list[dict]:
    problems = []
    for rule in FORBIDDEN:
        for rel in rule["files"]:
            path = DOCS_ROOT / rel
            if not path.is_file():
                continue
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(rule["pattern"], line):
                    problems.append({"kind": "forbidden-phrase", "file": rel, "line": i,
                                     "text": line.strip()[:160], "why": rule["why"]})
    return problems


def check() -> tuple[list[dict], list[dict]]:
    cache: dict[str, object] = {}
    problems: list[dict] = []
    ok: list[dict] = []
    for claim in CLAIMS:
        path = DOCS_ROOT / claim["file"]
        if not path.is_file():
            problems.append({"kind": "missing-file", "file": claim["file"]})
            continue
        match = re.search(claim["pattern"], path.read_text(encoding="utf-8"))
        if not match:
            problems.append({"kind": "claim-not-found", "file": claim["file"], "pattern": claim["pattern"]})
            continue
        key = claim["label"]
        if key not in cache:
            cache[key] = claim["resolve"](None)
        actual = cache[key]
        if claim.get("multi"):
            claimed = [int(g) for g in match.groups()]
            measured = [actual[k] for k in claim["keys"]] if isinstance(actual, dict) else []
            if claimed != measured:
                problems.append({"kind": "mismatch", "file": claim["file"], "label": claim["label"],
                                 "claimed": claimed, "measured": measured, "command": claim["command"]})
            else:
                ok.append({"file": claim["file"], "label": claim["label"], "value": measured})
            continue
        claimed_n = int(match.group(1))
        measured_n = actual if isinstance(actual, int) else None
        if measured_n is None:
            problems.append({"kind": "resolver-shape", "file": claim["file"], "label": claim["label"]})
        elif claimed_n != measured_n:
            problems.append({"kind": "mismatch", "file": claim["file"], "label": claim["label"],
                             "claimed": claimed_n, "measured": measured_n, "command": claim["command"]})
        else:
            ok.append({"file": claim["file"], "label": claim["label"], "value": measured_n})
    return ok, problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Compare the numbers in prose with the numbers in the tree.")
    ap.add_argument("--list", action="store_true", help="show the registered claims and their commands")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--docs-root", default=None, help="read the prose from another tree (used by the self-test)")
    ap.add_argument("--test-count", type=int, default=None, help="reuse a count already measured by the runner")
    args = ap.parse_args(argv)
    if args.docs_root:
        global DOCS_ROOT
        DOCS_ROOT = Path(args.docs_root).resolve()
    if args.test_count is not None:
        global TEST_COUNT_OVERRIDE
        TEST_COUNT_OVERRIDE = args.test_count

    if args.list:
        for claim in CLAIMS:
            print(f"{claim['file']:<32} {claim['label']:<40} {claim['command']}")
        for rule in FORBIDDEN:
            print(f"{'forbidden':<32} {rule['pattern']:<40} {rule['why'][:60]}")
        return 0

    ok, problems = check()
    problems += scan_forbidden()

    if args.json:
        print(json.dumps({"checked": ok, "problems": problems}, ensure_ascii=False, indent=2))
    else:
        for item in ok:
            print(f"ok    {item['file']:<32} {item['label']:<40} = {item['value']}")
        for item in problems:
            if item["kind"] == "mismatch":
                print(f"DRIFT {item['file']:<32} {item['label']:<40} claimed {item['claimed']}, measured {item['measured']}")
                print(f"      reproduce with: {item['command']}")
            elif item["kind"] == "forbidden-phrase":
                print(f"STALE {item['file']}:{item['line']}  {item['text']}")
                print(f"      why: {item['why']}")
            else:
                print(f"ERROR {item['file']:<32} {item['kind']}")

    if problems:
        print(f"\ncheck-prose-numbers: {len(problems)} problem(s) - the prose and the tree disagree")
        return 1
    print(f"\ncheck-prose-numbers: {len(ok)} claim(s) agree with the tree")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
