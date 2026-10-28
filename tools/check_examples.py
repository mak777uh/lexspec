#!/usr/bin/env python3
"""check_examples — assert every example's verdict against a recorded expectation.

Why this is a separate tool from tests/run_tests.py: the workflow needs one
command that answers "does the published behaviour still match the published
table?", and a human needs the same command locally. tests/expected.json is the
table; this file compares reality with it and prints the diff.

The table is *generated* (``--write``) from a real run and then *asserted*. That
order matters: a verdict typed by hand is a claim, a verdict captured from the
checker and re-asserted on every push is a measurement. Regenerating the table to
make a red build green is the one thing this tool cannot protect you from —
AGENTS.md rule 3 covers it, and the diff is visible in review.

Exit codes: 0 all expectations hold, 1 mismatch, 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "tools" / "lexcheck.py"
EXPECTED = ROOT / "tests" / "expected.json"
DEFAULT_THRESHOLD = 0.8


def run_checker(example: Path, threshold: float) -> tuple[int, dict | None]:
    """Run the checker as a subprocess: the test must exercise the CLI, not a helper."""
    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            str(example.relative_to(ROOT)),
            "--json",
            "--coverage-threshold",
            str(threshold),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    report = None
    if completed.stdout.strip():
        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError:
            report = None
    return completed.returncode, report


def measure(threshold: float) -> dict:
    """Measure every example; the only source of truth for the table."""
    examples = sorted((ROOT / "examples").glob("*.lex.json"))
    measured = {}
    for example in examples:
        code, report = run_checker(example, threshold)
        if report is None:
            raise SystemExit(f"check_examples: no JSON report for {example.name} (exit {code})")
        measured[example.name] = {
            "verdict": report["verdict"],
            "exit_code": code,
            "coverage": report["coverage"],
            "codes": sorted({finding["code"] for finding in report["findings"]}),
        }
    return {"coverage_threshold": threshold, "examples": measured}


def compare(expected: dict, measured: dict) -> list[str]:
    problems = []
    expected_examples = expected.get("examples", {})
    measured_examples = measured["examples"]

    for name in sorted(measured_examples):
        if name not in expected_examples:
            problems.append(f"{name}: not recorded in tests/expected.json (regenerate with --write)")
    for name in sorted(expected_examples):
        if name not in measured_examples:
            problems.append(f"{name}: recorded in tests/expected.json but no such example file")

    for name in sorted(set(expected_examples) & set(measured_examples)):
        want = expected_examples[name]
        got = measured_examples[name]
        if want.get("verdict") != got["verdict"]:
            problems.append(f"{name}: verdict {got['verdict']!r}, expected {want.get('verdict')!r}")
        if want.get("exit_code") != got["exit_code"]:
            problems.append(f"{name}: exit {got['exit_code']}, expected {want.get('exit_code')}")
        if abs(float(want.get("coverage", -1)) - got["coverage"]) > 1e-9:
            problems.append(f"{name}: coverage {got['coverage']}, expected {want.get('coverage')}")
        if sorted(want.get("codes", [])) != got["codes"]:
            problems.append(
                f"{name}: codes {got['codes']}, expected {sorted(want.get('codes', []))}"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_examples",
        description="Assert that examples/*.lex.json produce the verdicts recorded in tests/expected.json.",
    )
    parser.add_argument("--write", action="store_true", help="(re)generate tests/expected.json from a real run")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"coverage threshold used for every example (default {DEFAULT_THRESHOLD})",
    )
    args = parser.parse_args(argv)

    if not (0.0 <= args.threshold <= 1.0):
        print("check_examples: error: --threshold must be between 0.0 and 1.0", file=sys.stderr)
        return 2
    if not CHECKER.is_file():
        print(f"check_examples: error: {CHECKER.relative_to(ROOT)} is missing", file=sys.stderr)
        return 2

    measured = measure(args.threshold)

    if args.write:
        EXPECTED.parent.mkdir(parents=True, exist_ok=True)
        EXPECTED.write_text(
            json.dumps(measured, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",  # write_text defaults to os.linesep, which is CRLF on Windows
        )
        print(f"check_examples: wrote {EXPECTED.relative_to(ROOT).as_posix()} from a real run "
              f"({len(measured['examples'])} examples, threshold {args.threshold})")
        return 0

    if not EXPECTED.is_file():
        print(f"check_examples: error: {EXPECTED.relative_to(ROOT)} is missing; run with --write", file=sys.stderr)
        return 2
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

    if abs(float(expected.get("coverage_threshold", -1)) - args.threshold) > 1e-9:
        print(
            "check_examples: error: tests/expected.json was recorded at threshold "
            f"{expected.get('coverage_threshold')}, but this run uses {args.threshold}; "
            "a verdict quoted without its threshold is not reproducible",
            file=sys.stderr,
        )
        return 2

    problems = compare(expected, measured)

    width = max((len(name) for name in measured["examples"]), default=0)
    print(f"threshold {args.threshold}")
    for name, result in measured["examples"].items():
        codes = ",".join(result["codes"]) or "-"
        print(f"  {name:<{width}}  {result['verdict']:<16} exit {result['exit_code']}  "
              f"coverage {result['coverage']:.3f}  {codes}")

    if problems:
        print(f"check_examples: {len(problems)} mismatch(es)")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print(f"check_examples: {len(measured['examples'])} examples match the recorded expectations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
