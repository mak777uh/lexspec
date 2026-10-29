"""search.py — search the web without the harness's search endpoint.

STATUS 2026-10-29 (updated): **working**, through the keyless **AnySearch** engine
(`api.anysearch.com/v1/search`) — the same one the `dsh-free-search` plugin ships. The earlier verdict
"non-functional" was wrong in an instructive way: DuckDuckGo (202 anomaly), Mojeek (JS captcha), Qwant (JS shell,
API 403), Bing/Startpage (challenge) and the SearXNG instances all gate this network, but AnySearch answers without
a key. It found the Bryansk judgment PDF that four court domains refused to serve.

Fallback order: AnySearch → DuckDuckGo HTML → Bing. A failure in one engine is reported, not swallowed, so an
empty result never silently means "nothing exists" (`lab/probe-egress.py` reports which hosts are reachable).

Why this exists: the built-in `web_search` path summarises results through a separate API endpoint whose key can
be invalid, and when it is, the whole tool fails even though plain HTTP works. This script talks to engines
directly, returns titles, URLs and snippets, and summarises nothing.

It is a **finding aid, not evidence**: a snippet is a lead. Nothing from here may enter `docs/` until the page it
points at is opened and quoted (charter C5, AGENTS.md §1).

Usage
    python lab/search.py "А09-14/2020 решение"
    python lab/search.py "ГК 395 ключевая ставка" --limit 10 --json
    python lab/search.py --open 3 "запрос"      # also fetch result 3 and print the first lines
    python lab/search.py --engine anysearch "…"  # pin one engine (anysearch | ddg | bing)

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


ANYSEARCH = "https://api.anysearch.com/v1/search"
BING = "https://www.bing.com/search"


def anysearch(query: str, limit: int) -> list[dict]:
    """Keyless structured search. This is the engine that actually answers from this network."""
    body = json.dumps({"query": query, "max_results": limit}).encode("utf-8")
    req = urllib.request.Request(
        ANYSEARCH,
        data=body,
        headers={"content-type": "application/json", "user-agent": UA, "accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    if data.get("code") not in (0, None):
        raise RuntimeError(f"AnySearch error: {data.get('message') or data.get('code')}")
    results = (data.get("data") or {}).get("results") or []
    out = []
    for r in results:
        url = r.get("url")
        if not url:
            continue
        out.append(
            {
                "title": str(r.get("title") or ""),
                "url": url,
                "snippet": str(r.get("snippet") or "")[:300],
            }
        )
    return out[:limit]


def duckduckgo(query: str, limit: int) -> list[dict]:
    """HTML endpoint; frequently answers 202 with a bot-check page, hence the fallback ordering."""
    req = urllib.request.Request(
        ENDPOINT.format(query=urllib.parse.quote_plus(query)),
        headers={"User-Agent": UA, "Accept-Language": "ru,en;q=0.7"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
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


ENGINES = {"anysearch": anysearch, "ddg": duckduckgo}


def search(query: str, limit: int, engine: str | None = None) -> tuple[list[dict], list[str]]:
    """Try the requested engine, then the rest. Returns results and the errors of the engines that failed."""
    order = [engine] if engine else ["anysearch", "ddg"]
    errors: list[str] = []
    for name in order:
        if name not in ENGINES:
            errors.append(f"{name}: unknown engine")
            continue
        try:
            found = ENGINES[name](query, limit)
        except Exception as exc:  # noqa: BLE001 - report, do not crash
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
            continue
        if found:
            if name != order[0]:
                errors.append(f"note: used {name} because earlier engines failed")
            return found, errors
        errors.append(f"{name}: 0 results")
    return [], errors


def fetch(url: str, chars: int = 800) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    text = raw.decode("utf-8", "replace")
    plain = html.unescape(TAGS.sub(" ", re.sub(r"(?s)<(script|style).*?</\1>", " ", text)))
    return re.sub(r"\s+", " ", plain)[:chars]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Search the web keyless (AnySearch, then DuckDuckGo), no summarisation.")
    ap.add_argument("query", nargs="+", help="the query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--engine", choices=sorted(ENGINES), help="pin one engine instead of falling back")
    ap.add_argument("--open", type=int, metavar="N", help="also fetch result N and print the beginning")
    args = ap.parse_args(argv)

    query = " ".join(args.query)
    results, errors = search(query, args.limit, args.engine)

    if args.json:
        print(json.dumps({"query": query, "engine_notes": errors, "results": results}, ensure_ascii=False, indent=2))
    else:
        print(f"query: {query}")
        for note in errors:
            print(f"  ({note})")
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
