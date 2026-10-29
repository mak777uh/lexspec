"""Self-test for lab/check-hohfeld.py: the algebra check must fail on a table that only looks right.

Three mutations, each the kind a careful editor could make:

  M1 a correlative cell changed inside its square      -> L2 (C is not an involution) must fire
  M2 an opposite moved into the other square           -> L7 (square not closed) must fire
  M3 the code's table diverges from the spec's         -> L8 must fire

If any mutation passes, the guard is decoration.

Run: python lab/selftest-hohfeld.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "lab" / "check-hohfeld.py"
SPEC = ROOT / "docs" / "10-SPEC-v0.1.md"
LEXCHECK = ROOT / "tools" / "lexcheck.py"


def run(spec: Path, code: Path) -> tuple[int, str]:
    env = dict(os.environ, LEXSPEC_HOHFELD_SPEC=str(spec), LEXSPEC_HOHFELD_CHECKER=str(code))
    proc = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True, encoding="utf-8", env=env)
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        spec = tmp / "spec.md"
        code = tmp / "lexcheck.py"
        shutil.copyfile(SPEC, spec)
        shutil.copyfile(LEXCHECK, code)

        rc, out = run(spec, code)
        if rc == 0:
            print("ok   S the real table passes")
        else:
            print("FAIL S the real table should pass")
            print(out[-800:])
            failures += 1

        # M1: right's correlative is duty; claiming privilege breaks the involution
        original = spec.read_text(encoding="utf-8")
        spec.write_text(original.replace("| `right` | `duty` | `privilege` |", "| `right` | `privilege` | `privilege` |"),
                        encoding="utf-8", newline="")
        rc, out = run(spec, code)
        if rc == 1 and "L2" in out:
            print("ok   M1 a broken correlative involution is caught")
        else:
            print("FAIL M1 L2 did not fire")
            failures += 1

        # M2: right's opposite moved to the power square
        spec.write_text(original.replace("| `right` | `duty` | `privilege` |", "| `right` | `duty` | `immunity` |"),
                        encoding="utf-8", newline="")
        rc, out = run(spec, code)
        if rc == 1 and ("L7" in out or "L4" in out):
            print("ok   M2 an opposite outside its square is caught")
        else:
            print("FAIL M2 neither L7 nor L4 fired")
            failures += 1

        # M3: spec restored, code diverges
        spec.write_text(original, encoding="utf-8", newline="")
        code_text = code.read_text(encoding="utf-8")
        code.write_text(code_text.replace('"right": "duty",', '"right": "liability",', 1), encoding="utf-8", newline="")
        rc, out = run(spec, code)
        if rc == 1 and "L8" in out:
            print("ok   M3 a code table that disagrees with the spec is caught")
        else:
            print("FAIL M3 L8 did not fire")
            failures += 1

    total = 4
    print(f"\nselftest-hohfeld: {total - failures}/{total} checks behaved as required")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
