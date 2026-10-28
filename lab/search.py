"""search.py — search the web without the harness's search endpoint.

STATUS 2026-10-29: **non-functional in this environment.** Every public engine either returns a bot-challenge
page (DuckDuckGo 202 anomaly, Mojeek JS captcha, Bing/Startpage challenge) or requires JavaScript (Qwant). The
code is kept because the failure is the network's, not the parser's, and because the next environment may differ.
Do not read an empty result from this tool as "nothing exists" — read it as "discovery is blocked here"
(lab/probe-egress.py reports the current state).

Why this exists: the built-in `web_search` path summarises results through a separate API endpoint, and when that
endpoint's credentials fail the whole tool fails — even though plain HTTP still works. This script goes to
DuckDuckGo's HTML endpoint directly, returns titles, URLs and snippets, and does not summarise anything, so there
is no second dependency to break.

It is a **finding aid, not evidence**: a snippet is a lead. Nothing from here may enter `docs/` until the page it
points at is opened and quoted (charter C5, AGENTS.md §1).

Usage
    python lab/search.py "А09-14/2020 решение"
    python lab/search.py "ГК 395 ключевая ставка" --limit 10 --json
    python lab/search.py --open 3 "запрос"      # also fetch result 3 and print the first lines

Exit: 0 results found, 1 none, 2 usage or network error. Standard library only.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request

ENDPOINT = "https://html.duckduckgo.com/html/?q={query}"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

RESULT = re.compile(
    r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
    r'(?:<a[^>]+class="result__snippet"[^>]*>(.*?)</a>)?',
    re.S,
)
TAGS = re.compile(r"<[^>]+>")


def clean(fragment: str) -> str:
    return html.unescape(TAGS.sub("", fragment)).strip()


def unwrap(url: str) -> str:
    """DuckDuckGo wraps results in a redirect; decode the real target."""
    if url.startswith("//"):
        url = "https:" + url
    parsed = urllib.parse.urlparse(url)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        target = urllib.parse.parse_qs(parsed.query).get("uddg")
        if target:
            return target[0]
    return url


def search(query: str, limit: int) -> list[dict]:
    req = urllib.request.Request(
        ENDPOINT.format(query=urllib.parse.quote_plus(query)),
        headers={"User-Agent": UA, "Accept-Language": "ru,en;q=0.7"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")

    out: list[dict] = []
    for match in RESULT.finditer(body):
        href, title, snippet = match.group(1), match.group(2), match.group(3) or ""
        url = unwrap(href)
        if not url.startswith("http"):
            continue
        out.append({"title": clean(title), "url": url, "snippet": clean(snippet)})
        if len(out) >= limit:
            break
    return out


def fetch(url: str, chars: int = 800) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    text = raw.decode("utf-8", "replace")
    plain = html.unescape(TAGS.sub(" ", re.sub(r"(?s)<(script|style).*?</\1>", " ", text)))
    return re.sub(r"\s+", " ", plain)[:chars]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Search the web via DuckDuckGo HTML (no summarisation).")
    ap.add_argument("query", nargs="+", help="the query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--open", type=int, metavar="N", help="also fetch result N and print the beginning")
    args = ap.parse_args(argv)

    query = " ".join(args.query)
    try:
        results = search(query, args.limit)
    except Exception as exc:  # noqa: BLE001 - report, do not crash
        print(f"search: network error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"query": query, "results": results}, ensure_ascii=False, indent=2))
    else:
        print(f"query: {query}")
        for i, r in enumerate(results, 1):
            print(f"{i:>2}. {r['title']}")
            print(f"    {r['url']}")
            if r["snippet"]:
                print(f"    {r['snippet'][:160]}")
    if args.open:
        if 1 <= args.open <= len(results):
            print(f"\n--- opening {results[args.open - 1]['url']} ---")
            try:
                print(fetch(results[args.open - 1]["url"]))
            except Exception as exc:  # noqa: BLE001
                print(f"fetch failed: {exc}", file=sys.stderr)
        else:
            print("search: --open index out of range", file=sys.stderr)
            return 2
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
