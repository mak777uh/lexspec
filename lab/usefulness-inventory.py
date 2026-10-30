"""Build an inventory of Proof-of-Usefulness reports: locate, fetch, extract score and the claimed data point.

The public site has no list endpoint and HackerNoon's tag page is rendered client-side, so the inventory is assembled
the only way left: search per project name, keep the first HackerNoon URL that looks like a report, fetch it once and
cache the extraction in lab/usefulness-inventory.json.

Run: python lab/usefulness-inventory.py
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "lab" / "usefulness-inventory.json"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0"}

PROJECTS = {
    "Visby": "tracking brand visibility across AI search",
    "FoxPlug": "white-label launch kit generator",
    "Siiqo": "unknown category",
    "Cofoundr": "unknown category",
    "HOL Guard": "unknown category (Algolia prize)",
    "Visual MCP Gateway": "unknown category",
    "HostLens AI": "unknown category (Neo4j prize)",
    "FlowMind": "AI project manager that auto-assigns tasks",
    "PMB": "local memory for AI coding agents",
    "tenv": "unknown category",
    "Claude Code Organizer": "dashboard for Claude Code memories, configs and MCP servers",
    "Snatch Guard": "unknown category",
    "Autonomous Company Deep Research Agent": "unknown category",
    "Ella's AI Agent": "unknown category",
    "TransactionLink": "unknown category",
    "hello.cv": "unknown category",
    "Developer Farm": "unknown category",
    "theCloaq": "unknown category",
    "Tinky Town": "unknown category",
    "AIOProductOS": "unknown category",
}

SCORE_RE = re.compile(r"scored (?:a |an )?([0-9]{1,4}(?:\.[0-9]{1,2})?)", re.I)
# The slug itself carries the score: "...-earns-a-8794-proof-of-usefulness-score..." is 87.94, and
# "...-earns-a-42-..." is 42. Four digits mean hundredths; fewer mean the integer.
SLUG_SCORE = re.compile(r"earns-a-(\d{1,4})(?:-|$)")


def slug_score(url: str) -> float | None:
    m = SLUG_SCORE.search(url.rsplit("/", 1)[-1])
    if not m:
        return None
    digits = m.group(1)
    return round(int(digits) / 100, 2) if len(digits) == 4 else float(digits)



def search(query: str) -> list[dict]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "lab" / "search.py"), query, "--limit", "6", "--json"],
        capture_output=True, text=True, encoding="utf-8",
    )
    try:
        return json.loads(proc.stdout).get("results", [])
    except json.JSONDecodeError:
        return []


def usable(url: str) -> bool:
    """Reject scraper artefacts: a mailto-in-host or a non-http scheme is not a report."""
    return (
        url.startswith("https://hackernoon.com/")
        and "@" not in url.split("/", 3)[2]
        and " " not in url
    )


def report_url(name: str, hint: str) -> str | None:
    queries = [
        f'hackernoon "{name}" "proof of usefulness score"',
        f'{name} hackernoon proof of usefulness report',
    ]
    for query in queries:
        for result in search(query):
            url = result.get("url", "")
            if not usable(url):
                continue
            tail = url.rsplit("/", 1)[-1]
            # A report names the project and the score ("...-earns-a-47-..."). The rubric page and the
            # partner announcements also contain "usefulness" and are not reports.
            if "earns" in tail:
                return url
    return None


def plain(url: str) -> str:
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=40).read().decode("utf-8", "replace")
    body = re.sub(r"(?s)<(script|style|nav|footer).*?</\1>", " ", raw)
    body = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return re.sub(r"\s+", " ", body)


def extract(text: str, url: str = "") -> dict:
    score = SCORE_RE.search(text)
    evidence = ""
    marker = "one data point that proves"
    i = text.lower().find(marker)
    if i != -1:
        evidence = text[i : i + 700]
    numbers = re.findall(r"\b\d[\d,\.]{2,}\s*(?:users|downloads|stars|%|weekly|installs)", text, re.I)
    return {
        "score": (slug_score(url) if url else None) or (score.group(1) if score else None),
        "data_point": evidence[:500],
        "numbers": numbers[:6],
    }


def main() -> int:
    cache: dict = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.is_file() else {}
    for name, hint in PROJECTS.items():
        if name in cache and cache[name].get("url"):
            print(f"cached  {name}")
            continue
        url = report_url(name, hint)
        if not url:
            cache[name] = {"hint": hint, "url": None, "note": "no report found by search"}
            print(f"MISS    {name}")
            continue
        try:
            text = plain(url)
            record = {"hint": hint, "url": url, **extract(text, url)}
        except Exception as exc:  # noqa: BLE001 - a bad result must not end the inventory
            cache[name] = {"hint": hint, "url": url, "note": f"{type(exc).__name__}: {str(exc)[:80]}"}
            print(f"FETCH   {name}: {type(exc).__name__}")
            time.sleep(1)
            continue
        cache[name] = record
        print(f"found   {name:<42} score={record['score']}  {url.rsplit('/', 1)[-1][:60]}")
        time.sleep(0.5)

    # written even on an interrupted run, so a twenty-project inventory is never restarted from zero
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    found = sum(1 for v in cache.values() if v.get("url"))
    scored = sum(1 for v in cache.values() if v.get("score"))
    print(f"\ninventory: {len(cache)} projects, {found} with a report, {scored} with a score")
    return 0


if __name__ == "__main__":
    sys.exit(main())
