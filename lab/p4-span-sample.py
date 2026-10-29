"""P4 — how often is a random span genuinely ambiguous in our corpora?

Principle P4 says anchoring failures are a formatting phenomenon, not an ambiguity phenomenon. The formatting half was
settled by span_hint (6 of 6 recovered). This script settles the other half: take random spans from the real
corpora, and count how many select more than one region

  * alone,
  * with 32 characters of context (the window Hypothesis uses),

and how many cross a line break in the raw file (the formatting cause, measured separately).

Large N matters: a single example proves nothing, and the whole point of the register is numbers, not impressions.

Run: python lab/p4-span-sample.py [--n 200] [--json]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = 32
LEN_MIN, LEN_MAX = 40, 120


def load_hint():
    spec = importlib.util.spec_from_file_location("span_hint", ROOT / "tools" / "span_hint.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def regions(haystack: str, needle: str) -> int:
    count, start = 0, 0
    while True:
        hit = haystack.find(needle, start)
        if hit == -1:
            return count
        count += 1
        start = hit + 1


def sample(path: Path, n: int, rng: random.Random, hint) -> dict:
    raw = path.read_text(encoding="utf-8")
    norm, cmap = hint.normalize_with_map(raw)
    if len(norm) < 400:
        return {"corpus": str(path.name), "skipped": "too short"}

    alone_unique = ctx_unique = ambiguous = crossable = 0
    multiplicities: list[int] = []
    lengths: list[int] = []

    for _ in range(n):
        length = rng.randint(LEN_MIN, LEN_MAX)
        if length >= len(norm):
            continue
        start = rng.randrange(0, len(norm) - length)
        span = norm[start : start + length]
        if span.strip() != span or "  " in span:
            continue  # not a clean quote

        total = regions(norm, span)
        multiplicities.append(total)
        lengths.append(len(span))
        first, last = cmap[start], cmap[start + length - 1]
        if '\n' in raw[first:last + 1]:
            crossable += 1
        if total == 1:
            alone_unique += 1
            ctx_unique += 1
            continue
        if total == 0:  # defensive: cannot happen for a substring of the same text
            continue
        # does a 32-char window separate it?
        prefix = norm[max(0, start - CONTEXT) : start]
        suffix = norm[start + length : start + length + CONTEXT]
        survivors = 0
        s = 0
        while True:
            hit = norm.find(span, s)
            if hit == -1:
                break
            if norm[max(0, hit - CONTEXT) : hit] == prefix and norm[hit + length : hit + length + CONTEXT] == suffix:
                survivors += 1
            s = hit + 1
        if survivors == 1:
            ctx_unique += 1
        else:
            ambiguous += 1
        # formatting check: does the raw slice contain a line break?
        first, last = cmap[start], cmap[start + length - 1]
        if "\n" in raw[first : last + 1]:
            crossable += 1

    tried = alone_unique + (len(multiplicities) - alone_unique)
    return {
        "corpus": str(path.name),
        "sampled": len(multiplicities),
        "alone_unique": alone_unique,
        "ctx_unique": ctx_unique,
        "still_ambiguous": ambiguous,
        "crossing_a_line_break": crossable,
        "mean_multiplicity": round(statistics.mean(multiplicities), 3) if multiplicities else 0.0,
        "max_multiplicity": max(multiplicities) if multiplicities else 0,
        "mean_length": round(statistics.mean(lengths), 1) if lengths else 0.0,
        "alone_unique_pct": round(100 * alone_unique / len(multiplicities), 1) if multiplicities else 0.0,
        "ctx_unique_pct": round(100 * ctx_unique / len(multiplicities), 1) if multiplicities else 0.0,
        "still_ambiguous_pct": round(100 * ambiguous / len(multiplicities), 1) if multiplicities else 0.0,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Measure genuine span ambiguity in the corpora.")
    ap.add_argument("--n", type=int, default=200, help="random spans per corpus")
    ap.add_argument("--min-len", type=int, default=40)
    ap.add_argument("--max-len", type=int, default=120)
    ap.add_argument("--seed", type=int, default=20261029)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    global LEN_MIN, LEN_MAX
    LEN_MIN, LEN_MAX = args.min_len, args.max_len
    hint = load_hint()
    rng = random.Random(args.seed)
    rows = []
    for corpus in sorted((ROOT / "corpus").glob("*.txt")):
        rows.append(sample(corpus, args.n, rng, hint))

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    print(f"{'corpus':<34}{'n':>5}{'uniq':>7}{'ctx32':>8}{'ambig':>7}{'x-line':>8}{'meanMult':>9}")
    for r in rows:
        if "skipped" in r:
            print(f"{r['corpus']:<34}  skipped: {r['skipped']}")
            continue
        print(f"{r['corpus']:<34}{r['sampled']:>5}{r['alone_unique_pct']:>6.1f}%{r['ctx_unique_pct']:>7.1f}%"
              f"{r['still_ambiguous_pct']:>6.1f}%{r['crossing_a_line_break']:>8}{r['mean_multiplicity']:>9.2f}")

    total = sum(r["sampled"] for r in rows if "skipped" not in r)
    amb = sum(r["still_ambiguous"] for r in rows if "skipped" not in r)
    alone = sum(r["alone_unique"] for r in rows if "skipped" not in r)
    print(f"\ntotal spans: {total}")
    print(f"  unique alone: {alone} ({100*alone/total:.1f}%)")
    print(f"  unique with {CONTEXT}-char context: {total - amb} ({100*(total-amb)/total:.1f}%)")
    print(f"  still ambiguous: {amb} ({100*amb/total:.1f}%)")
    print(f"\nP4 reading: if 'still ambiguous' is near zero, genuine ambiguity is rare and the exact-span rule is")
    print("over-strict for the wrong reason; if it is material, the context window is doing real work.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
