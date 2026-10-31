"""Compare the Rust canonicaliser with the Python one on every example, byte for byte.

This is the acceptance test ADR-0002 set: the primary implementation earns its status by agreeing with the twin, and
identity is over bytes, so the comparison is of digests rather than of parsed structures.
"""

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUST = ROOT / "rust" / "target" / "release" / "lexspec.exe"
PY = sys.executable


def python_canonical(path: pathlib.Path) -> tuple[str, str]:
    proc = subprocess.run(
        [PY, str(ROOT / "tools" / "lexcheck.py"), str(path), "--canonical"],
        capture_output=True, text=True, encoding="utf-8",
    )
    lines = proc.stdout.splitlines()
    digest = next((line.split(" ", 1)[1] for line in lines if line.startswith("sha256 ")), "")
    return "\n".join(lines[:-1]), digest


def rust_canonical(path: pathlib.Path) -> tuple[str, str]:
    proc = subprocess.run([str(RUST), "canonical", str(path)], capture_output=True, text=True, encoding="utf-8")
    lines = proc.stdout.splitlines()
    digest = next((line.split(" ", 1)[1] for line in lines if line.startswith("sha256 ")), "")
    return "\n".join(lines[:-1]), digest


def main() -> int:
    if not RUST.is_file():
        print(f"missing binary: {RUST}", file=sys.stderr)
        return 2
    agreement = 0
    disagreements = []
    for path in sorted((ROOT / "examples").glob("*.lex.json")):
        py_text, py_digest = python_canonical(path)
        rs_text, rs_digest = rust_canonical(path)
        if py_digest == rs_digest and py_text == rs_text:
            agreement += 1
            print(f"ok    {path.name:<42} {py_digest[:16]}")
        else:
            disagreements.append(path.name)
            print(f"DIFF  {path.name:<42} rust={rs_digest[:16]} python={py_digest[:16]}")
            if py_text != rs_text:
                for index, (a, b) in enumerate(zip(py_text, rs_text)):
                    if a != b:
                        print(f"      first byte difference at {index}: python={py_text[index:index + 40]!r}")
                        print(f"                                        rust  ={rs_text[index:index + 40]!r}")
                        break
    print(f"\nbyte-identical: {agreement}/{agreement + len(disagreements)}")
    return 0 if not disagreements else 1


if __name__ == "__main__":
    raise SystemExit(main())
