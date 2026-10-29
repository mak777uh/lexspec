"""Self-test for lab/check-prose-numbers.py: the guard must fail when the prose drifts.

A checker that only ever prints "ok" is decoration. This builds a shadow copy of the documents that carry the
registered claims, confirms the copy passes unchanged, then mutates one number and one stale phrase and confirms the
checker catches both.

Run: python lab/selftest-prose.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "lab" / "check-prose-numbers.py"
FILES = ["README.md", "docs/25-TRUTH-AND-BOUNDS.md", "docs/30-REPO-WALK.md", "docs/11-REFUSAL-CODES.md"]


def measure_tests() -> int:
    proc = subprocess.run([sys.executable, str(ROOT / "tests" / "run_tests.py")], capture_output=True, text=True, encoding="utf-8")
    m = re.search(r"Ran (\d+) tests?", proc.stderr + proc.stdout)
    if not m:
        raise SystemExit("selftest-prose: could not read the test count")
    return int(m.group(1))


def run(docs_root: Path, tests: int) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--docs-root", str(docs_root), "--test-count", str(tests)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc.returncode, proc.stdout + proc.stderr


def shadow(tmp: Path) -> Path:
    for rel in FILES:
        src = ROOT / rel
        dst = tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return tmp


def main() -> int:
    failures = 0
    tests = measure_tests()
    print(f"     measured {tests} tests once, reused across the mutations")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = shadow(Path(tmpdir))
        code, out = run(tmp, tests)
        if code == 0:
            print("ok   S shadow copy unchanged passes")
        else:
            print("FAIL S shadow copy unchanged should pass")
            print(out[-1200:])
            failures += 1

        # mutation 1: a number in prose that the tree contradicts
        doc = tmp / "docs" / "25-TRUTH-AND-BOUNDS.md"
        text = doc.read_text(encoding="utf-8")
        # mutate whatever the claim currently says, not a literal from the past: a self-test that hardcodes
        # the number it is testing silently stops testing anything the moment the prose is updated (CI caught
        # exactly that on 2026-10-29).
        mutated, n = re.subn(r"→ \d+ tests pass", "→ 999 tests pass", text)
        if n != 1:
            print(f"FAIL M1 the tests claim was not found to mutate (n={n})")
            failures += 1
        doc.write_text(mutated, encoding="utf-8", newline="")
        code, out = run(tmp, tests)
        if code == 1 and "999" in out:
            print("ok   M1 a wrong test count is caught")
        else:
            print("FAIL M1 a wrong test count was not caught")
            failures += 1

        # mutation 2: a phrase that a decision made stale
        readme = tmp / "README.md"
        text = readme.read_text(encoding="utf-8")
        readme.write_text(
            text + "\n`CHECKED` because coverage is below threshold.\n", encoding="utf-8", newline=""
        )
        code, out = run(tmp, tests)
        if code == 1 and "STALE" in out:
            print("ok   M2 a stale phrase from a superseded decision is caught")
        else:
            print("FAIL M2 a stale phrase was not caught")
            failures += 1

    total = 3
    print(f"\nselftest-prose: {total - failures}/{total} checks behaved as required")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
