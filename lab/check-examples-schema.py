"""check-examples-schema.py — the shipped examples must validate against the published schema.

Written because an external audit found three of twelve examples violating `schemas/statement-0.1.json` while every
gate was green: the schema was documentation, and nothing asserted that the data shipped with the repository obeys it.
A schema nobody validates against is a description of an intention.

Usage
    python lab/check-examples-schema.py          # validate all examples
    python lab/check-examples-schema.py --json   # machine-readable

Exit: 0 all examples validate, 1 at least one does not, 2 the validator is unavailable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "statement-0.1.json"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate examples/*.lex.json against the published schema.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        import jsonschema
    except ImportError:
        print("check-examples-schema: jsonschema is not installed (python -m pip install jsonschema)", file=sys.stderr)
        return 2

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)

    problems: list[dict] = []
    checked = 0
    for path in sorted((ROOT / "examples").glob("*.lex.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        checked += 1
        for error in sorted(validator_cls(schema).iter_errors(document), key=lambda e: list(e.path)):
            problems.append(
                {
                    "file": path.name,
                    "path": "/".join(str(p) for p in error.path),
                    "message": error.message,
                }
            )

    if args.json:
        print(json.dumps({"checked": checked, "problems": problems}, ensure_ascii=False, indent=2))
    else:
        for item in problems:
            print(f"INVALID {item['file']}: {item['path']} -> {item['message'][:160]}")
        print(f"\ncheck-examples-schema: {checked} example(s), {len(problems)} violation(s)")

    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
