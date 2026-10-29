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


class ProseProblem(Exception):
    """A resolver found a defect that is not a number mismatch; it becomes a finding, not a crash."""

    def __init__(self, kind: str, detail: str) -> None:
        super().__init__(detail)
        self.kind = kind
        self.detail = detail


def suite_is_green(returncode: int, output: str) -> tuple[bool, str]:
    """A test count only means "pass" if the run also passed. Separated so it can be unit-tested."""
    if returncode != 0:
        return False, f"the test suite exited {returncode}"
    if not re.search(r"^OK\b", output, re.M):
        return False, "the test suite did not print OK"
    return True, ""


def _run_test_suite() -> int:
    """Run the suite and read the real number — and refuse to lend it to a claim when the run failed.

    The first version of this resolver read `Ran N tests` and returned N regardless of the exit code, so a red
    suite still satisfied the sentence "N tests pass". The claim is about passing, so the resolver has to prove it.
    """
    proc = subprocess.run([PY, str(ROOT / "tests" / "run_tests.py")], capture_output=True, text=True, encoding="utf-8")
    output = proc.stderr + proc.stdout
    green, why = suite_is_green(proc.returncode, output)
    if not green:
        raise ProseProblem("suite-red", why)
    match = re.search(r"Ran (\d+) tests?", output)
    if not match:
        raise ProseProblem("suite-red", "the runner printed OK but no test count")
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
        "pattern": r"\((\d+) tests, (\d+) examples, (\d+) atoms, (\d+) closed\)",
        "resolve": lambda ctx: {"tests": test_count(), **status_numbers()},
        "label": "status triple quoted in the walk",
        "command": "python tests/run_tests.py && python tools/lexspec_status.py",
        "multi": True,
        "keys": ["tests", "examples", "atoms", "closed"],
    },
]

# Phrases that must not appear, each with the decision that killed it. A stale description is drift too, and this
# is the cheapest place to catch it.
FORBIDDEN = [
    {
        "pattern": r"coverage is below threshold",
        "why": "ADR-0010: the threshold is a reporting metric; CHECKED is caused by a declared escape, not by coverage",
        "files": ["README.md", "docs/10-SPEC-v0.1.md", ".github/workflows/guards.yml"],
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
            try:
                cache[key] = claim["resolve"](None)
            except ProseProblem as problem:
                problems.append({"kind": problem.kind, "file": claim["file"], "label": claim["label"],
                                 "detail": problem.detail})
                continue
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


# Living documents: the ones a reader treats as current. A historical lab note may quote an old number on purpose,
# so it is out of scope by declaration rather than by accident.
LIVING = ["README.md", "README.ru.md", "docs/25-TRUTH-AND-BOUNDS.md"]

# Count-adjacent numbers allowed to differ from the tree, each with the reason it is allowed. A whitelist without
# reasons is how a guard becomes decoration, so every entry states why.
WHITELIST = {
    ("docs/25-TRUTH-AND-BOUNDS.md", "60 tests"): "quotes the *earlier* count inside the correction block, on purpose",
    ("docs/25-TRUTH-AND-BOUNDS.md", "61 tests"): "same block, the value it was corrected to at that time",
    ("docs/25-TRUTH-AND-BOUNDS.md", "17 codes"): "the code count before the S8/S9 groups existed",
    ("docs/25-TRUTH-AND-BOUNDS.md", "22 codes"): "the code count after S8, before S9",
    ("docs/25-TRUTH-AND-BOUNDS.md", "4 atoms"): "GDPR Art. 17 has four atoms — a per-provision count, not a tree total",
}

COUNTING = re.compile(r"\b(\d+)\s+(tests?|examples?|atoms?|codes?|refusals?)\b", re.I)


def unregistered_numbers() -> list[dict]:
    """Every count-adjacent number in a living document must be either registered in CLAIMS or explained here."""
    registered: set[tuple[str, str]] = set()
    for claim in CLAIMS:
        registered.add((claim["file"], claim["label"]))
    resolved: dict[str, str] = {}
    if "test_count" not in resolved:
        try:
            resolved["tests"] = str(test_count())
        except ProseProblem:
            resolved["tests"] = "?"
    try:
        numbers = status_numbers()
        for key in ("examples", "atoms", "closed"):
            resolved[key] = str(numbers[key])
    except Exception:  # noqa: BLE001 - a missing status is reported elsewhere
        pass
    try:
        resolved["codes"] = str(refusal_codes())
    except Exception:  # noqa: BLE001
        pass

    problems: list[dict] = []
    for rel in LIVING:
        path = DOCS_ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in COUNTING.finditer(text):
            number, unit = match.group(1), match.group(2).lower()
            phrase = f"{number} {unit}"
            if (rel, phrase) in WHITELIST:
                continue
            key = {"tests": "tests", "test": "tests", "examples": "examples", "example": "examples",
                   "atoms": "atoms", "atom": "atoms", "codes": "codes", "code": "codes",
                   "refusals": "codes", "refusal": "codes"}[unit.lower()]
            expected = resolved.get(key)
            if expected is None:
                continue
            if number == expected:
                continue
            line = text[: match.start()].count("\n") + 1
            problems.append(
                {
                    "kind": "unregistered",
                    "file": rel,
                    "line": line,
                    "detail": f"{phrase!r} is not the tree's {expected!r} and is not whitelisted with a reason",
                }
            )
    return problems


def mirror_numbers() -> list[dict]:
    """README.md is canonical and README.ru.md mirrors it; numbers must not diverge even where words may.

    This is spec §5 rule 0 applied to two files instead of a quote and a corpus: extract the numeric tokens, compare
    the sets, report the difference. Words are allowed to differ in translation; a count is not.
    """
    en, ru = DOCS_ROOT / "README.md", DOCS_ROOT / "README.ru.md"
    if not (en.is_file() and ru.is_file()):
        return []
    # Counts only. An identifier such as 19-PORTFOLIO is not a count, and comparing identifiers would flag a
    # document list that legitimately differs while the mirror catches up — noise that teaches people to ignore
    # this check. Measured counts are what "the mirror may differ in words, never in numbers" was about.
    token = re.compile(r"(\d+)\s+(?:tests?|examples?|atoms?|codes?|files?|refusals?)\b", re.I)
    a = {m.group(1) for m in token.finditer(en.read_text(encoding="utf-8"))}
    b = {m.group(1) for m in token.finditer(ru.read_text(encoding="utf-8"))}
    problems: list[dict] = []
    for missing in sorted(a - b, key=int):
        problems.append({"kind": "mirror", "file": "README.ru.md", "detail": f"{missing} is in README.md but not in the mirror"})
    for extra in sorted(b - a, key=int):
        problems.append({"kind": "mirror", "file": "README.ru.md", "detail": f"{extra} is in the mirror but not in README.md"})
    return problems


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
    problems += unregistered_numbers()
    problems += mirror_numbers()

    if args.json:
        print(json.dumps({"checked": ok, "problems": problems}, ensure_ascii=False, indent=2))
    else:
        for item in ok:
            print(f"ok    {item['file']:<32} {item['label']:<40} = {item['value']}")
        for item in problems:
            if item["kind"] == "mismatch":
                print(f"DRIFT {item['file']:<32} {item['label']:<40} claimed {item['claimed']}, measured {item['measured']}")
                print(f"      reproduce with: {item['command']}")
            elif item["kind"] in {"suite-red", "unregistered", "mirror"}:
                print(f"{item['kind'].upper():<5} {item['file']}:{item.get('line', '-')}  {item['detail']}")
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
