"""check-hohfeld.py — is our eight-position table actually the Hohfeld algebra, or eight words we like?

Nobody in the family has machine-checked this: flowguard's review says so explicitly ("комбинаторику
хохфельдовских позиций я не проверял"), and our own guard only compares prose with code — it compares the two
tables' *cells*, not the structure they are supposed to satisfy.

A table of eight positions with two maps can be wrong in ways that copy-editing cannot see: a correlative that is
not an involution, an opposite that drifts outside its square, a pair that quietly becomes a triple. This script
reads the table from the spec, reads the code's copy, and checks both against the algebra.

The laws (Hohfeld 1913/1917, and the standard reading of the four squares):

  L1  totality and closure: every position has exactly one correlative and one opposite, and both are among the eight
  L2  correlative is an involution: C(C(x)) = x
  L3  opposite is an involution:    O(O(x)) = x
  L4  the square commutes:          O(C(x)) = C(O(x))
  L5  no fixed points:              C(x) != x and O(x) != x
  L6  pairs partition:              the four correlative pairs are disjoint and cover the eight
  L7  squares are closed:           {right, duty, no-right, privilege} and {power, liability, disability, immunity}
                                    are each closed under C and O, and no position sits in both
  L8  spec and code agree cell by cell

L4 is the one that catches a plausible-looking but wrong table: it says that going "across" and then "around" the
square lands in the same place as going around and then across. A table with one cell edited usually still satisfies
L2 and L3 and fails L4.

Usage
    python lab/check-hohfeld.py            # human output
    python lab/check-hohfeld.py --json

Exit: 0 all laws hold, 1 a law is violated, 2 the table could not be read.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "10-SPEC-v0.1.md"
CHECKER = ROOT / "tools" / "lexcheck.py"
# overridable, so lab/selftest-hohfeld.py can point at a mutated shadow copy
SPEC = Path(__import__("os").environ.get("LEXSPEC_HOHFELD_SPEC", SPEC))
CHECKER = Path(__import__("os").environ.get("LEXSPEC_HOHFELD_CHECKER", CHECKER))

ROW = re.compile(r"^\|\s*`([a-z-]+)`\s*\|\s*`([a-z-]+)`\s*\|\s*`([a-z-]+)`\s*\|\s*$", re.M)
SQUARES = (
    {"right", "duty", "no-right", "privilege"},
    {"power", "liability", "disability", "immunity"},
)


def from_spec() -> tuple[dict[str, str], dict[str, str]]:
    text = SPEC.read_text(encoding="utf-8")
    start = text.index("## §4 The Hohfeld layer")
    end = text.find("\n## ", start + 10)
    body = text[start:end if end != -1 else len(text)]
    corr: dict[str, str] = {}
    opp: dict[str, str] = {}
    for position, correlative, opposite in ROW.findall(body):
        corr[position] = correlative
        opp[position] = opposite
    if len(corr) != 8:
        raise SystemExit(f"check-hohfeld: read {len(corr)} positions from the spec, expected 8")
    return corr, opp


def from_code() -> tuple[dict[str, str], dict[str, str]]:
    spec = importlib.util.spec_from_file_location("lexcheck", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return dict(module.CORRELATIVE), dict(module.OPPOSITE)


def laws(corr: dict[str, str], opp: dict[str, str]) -> list[dict]:
    positions = sorted(corr)
    violations: list[dict] = []

    def fail(law: str, detail: str) -> None:
        violations.append({"law": law, "detail": detail})

    # L1
    for x in positions:
        if x not in opp:
            fail("L1", f"{x} has no opposite")
        for name, m in (("correlative", corr), ("opposite", opp)):
            if m.get(x) not in set(positions):
                fail("L1", f"{name} of {x} is {m.get(x)!r}, which is not one of the eight")

    # L2, L3
    for x in positions:
        if corr.get(corr.get(x)) != x:
            fail("L2", f"correlative is not an involution at {x}: C(C({x}))={corr.get(corr.get(x))}")
        if opp.get(opp.get(x)) != x:
            fail("L3", f"opposite is not an involution at {x}: O(O({x}))={opp.get(opp.get(x))}")

    # L4
    for x in positions:
        left, right = opp.get(corr.get(x)), corr.get(opp.get(x))
        if left != right:
            fail("L4", f"the square does not commute at {x}: O(C({x}))={left}, C(O({x}))={right}")

    # L5
    for x in positions:
        if corr.get(x) == x:
            fail("L5", f"correlative of {x} is itself")
        if opp.get(x) == x:
            fail("L5", f"opposite of {x} is itself")

    # L6
    pairs = {frozenset({x, corr.get(x)}) for x in positions}
    if len(pairs) != 4:
        fail("L6", f"expected four correlative pairs, got {len(pairs)}")
    covered = set().union(*pairs) if pairs else set()
    if covered != set(positions):
        fail("L6", f"correlative pairs cover {sorted(covered)}, not the eight positions")

    # L7
    for i, square in enumerate(SQUARES):
        missing = square - set(positions)
        if missing:
            fail("L7", f"square {i} names positions that do not exist: {sorted(missing)}")
            continue
        for x in square:
            if corr.get(x) not in square:
                fail("L7", f"square {i} is not closed under correlative: C({x})={corr.get(x)}")
            if opp.get(x) not in square:
                fail("L7", f"square {i} is not closed under opposite: O({x})={opp.get(x)}")
    if SQUARES[0] & SQUARES[1]:
        fail("L7", f"the two squares overlap: {sorted(SQUARES[0] & SQUARES[1])}")
    if SQUARES[0] | SQUARES[1] != set(positions):
        fail("L7", f"the squares do not cover the eight positions: missing {sorted(set(positions) - (SQUARES[0] | SQUARES[1]))}")

    return violations


def compare(spec_c: dict[str, str], spec_o: dict[str, str], code_c: dict[str, str], code_o: dict[str, str]) -> list[dict]:
    out: list[dict] = []
    for x in sorted(set(spec_c) | set(code_c)):
        if spec_c.get(x) != code_c.get(x):
            out.append({"law": "L8", "detail": f"correlative of {x}: spec {spec_c.get(x)!r}, code {code_c.get(x)!r}"})
        if spec_o.get(x) != code_o.get(x):
            out.append({"law": "L8", "detail": f"opposite of {x}: spec {spec_o.get(x)!r}, code {code_o.get(x)!r}"})
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check the eight Hohfeld positions against the algebra they claim.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        spec_c, spec_o = from_spec()
        code_c, code_o = from_code()
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2

    problems = laws(spec_c, spec_o) + compare(spec_c, spec_o, code_c, code_o)

    if args.json:
        print(json.dumps({"positions": sorted(spec_c), "violations": problems}, ensure_ascii=False, indent=2))
    else:
        print("positions:", ", ".join(sorted(spec_c)))
        print("correlative pairs:", ", ".join(sorted("{" + a + ", " + b + "}" for a, b in
                                                      ((x, spec_c[x]) for x in sorted(spec_c) if x < spec_c[x]))))
        if problems:
            for p in problems:
                print(f"  VIOLATION {p['law']}: {p['detail']}")
        else:
            print("laws: L1 totality, L2 C-involution, L3 O-involution, L4 commutation, L5 no fixed points,")
            print("      L6 pairs partition, L7 squares closed, L8 spec==code - all hold")

    if problems:
        print(f"\ncheck-hohfeld: {len(problems)} violation(s)")
        return 1
    print("\ncheck-hohfeld: the table is the algebra")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
