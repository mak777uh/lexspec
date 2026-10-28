"""span_hint.py — turn a human quote into the byte-exact span a statement needs.

Why this exists: in two real measurements **6 of 14** candidate quotes failed, and nearly all of them failed
because the source wraps at ~100 characters and a quote transcribed from the screen crosses a line break. The
checker was right to refuse — the quote really was not in the file — but the report could only say "span does not
occur". Round 03 settled the correct procedure (docs/26, W6): normalise first, then match, then report the raw
bytes.

This tool applies the normalisation policy declared in spec §5 rule 0 and prints:

  * whether the quote matches after normalisation,
  * the exact **raw** substring to paste into `anchor.span` (line breaks included),
  * the raw `prefix` and `suffix` that make it unique,
  * how many regions the quote selects, with and without context.

Usage
    python tools/span_hint.py --corpus corpus/x.txt --quote "обязуется передать"
    python tools/span_hint.py --corpus corpus/x.txt --quote-file q.txt --json
    python tools/span_hint.py --corpus corpus/x.txt --quote "…" --context 40

Exit codes
    0  exactly one region is selected with the given context
    1  zero regions, or more than one (the detail says which)
    2  usage error

Standard library only. The normalisation function is exported so that the checker can import it later instead of
keeping a second copy of the same rule.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

WHITESPACE = re.compile(r"\s+")


def normalize_with_map(raw: str) -> tuple[str, list[int]]:
    """Return the normalised text and, for each normalised character, its offset in `raw`.

    The policy (spec §5 rule 0): decode character entities, drop HTML/XML tags, collapse every run of
    whitespace — including line breaks — to a single space, and trim the ends. The map is what lets us report a
    span in raw bytes: without it, normalisation would be a one-way door.
    """
    # 1. strip markup and decode entities, remembering where each surviving char came from
    text = html.unescape(raw)
    text = re.sub(r"<[^>]+>", "", text)

    # `html.unescape` and tag removal change lengths, so rebuild offsets by walking the raw string through the
    # same transformations is not reliable. Instead: map by searching each normalised character forward in raw.
    # For legal corpora (plain text) this is exact; for HTML it is an approximation, and the caller is warned.
    out: list[str] = []
    offsets: list[int] = []
    cursor = 0
    for ch in text:
        found = raw.find(ch, cursor)
        if found == -1:
            # character came from entity decoding or normlisation; attach it to the current cursor
            found = cursor
        else:
            cursor = found + 1
        out.append(ch)
        offsets.append(found)

    # 2. collapse whitespace runs to a single space, keeping the first char's offset for the run
    collapsed: list[str] = []
    cmap: list[int] = []
    i = 0
    while i < len(out):
        if out[i].isspace():
            start = i
            while i < len(out) and out[i].isspace():
                i += 1
            collapsed.append(" ")
            cmap.append(offsets[start])
        else:
            collapsed.append(out[i])
            cmap.append(offsets[i])
            i += 1

    # 3. trim
    text_norm = "".join(collapsed)
    stripped_left = len(text_norm) - len(text_norm.lstrip())
    text_norm = text_norm.strip()
    cmap = cmap[stripped_left : stripped_left + len(text_norm)]
    return text_norm, cmap


def find_regions(haystack: str, needle: str) -> list[int]:
    """All start positions, overlapping included (spec §5 rule 4)."""
    out: list[int] = []
    start = 0
    while True:
        hit = haystack.find(needle, start)
        if hit == -1:
            return out
        out.append(hit)
        start = hit + 1


def raw_slice(raw: str, cmap: list[int], start: int, length: int) -> str:
    first = cmap[start]
    last = cmap[start + length - 1] if length else first
    # extend to the end of the last normalised character's raw extent
    return raw[first : last + 1]


def context_spans(raw: str, cmap: list[int], start: int, length: int, width: int) -> tuple[str, str]:
    a = max(0, start - width)
    b = min(len(cmap), start + length + width)
    prefix = raw_slice(raw, cmap, a, start - a) if a < start else ""
    suffix = raw_slice(raw, cmap, start + length, b - (start + length)) if b > start + length else ""
    return prefix, suffix


def analyse(raw: str, quote: str, context: int) -> dict:
    norm, cmap = normalize_with_map(raw)
    q_norm = WHITESPACE.sub(" ", html.unescape(quote)).strip()
    if not q_norm:
        return {"ok": False, "reason": "empty quote after normalisation"}

    hits = find_regions(norm, q_norm)
    result: dict = {
        "quote_normalised": q_norm,
        "raw_has_quote": q_norm in raw,
        "regions": len(hits),
        "context_width": context,
    }
    if not hits:
        # diagnostic: how far does the beginning match? gives the author something to fix
        probe = q_norm[:60]
        closest = norm.find(probe)
        result.update(
            ok=False,
            reason="quote does not occur after normalisation",
            hint=(
                "the beginning of the quote occurs at normalised offset %d" % closest
                if closest != -1
                else "not even the first 60 characters occur; the quote is from a different revision"
            ),
        )
        return result

    span = raw_slice(raw, cmap, hits[0], len(q_norm))
    prefix, suffix = context_spans(raw, cmap, hits[0], len(q_norm), context)

    # uniqueness with context: how many regions survive prefix+span+suffix
    with_context = 0
    for h in hits:
        p, s = context_spans(raw, cmap, h, len(q_norm), context)
        if p == prefix and s == suffix:
            with_context += 1

    result.update(
        ok=(with_context == 1),
        span=span,
        prefix=prefix,
        suffix=suffix,
        regions_with_context=with_context,
    )
    if with_context > 1:
        result["reason"] = (
            "the quote and its %d-character context still select %d regions; widen --context" % (context, with_context)
        )
    elif with_context == 0:  # pragma: no cover - defensive
        result["reason"] = "internal: the first match vanished while counting"
    return result


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Turn a quote into a byte-exact span for a LexSpec statement.")
    ap.add_argument("--corpus", required=True, help="path to the pinned corpus file")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--quote", help="the quote, pasted as-is (line breaks are fine)")
    group.add_argument("--quote-file", help="file containing the quote")
    ap.add_argument("--context", type=int, default=30, help="characters of prefix/suffix context (default 30)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    path = Path(args.corpus)
    if not path.is_file():
        print(f"span_hint: no such corpus file: {path}", file=sys.stderr)
        return 2
    raw = path.read_text(encoding="utf-8")
    quote = args.quote if args.quote is not None else Path(args.quote_file).read_text(encoding="utf-8")

    report = analyse(raw, quote, args.context)
    report["corpus"] = str(path)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"corpus            {path}")
        print(f"quote (normalised) {report['quote_normalised'][:90]!r}")
        print(f"occurs raw        {report.get('raw_has_quote')}")
        print(f"regions           {report['regions']}")
        if report["regions"]:
            print(f"regions w/ context {report.get('regions_with_context')} (context {args.context})")
            print(f"span (paste this)  {report['span']!r}")
            print(f"prefix             {report['prefix']!r}")
            print(f"suffix             {report['suffix']!r}")
        if not report["ok"]:
            print(f"reason            {report.get('reason')}")
            if report.get("hint"):
                print(f"hint              {report['hint']}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
