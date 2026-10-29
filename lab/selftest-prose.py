"""Self-test for lab/check-prose-numbers.py — every registered claim must be able to go red.

The first version of this file tested three things and called it a self-test: the base pass, one mutated number, and
one stale phrase. An audit pointed out the consequence — two of the three registered claims and one resolver had
never been seen failing, so their green meant nothing.

This version derives the checks from the guard itself: one mutation per claim, the suite-green rule tested with
synthetic output, and the stale-phrase, unregistered and mirror paths. The number of checks is computed, not asserted.

Run: python lab/selftest-prose.py
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "lab" / "check-prose-numbers.py"
FILES = ["README.md", "README.ru.md", "docs/25-TRUTH-AND-BOUNDS.md", "docs/30-REPO-WALK.md", "docs/11-REFUSAL-CODES.md"]


def load_guard():
    spec = importlib.util.spec_from_file_location("prose_guard", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def measure_tests() -> int:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "run_tests.py")], capture_output=True, text=True, encoding="utf-8"
    )
    match = re.search(r"Ran (\d+) tests?", proc.stderr + proc.stdout)
    if not match:
        raise SystemExit("selftest-prose: could not read the test count")
    return int(match.group(1))


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
        if not src.is_file():
            continue
        dst = tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return tmp


def main() -> int:
    guard = load_guard()
    tests = measure_tests()
    print(f"     measured {tests} tests once, reused across the mutations")

    checks = 0
    failures = 0

    def expect(name: str, condition: bool, detail: str = "") -> None:
        nonlocal checks, failures
        checks += 1
        print(f"ok   {name}" if condition else f"FAIL {name} {detail}")
        if not condition:
            failures += 1

    # the suite-green rule, without running anything
    green, _ = guard.suite_is_green(0, "Ran 74 tests in 1.0s\n\nOK\n")
    expect("G1 a green run with OK counts as passing", green)
    red_rc, _ = guard.suite_is_green(1, "Ran 74 tests in 1.0s\n\nOK\n")
    expect("G2 a non-zero exit is not passing, even if OK was printed", not red_rc)
    red_ok, _ = guard.suite_is_green(0, "Ran 74 tests in 1.0s\n\nFAILED (failures=1)\n")
    expect("G3 a run without OK is not passing, even with exit 0", not red_ok)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = shadow(Path(tmpdir))
        rc, out = run(tmp, tests)
        expect("S the shadow copy unchanged passes", rc == 0, out[-600:])

        # one mutation per registered claim: whatever number the claim matches becomes 999
        for claim in guard.CLAIMS:
            path = tmp / claim["file"]
            if not path.is_file():
                expect(f"C {claim['label']}: file present", False)
                continue
            text = path.read_text(encoding="utf-8")
            match = re.search(claim["pattern"], text)
            if not match:
                expect(f"C {claim['label']}: claim matched", False, "the guard's own pattern found nothing")
                continue
            number = match.group(1)
            mutated = text[: match.start()] + text[match.start() : match.end()].replace(number, "999", 1) + text[match.end() :]
            path.write_text(mutated, encoding="utf-8", newline="")
            rc, out = run(tmp, tests)
            expect(f"C {claim['label']}: a wrong number is caught", rc == 1 and "999" in out)
            path.write_text(text, encoding="utf-8", newline="")

        readme = tmp / "README.md"
        original = readme.read_text(encoding="utf-8")
        readme.write_text(original + "\n`CHECKED` because coverage is below threshold.\n", encoding="utf-8", newline="")
        rc, out = run(tmp, tests)
        expect("F a stale phrase is caught", rc == 1 and "STALE" in out)
        readme.write_text(original, encoding="utf-8", newline="")

        doc = tmp / "docs" / "25-TRUTH-AND-BOUNDS.md"
        original_doc = doc.read_text(encoding="utf-8")
        doc.write_text(original_doc + "\nThis repository has 4242 examples.\n", encoding="utf-8", newline="")
        rc, out = run(tmp, tests)
        expect("U an unregistered count is caught", rc == 1 and "UNREGISTERED" in out)
        doc.write_text(original_doc, encoding="utf-8", newline="")

        ru = tmp / "README.ru.md"
        original_ru = ru.read_text(encoding="utf-8") if ru.is_file() else ""
        if original_ru:
            ru.write_text(original_ru + "\n77 tests\n", encoding="utf-8", newline="")
            rc, out = run(tmp, tests)
            expect("M a count missing from the mirror is caught", rc == 1 and "MIRROR" in out)
            ru.write_text(original_ru, encoding="utf-8", newline="")

    print(f"\nselftest-prose: {checks - failures}/{checks} checks behaved as required")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
