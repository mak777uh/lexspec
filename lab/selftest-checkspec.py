"""selftest-checkspec.py — prove that check-spec.py actually catches contradictions.

A guard that only ever prints "clean" is decoration. This script builds a throwaway copy of the four inputs,
injects one defect at a time, and asserts that the corresponding check fires. If a mutation is not caught, the
guard is broken, not the repository.

No third-party imports, no network, no writes outside a temporary directory.

Usage: python lab/selftest-checkspec.py
Exit: 0 all mutations caught, 1 a mutation slipped through, 2 usage.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_guard():
    spec = importlib.util.spec_from_file_location("checkspec", ROOT / "lab" / "check-spec.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def run_guard(module, root: Path) -> list[tuple[str, str]]:
    """Point the guard at a shadow tree and collect findings."""
    module.ROOT = root
    module.SPEC = root / "docs" / "10-SPEC-v0.1.md"
    module.CODES = root / "docs" / "11-REFUSAL-CODES.md"
    module.SCHEMA = root / "schemas" / "statement-0.1.json"
    module.CHECKER = root / "tools" / "lexcheck.py"
    module.README = root / "README.md"
    module.EXAMPLES = root / "examples"
    module.findings = []
    for check in (
        module.check_codes,
        module.check_fields,
        module.check_relations,
        module.check_verdicts,
        module.check_examples,
        module.check_glossary,
        module.check_refs,
    ):
        check()
    return module.findings


def shadow() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="lexspec-selfcheck-"))
    for part in ("docs", "schemas", "tools", "examples", "corpus"):
        src = ROOT / part
        if src.is_dir():
            shutil.copytree(src, tmp / part)
    shutil.copy2(ROOT / "README.md", tmp / "README.md")
    return tmp


def mutate_codes(root: Path) -> None:
    """docs/11 catalogues a code the checker cannot emit."""
    p = root / "docs" / "11-REFUSAL-CODES.md"
    p.write_text(p.read_text(encoding="utf-8") + "\n| `S6_PHANTOM_CODE` | invented | — |\n", encoding="utf-8", newline="")


def mutate_field(root: Path) -> None:
    """The schema gains a field the spec does not document."""
    p = root / "schemas" / "statement-0.1.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    doc["properties"]["undocumented_field"] = {"type": "string"}
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")


def mutate_square(root: Path) -> None:
    """The checker's correlative map disagrees with the spec's table."""
    p = root / "tools" / "lexcheck.py"
    src = p.read_text(encoding="utf-8")
    src = src.replace('"right": "duty"', '"right": "privilege"', 1)
    p.write_text(src, encoding="utf-8", newline="")


def mutate_example(root: Path) -> None:
    """An example carries a float, which the canonical form forbids."""
    p = root / "examples" / "01-delivery-ok.lex.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    doc["_selftest_float"] = 1.5
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")


MUTATIONS = [
    ("A codes", mutate_codes, "A"),
    ("B fields", mutate_field, "B"),
    ("D squares", mutate_square, "D"),
    ("F examples", mutate_example, "F"),
]


def main() -> int:
    failures = 0
    for label, mutation, group in MUTATIONS:
        module = load_guard()
        root = shadow()
        try:
            baseline = run_guard(module, root)
            if baseline:
                print(f"FAIL {label}: the shadow tree is not clean before mutation ({len(baseline)} findings)")
                failures += 1
                continue
            mutation(root)
            found = run_guard(module, root)
            caught = [f for f in found if f[0] == group]
            if caught:
                print(f"ok   {label}: caught {caught[0][1][:80]}")
            else:
                print(f"FAIL {label}: mutation not caught (findings: {found or 'none'})")
                failures += 1
        finally:
            shutil.rmtree(root, ignore_errors=True)
    print(f"selftest-checkspec: {len(MUTATIONS) - failures}/{len(MUTATIONS)} mutations caught")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
