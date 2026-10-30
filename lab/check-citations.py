"""check-citations.py — are the external sources we cite still alive?

Taken from `cases` (`tools/check_evidence.py`), which states the principle better than we had it: *a case with a
dead link is worse than no case, because it looks like evidence and is not.* Our corpora are hashed, so a dead URL
cannot change a verdict — but our **provenance claim** ("this text came from that address on that date") becomes
unverifiable the moment the address stops answering, and nothing in this repository notices.

What this does not do: it does not verify content, and it cannot. A 200 says the address answers, not that the text
behind it is the same text we hashed.

Two details are copied deliberately, because each was learned the hard way by the repository we took the idea from:

  * 403 counts as **alive but closed** (Cloudflare and friends block bots); only 4xx/5xx/0 count as dead, unless
    `--strict` is given.
  * The binary is resolved with `shutil.which`, not hardcoded: a hardcoded `curl.exe` made that repository's CI
    report every link as dead, so the check was failing for its own reason rather than for a dead source.

Run locally or on a schedule, not on every push: the network is not the repository's business.

    python lab/check-citations.py
    python lab/check-citations.py --strict --timeout 20

Exit: 0 every cited address answered, 1 at least one is dead, 2 curl is unavailable.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CURL = shutil.which("curl.exe") or shutil.which("curl")
DEVNULL = "NUL" if os.name == "nt" else "/dev/null"

URL_RE = re.compile(r"https?://[^\s)\]<>\"']+")
FENCE_RE = re.compile(r"```[\s\S]*?```")

# Files whose links are provenance claims rather than convenience links. Corpus headers carry the address the text
# was taken from; docs/25 and docs/31 name the sources a claim rests on.
SOURCES = ["corpus/*.txt", "docs/25-TRUTH-AND-BOUNDS.md", "docs/31-LONGTAILS.md", "lab/sources.md"]


def links() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            text = path.read_text(encoding="utf-8", errors="replace")
            # fenced blocks are commands, not public addresses
            text = FENCE_RE.sub(" ", text)
            for url in URL_RE.findall(text):
                out.append((path.relative_to(ROOT).as_posix(), url.rstrip(".,;:`\"'")))
    # de-duplicate, keep the first place it is cited
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for where, url in out:
        if url in seen:
            continue
        seen.add(url)
        unique.append((where, url))
    return unique


def fetch_code(url: str, timeout: int, method: str = "GET") -> int:
    cmd = [CURL, "-s", "-o", DEVNULL, "-w", "%{http_code}", "-L", "--max-time", str(timeout),
           "-A", "Mozilla/5.0 (compatible; lexspec-citation-check)"]
    if method == "HEAD":
        cmd.insert(1, "-I")
    cmd.append(url)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15, encoding="utf-8", errors="replace")
        return int((proc.stdout or "0").strip() or 0)
    except Exception:  # noqa: BLE001 - a failure to run is reported as 0, dead
        return 0


def check(url: str, timeout: int) -> int:
    """GET, then HEAD if the first answer looks bad — redirects and bot walls differ per method."""
    code = fetch_code(url, timeout)
    if not (200 <= code < 400):
        alt = fetch_code(url, timeout, "HEAD")
        if 200 <= alt < 400:
            return alt
    return code


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check that the external sources we cite still answer.")
    ap.add_argument("--strict", action="store_true", help="treat 403 as dead")
    ap.add_argument("--timeout", type=int, default=25)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if CURL is None:
        print("check-citations: curl is not available", file=sys.stderr)
        return 2

    rows = []
    dead = 0
    for where, url in links():
        code = check(url, args.timeout)
        alive = 200 <= code < 400 or (code == 403 and not args.strict)
        if not alive:
            dead += 1
        rows.append({"where": where, "url": url, "code": code, "alive": alive})

    if args.json:
        import json

        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            mark = "ok  " if row["alive"] else "DEAD"
            note = " (alive but closed)" if row["code"] == 403 else ""
            print(f"{mark} {row['code']:>3} {row['url']}{note}  [{row['where']}]")
        print(f"\ncheck-citations: {len(rows)} address(es), {dead} dead")

    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
