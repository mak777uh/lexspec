"""check-guard-catalog.py — is every guard in this repository able to fail, and does anything run it?

Taken from `VecDHT/lab/check-guard-selftests.py`, which states the reason better than we had it: *a guard whose zero
is indistinguishable from "did not look" protects exactly as well as a disabled one.* Its design has three parts
worth copying literally:

  * the catalogue is discovered **from the directory by prefix**, not listed inside this file, so a guard added
    tomorrow enters the count without editing the guard;
  * "no planted-defect mode" and "planted-defect mode not wired into a persistent contour" are **different findings**,
    because the remedies differ;
  * exceptions live in a **baseline with reasons**, and a baseline entry that no longer applies is itself a finding.

That last part is the half we were missing everywhere: our whitelists were write-only.

Usage
    python lab/check-guard-catalog.py
    python lab/check-guard-catalog.py --json

Exit: 0 every guard has both properties or a declared reason, 1 otherwise, 2 the tree could not be read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "guards.yml"
LAB = ROOT / "lab"

# Guard = a file in lab/ named check-*.py (the family's convention) plus the two tools that act as guards.
# The convention is `lab/check-*.py`. tools/lexcheck_twin.py is covered by TwinAgreement inside
# tests/run_tests.py; the suite is not a guard over the tree but the tree's own test rail.
EXTRA_GUARDS: list[str] = []

# Accepted debt, each entry stating why. A pair that stops being true is reported as STALE — an exemption that no
# longer applies is a hole that stays open while looking closed.
BASELINE: dict[str, str] = {
    "check-citations.py": "network-dependent by design; runs weekly, not per push, and a proxy failure must not red the build",
    "check-audit-freshness.py": "needs GitHub API access at review time; it is a pre-publication tool, not a CI gate",
    "check-secrets.py": "wired into CI and self-tested by mutation conventions in the family, but it has no --selftest "
    "mode of its own; the planted-secret check lives in lab/selftest-checkspec.py's shadow tree",
    "check-examples-schema.py": "validates data against the published schema; its failure mode is demonstrated by the "
    "schema's own enum (a value outside it), which the checker tests already cover",
    "check-guard-catalog.py": "bootstraps the catalogue: its own red path is a guard without a selftest or a baseline "
    "entry that stopped applying, both exercised by hand in docs/32 section 3",
}

# A guard has a planted-defect mode if it exposes one itself or has a sibling selftest file.
SELFTEST_FILE = re.compile(r"^selftest-(.+)\.py$")


def guards() -> list[str]:
    found = sorted(p.name for p in LAB.glob("check-*.py"))
    found += [name for name in EXTRA_GUARDS if (ROOT / name).is_file()]
    return found


def code_only(text: str) -> str:
    """Strip comments and string literals: a switch that exists only in prose is speech, not a mechanism."""
    import re as _re

    text = _re.sub(r'(?s)""".*?"""', " ", text)
    text = _re.sub(r"(?s)'''.*?'''", " ", text)
    text = _re.sub(r"(?m)^\s*#.*$", " ", text)
    text = _re.sub(r"(?m)\s+#.*$", " ", text)
    return text


def has_selftest(name: str, sibling_selftests: set[str]) -> bool:
    path = LAB / name if name.startswith("check-") else ROOT / name
    text = code_only(path.read_text(encoding="utf-8", errors="replace"))
    # the switch must be declared as an option or read from the parsed args
    if re.search(r"add_argument\(\s*['\"]--selftest", text) or re.search(r"args\.selftest\b", text):
        return True
    # Our selftests are named loosely (`selftest-checkspec.py` covers `check-spec.py`), so the match is on
    # normalised names: strip non-alphanumerics and the check/selftest prefixes, then look for containment.
    guard_key = re.sub(r"[^a-z0-9]", "", Path(name).stem.lower()).removeprefix("check")
    return any(len(s) >= 4 and s in guard_key for s in sibling_selftests)


def wired(name: str, workflow: str) -> bool:
    return name in workflow


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Every guard must be able to fail, and something must run it.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not WORKFLOW.is_file():
        print("check-guard-catalog: no workflow to read", file=sys.stderr)
        return 2
    workflow = WORKFLOW.read_text(encoding="utf-8")

    sibling_selftests = {
        re.sub(r"[^a-z0-9]", "", q.stem.lower()).removeprefix("selftest").removeprefix("check")
        for q in LAB.glob("selftest-*.py")
    }

    findings: list[dict] = []
    checked: list[str] = []
    all_guards = guards()
    for name in all_guards:
        checked.append(name)
        tested = has_selftest(name, sibling_selftests)
        called = wired(name, workflow)
        excused = BASELINE.get(name)
        if excused and (tested and called):
            findings.append(
                {
                    "kind": "STALE",
                    "guard": name,
                    "detail": f"baseline reason no longer applies ({excused!r}): the guard now has both properties",
                }
            )
            continue
        if excused:
            continue
        if not tested:
            findings.append({"kind": "NO_SELFTEST", "guard": name, "detail": "no planted-defect mode; its zero proves nothing"})
        if not called:
            findings.append({"kind": "UNWIRED", "guard": name, "detail": "nothing in .github/workflows/guards.yml calls it"})

    unused = sorted(set(BASELINE) - set(all_guards))
    for name in unused:
        findings.append({"kind": "STALE", "guard": name, "detail": "baseline names a guard that no longer exists"})

    if args.json:
        print(json.dumps({"checked": checked, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        for name in checked:
            state = "excused" if name in BASELINE else "ok"
            print(f"{state:<8} {name}")
        for item in findings:
            print(f"{item['kind']:<12} {item['guard']}: {item['detail']}")
        print(f"\ncheck-guard-catalog: {len(checked)} guard(s), {len(findings)} finding(s), {len(BASELINE)} excused")

    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
