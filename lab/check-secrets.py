#!/usr/bin/env python3
"""check-secrets — refuse credential-shaped strings and machine-local paths.

Why this exists: a repository that publishes a verdict about documents is only
as trustworthy as its own commits, and one pasted token makes every later claim
worthless. This scan is deliberately dumb and deliberately loud: it does not try
to decide whether a match is "probably fine". It exits 1 and names the line.

Two rules that are worth reading before adding a pattern:

  * Patterns are assembled from fragments (``_p("gh", "p_")``) so that this file
    does not match itself. A scanner that flags its own source is noise, and the
    obvious fix — exempting itself — would hide a real hit in here one day.
  * A 64-character hex string is *not* reported when its line names a digest
    (``sha256``, ``text_sha256``, ``checksum``, ``digest``, ``hash``). LexSpec
    statements are full of sha256 values by design, and a hash of public bytes
    is not a credential. The exemption is this narrow on purpose: it is visible
    in review, and any other line with 64 hex characters is still a finding.

No network, no git: the file list is a plain walk, minus .git and build output,
so this runs identically on a developer machine and in CI. "Tracked files" is
approximated by "text files in the working tree" — a file that is untracked but
present can still be pushed by accident, and scanning it is the safer error.

Exit codes: 0 clean, 1 findings, 2 usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Directories that never contain hand-written text worth scanning.
PRUNE_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache"}

# Extensions that are binary or generated; reading them as text produces noise.
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".bz2",
    ".xz", ".7z", ".tar", ".pyc", ".pyd", ".so", ".dll", ".exe", ".bin", ".woff",
    ".woff2", ".ttf", ".otf", ".mp4", ".mp3", ".wav", ".xlsx", ".docx", ".pptx",
}

MAX_BYTES = 2 * 1024 * 1024


def _p(*parts: str) -> str:
    """Join pattern fragments so this file's own source does not match them."""
    return "".join(parts)


# (pattern, label). Order decides which label a line is reported under.
PATTERNS = [
    (re.compile(_p("gh", "p_") + r"[A-Za-z0-9]{20,}"), "GitHub personal access token"),
    (re.compile(_p("github", "_pat_") + r"[A-Za-z0-9_]{20,}"), "GitHub fine-grained token"),
    (re.compile(_p("sk", "-") + r"[A-Za-z0-9]{20,}"), "API secret key"),
    (re.compile(_p("AK", "IA") + r"[0-9A-Z]{16}"), "AWS access key id"),
    (
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
        "private key block",
    ),
    (re.compile(r"\b[0-9a-fA-F]{64}\b"), "64-hex key or digest"),
    (re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/](?![\\/])"), "absolute Windows path"),
    (
        re.compile(r"(?<![\w.])/(?:home|Users|root|tmp|var|opt|etc|mnt|srv)/"),
        "absolute Unix path",
    ),
]

# A digest is a value, not a credential, when the line says so. The pattern is
# deliberately not word-bounded on the left: the real lines read
# "statement_sha256" and "text_sha256", and a `\bsha256\b` exemption would miss
# both — which is how this file's first version reported every digest in its own
# SELFTEST.md. Kept to "sha256/sha-256/checksum/digest/hash" so the exemption
# stays narrow enough to see in review.
DIGEST_CONTEXT = re.compile(r"(?i)(?:sha-?256|checksum|digest|\bhash\b)")


def iter_files(root: Path):
    """Yield candidate text files, deterministic order, no build output."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in PRUNE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
        except OSError:
            continue
        yield path


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Return [(line_number, label, line_text)] for every match in one file."""
    try:
        raw = path.read_bytes()
    except OSError:
        return []
    if b"\x00" in raw[:4096]:  # NUL bytes: binary, not a document we can read
        return []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return []

    hits: list[tuple[int, str, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for pattern, label in PATTERNS:
            if not pattern.search(line):
                continue
            if label == "64-hex key or digest" and DIGEST_CONTEXT.search(line):
                continue  # sha256 of public bytes, and the line says so
            hits.append((number, label, line.strip()[:160]))
            break  # one label per line keeps the output readable
    return hits


def scan(root: Path) -> tuple[list[str], int]:
    """Return (report lines, scanned file count)."""
    lines: list[str] = []
    scanned = 0
    for path in iter_files(root):
        scanned += 1
        relative = path.relative_to(root).as_posix()
        for number, label, excerpt in scan_file(path):
            lines.append(f"{relative}:{number}: {label}: {excerpt}")
    return lines, scanned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check-secrets",
        description="Scan text files for credential-shaped strings and machine-local paths.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="directory to scan (default: the repository root, i.e. this file's grandparent)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"check-secrets: error: {root} is not a directory", file=sys.stderr)
        return 2

    findings, scanned = scan(root)
    if findings:
        for line in findings:
            print(line)
        files = len({line.split(":", 1)[0] for line in findings})
        print(f"check-secrets: {len(findings)} finding(s) in {files} file(s); scanned {scanned}")
        return 1

    print(f"check-secrets: clean ({scanned} text files scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
