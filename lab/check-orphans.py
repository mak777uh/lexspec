"""check-orphans.py — documents that nothing links to are memory clutter with a version history.

A file nobody references is not read, and a file that is not read drifts: it keeps describing a repository that has
moved. This is the cheapest guard in the set — a link graph over `docs/`, `lab/` and `interop/` — and it earned its
place immediately: five documents had no inbound link at all, including the legal read that produced four of our atoms.

The check is one-directional on purpose (who links *to* this file). Outbound dead links are `lab/check-links`-style
work done by the temp link checker in CI; here the question is only whether a document is reachable at all.

Usage
    python lab/check-orphans.py
    python lab/check-orphans.py --json

Exit: 0 every document is reachable, 1 at least one is not.
"""

import argparse
import json
import pathlib
import sys
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)]+)\)")


def targets(path: pathlib.Path) -> set[str]:
    out = set()
    for raw in LINK.findall(path.read_text(encoding="utf-8", errors="replace")):
        target = raw.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            out.add(resolved.relative_to(ROOT).as_posix())
        except ValueError:
            out.add(str(resolved))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Documents nothing links to.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    files = sorted(
        [p for p in (ROOT / "docs").glob("*.md")]
        + [p for p in (ROOT / "lab").rglob("*.md")]
        + [p for p in (ROOT / "interop").glob("*.md")]
    )
    graph: dict[str, set[str]] = {}
    for path in files:
        graph[path.relative_to(ROOT).as_posix()] = targets(path)
    # README and the guards count as roots
    roots = ["README.md", "README.ru.md", "interop/README.md", ".github/workflows/guards.yml"]
    for extra in (ROOT / "README.md", ROOT / ".github" / "workflows" / "guards.yml"):
        if extra.is_file():
            graph[extra.relative_to(ROOT).as_posix()] = targets(extra)

    inbound: dict[str, int] = {name: 0 for name in graph}
    for source, targets_ in graph.items():
        for target in targets_:
            if target in inbound and target != source:
                inbound[target] += 1

    orphans = sorted(name for name, count in inbound.items() if count == 0 and name not in roots)
    if args.json:
        print(json.dumps({"documents": len(files), "orphans": orphans}, ensure_ascii=False, indent=2))
    else:
        for name in orphans:
            print(f"ORPHAN {name}")
        print(f"\ncheck-orphans: {len(files)} document(s), {len(orphans)} unreachable")
    return 0 if not orphans else 1


if __name__ == "__main__":
    raise SystemExit(main())
