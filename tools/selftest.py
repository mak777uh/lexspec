#!/usr/bin/env python3
"""selftest — regenerate tools/SELFTEST.md from a real run.

Why a generator: the quality bar for this repository is that every number in a
document comes from a command (AGENTS.md rule 1). Hand-copying a transcript is
how a document ends up claiming something nobody ran. This script runs each
command, captures stdout/stderr and the exit code, and writes the markdown.
Re-running it after a change refreshes the evidence instead of editing it.

What it does NOT do: decide whether the output is good. A failing command is
recorded with its non-zero exit code and that is the honest result.

Exit codes: 0 if every recorded command matched its expected exit code,
1 otherwise (so a stale expectation is visible in CI, not only in the markdown).
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "tools" / "SELFTEST.md"

# (heading, argv, expected exit code). Order is the order a reader needs.
COMMANDS = [
    ("environment", [sys.executable, "--version"], 0),
    ("example 01 — the happy path", [sys.executable, "tools/lexcheck.py", "examples/01-delivery-ok.lex.json"], 0),
    ("example 02 — opposite positions on one tuple", [sys.executable, "tools/lexcheck.py", "examples/02-opposite-conflict.lex.json"], 1),
    ("example 03 — a span that is not in the pinned text", [sys.executable, "tools/lexcheck.py", "examples/03-no-anchor.lex.json"], 1),
    ("example 04 — a correlative written on the same side", [sys.executable, "tools/lexcheck.py", "examples/04-unresolved-conflict.lex.json"], 1),
    ("example 05 — an open term, declared", [sys.executable, "tools/lexcheck.py", "examples/05-open-term.lex.json"], 0),
    ("example 06 — coverage below the threshold", [sys.executable, "tools/lexcheck.py", "examples/06-thin-coverage.lex.json"], 0),
    ("machine-readable report for example 01", [sys.executable, "tools/lexcheck.py", "examples/01-delivery-ok.lex.json", "--json"], 0),
    ("canonical form and digest", [sys.executable, "tools/lexcheck.py", "examples/01-delivery-ok.lex.json", "--canonical"], 0),
    ("every example against tests/expected.json", [sys.executable, "tools/check_examples.py"], 0),
    (
        "all examples in one invocation (array report, first 3 findings of each)",
        [
            sys.executable,
            "tools/lexcheck.py",
            "examples/01-delivery-ok.lex.json",
            "examples/02-opposite-conflict.lex.json",
            "examples/03-no-anchor.lex.json",
            "--json",
        ],
        1,
    ),
    ("status block", [sys.executable, "tools/lexspec_status.py"], 0),
    ("test suite", [sys.executable, "tests/run_tests.py"], 0),
    ("secret and local-path scan", [sys.executable, "lab/check-secrets.py"], 0),
    ("usage error is exit 2, not a verdict", [sys.executable, "tools/lexcheck.py"], 2),
]


def run(argv: list[str]) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    body = completed.stdout
    if completed.stderr.strip():
        body += ("\n" if body and not body.endswith("\n") else "") + completed.stderr
    return completed.returncode, body.rstrip("\n")


def determinism_note() -> str:
    """Show, rather than assert, that two runs agree byte for byte."""
    argv = [sys.executable, "tools/lexcheck.py", "examples/05-open-term.lex.json", "--json"]
    first = subprocess.run(argv, cwd=str(ROOT), capture_output=True).stdout
    second = subprocess.run(argv, cwd=str(ROOT), capture_output=True).stdout
    same = hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()
    return (
        "Two consecutive `--json` runs of example 05 were compared by sha256: "
        f"**{'identical' if same else 'DIFFERENT'}** "
        f"(`{hashlib.sha256(first).hexdigest()[:16]}…`).\n"
    )


def load_checker():
    spec = importlib.util.spec_from_file_location("lexcheck_for_selftest", ROOT / "tools" / "lexcheck.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def code_coverage(checker) -> tuple[str, list[str]]:
    """Build the `code -> where exercised` table, and report unexercised codes.

    Two different kinds of evidence, and the difference matters:

      * the *example* column comes from actually running each statement and
        reading its findings — a measurement;
      * the *unit test* column comes from finding the code string inside the body
        of a `test_*` function in tests/run_tests.py — a textual attribution, not
        a proof that the assertion fires for the wrong reason. The suite runs
        green in the same file, so a mention inside a test body is asserted
        somewhere; if a code is only mentioned in prose, the table will say the
        code is covered and a reader will be misled. Keeping the column narrow
        ("the body of this test mentions the code") is the honest framing.

    A code with neither is returned as missing, and main() turns that into a
    non-zero exit: an unexercised code is a vocabulary entry nobody can trust.
    """
    by_example: dict[str, list[str]] = {}
    for path in sorted((ROOT / "examples").glob("*.lex.json")):
        code, body = run([sys.executable, "tools/lexcheck.py", f"examples/{path.name}", "--json"])
        if code == 2:
            raise SystemExit(f"selftest: could not read example {path.name}: {body}")
        report = json.loads(body)
        # Path.stem leaves ".lex" on the end; the table reads better without it.
        label = path.name[: -len(".lex.json")]
        for finding in report["findings"]:
            names = by_example.setdefault(finding["code"], [])
            if label not in names:
                names.append(label)

    source = (ROOT / "tests" / "run_tests.py").read_text(encoding="utf-8")
    lines = source.splitlines()
    by_test: dict[str, list[str]] = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            body = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            for code in checker.CODE_ORDER:
                if re.search(r"\b" + re.escape(code) + r"\b", body):
                    by_test.setdefault(code, []).append(node.name)

    rows = []
    missing = []
    for code in checker.CODE_ORDER:
        examples = sorted(by_example.get(code, []))
        tests = sorted(set(by_test.get(code, [])))
        if not examples and not tests:
            missing.append(code)
        rows.append(
            "| `{code}` | {examples} | {tests} |".format(
                code=code,
                examples=", ".join(f"`{name}`" for name in examples) or "—",
                tests=", ".join(f"`{name}`" for name in tests) or "—",
            )
        )

    table = (
        "### code → where it is exercised\n\n"
        "| code | examples (ran now) | unit tests (body mentions the code) |\n"
        "|---|---|---|\n" + "\n".join(rows) + "\n"
    )
    return table, missing


PREAMBLE = """# Self-test — what was actually run, and what it printed

This file is **generated** by `python tools/selftest.py`; editing it by hand is how
a test transcript starts lying. Every block below is real stdout/stderr from the
command in its heading, with its real exit code. Regenerate it after changing a
tool, a schema, an example or the corpus.

Exit codes used throughout: `0` a passing verdict, `1` REFUSED (the checker
worked and the statement did not survive), `2` usage or parse error (nothing to
report on).

## What this does not establish

The evidence below supports exactly one claim: *these files, on this machine, on
this date, produced these bytes*. It does not establish that the checker is
correct, that the encoding is complete, or that any statement is legally valid —
`not_claimed` in every report says the same thing per statement. Specific
boundaries that a reader should not have to discover:

1. **No entailment.** Nothing here proves an atom follows from a provision. S2
   proves that a span exists exactly once in a text pinned by sha256; it does not
   prove the span says what the atom claims.
2. **The corpus is a test excerpt.** `corpus/gk-rf-2026-10-01.txt` is a short
   reconstruction marked `# NOTE: excerpt for testing only`. Its digest makes the
   pin reproducible; it does not make it authoritative. Correctness of the corpus
   outside the pinned revision is explicitly not claimed.
3. **S6 is narrow, and its known false positive is intentional.** It refuses a
   *correlative* written on the same ordered tuple (spec §7). Opposite relations on
   one tuple are S3 and no policy cures them. Two genuine mutual obligations about
   the same action land on one tuple and are also refused: §7 documents this as
   the price of keeping the check combinatorial, not as something to work around.
4. **Date format is S1, not S5.** `docs/11-REFUSAL-CODES.md` lists malformed dates
   under `S5_EMPTY_INTERVAL`, while `docs/10-SPEC-v0.1.md` §2 puts `YYYY-MM-DD` in
   the document model, which is S1. Where the two overlap, this checker assigns the
   defect once: a date that is not a real calendar day is `S1_SCHEMA`, and
   `S5_EMPTY_INTERVAL` is only `from > until`. One defect, one code.
5. **The JSON Schema is documentation; `lexcheck.py` is the executable
   contract.** No `jsonschema` package is allowed, so the validator is
   hand-written. `tests/run_tests.py` compares the two on required fields, the
   atom key set and every enum — not on the regex patterns or `format: date`,
   which are re-implemented (more strictly) in code.
6. **Canonical form is ours, not RFC 8785.** Keys are sorted by Unicode code
   point (Python's `sort_keys`), not by UTF-16 code unit as JCS specifies. Stable
   across platforms and Python 3.11+, and deliberately not claimed to interoperate
   with another canonicalisation scheme.
7. **A Windows clone may legitimately fail** if git rewrites line endings in the
   working tree: `C0_CANON` for statements, `S2_HASH_MISMATCH` for the corpus. The
   repository-side fix (`.gitattributes`) is recorded in
   `lab/2026-10-28-checkout-line-endings.md`; it is a root file this work does not
   own.
8. **Malformed atoms count, loudly.** An atom `S1_SCHEMA` rejected still sits in
   the coverage denominator and still demands an escape, because §8 says a
   malformed atom cannot be closed. A document with one broken atom therefore
   reports `S1_SCHEMA` **and** `OPEN_TERM` **and** `S4_UNDECLARED_ESCAPE` for it.
   That cascade is the spec's arithmetic, not an accident, and it is why the
   examples declare exactly the escapes the checker computes.

The table at the end, `code → where it is exercised`, is generated from the runs
above; a code that appears in neither column makes this script exit non-zero.
"""


def main() -> int:
    sections = []
    failures = []
    for heading, argv, expected in COMMANDS:
        code, body = run(argv)
        if code != expected:
            failures.append(f"{heading}: exit {code}, expected {expected}")
        display = " ".join(_display_arg(argv))
        sections.append(
            f"## {heading}\n\n```text\n$ {display}\n{body}\n\nexit={code}\n```\n"
        )

    checker = load_checker()
    table, unexercised = code_coverage(checker)
    sections.append(table)
    if unexercised:
        failures.append(
            "unexercised codes (no example, no test): " + ", ".join(unexercised)
        )

    sections.append(f"## determinism\n\n{determinism_note()}")

    header = (
        f"<!-- generated by tools/selftest.py on {date.today().isoformat()} -->\n\n"
        f"{PREAMBLE}\n"
        f"Recorded on **{date.today().isoformat()}**, Python "
        f"{sys.version.split()[0]}, working tree `{ROOT.name}` (paths are shown relative to it).\n"
    )
    OUTPUT.write_text(header + "\n" + "\n".join(sections), encoding="utf-8", newline="\n")

    print(f"selftest: wrote {OUTPUT.relative_to(ROOT).as_posix()} ({len(COMMANDS)} commands)")
    exercised = len(checker.CODE_ORDER) - len(unexercised)
    print(f"selftest: codes exercised by an example or a test: {exercised}/{len(checker.CODE_ORDER)}")
    if failures:
        for failure in failures:
            print(f"selftest: MISMATCH {failure}")
        return 1
    print("selftest: every command matched its expected exit code")
    return 0


def _display_arg(argv: list[str]) -> list[str]:
    """Show the command as a reader would type it, without the interpreter's path."""
    shown = list(argv)
    if shown and Path(shown[0]).name.lower().startswith("python"):
        shown[0] = "python"
    return shown


if __name__ == "__main__":
    sys.exit(main())
