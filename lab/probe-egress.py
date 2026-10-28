"""probe-egress.py — what this machine can actually reach, and what it cannot.

Written after a session in which the built-in web search failed with an authentication error, every public
search engine either blocked the IP or required JavaScript, and two Russian court domains did not resolve — while
several document hosts answered normally. That mix is not a bug in the tools; it is the shape of the network, and
it decides which verification is possible today.

The distinction that matters: **retrieval works, discovery does not.** With a known URL we can open and quote a
primary source. Without one we cannot find it, so questions that need discovery must be answered by a human or
deferred.

Usage
    python lab/probe-egress.py            # probe the default set
    python lab/probe-egress.py --json     # machine-readable
    python lab/probe-egress.py --only search

Exit: 0 if at least one host answers, 2 if none do (i.e. the network is down, not just blocked).
"""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# (group, label, url). Groups: search = discovery; docs = retrieval of primary sources; legal = court/registry.
TARGETS: list[tuple[str, str, str]] = [
    ("search", "duckduckgo-html", "https://html.duckduckgo.com/html/?q=test"),
    ("search", "mojeek", "https://www.mojeek.com/search?q=test"),
    ("search", "qwant", "https://www.qwant.com/?q=test"),
    ("search", "bing", "https://www.bing.com/search?q=test"),
    ("search", "startpage", "https://www.startpage.com/sp/search?query=test"),
    ("docs", "w3.org", "https://www.w3.org/TR/annotation-model/"),
    ("docs", "ietf", "https://datatracker.ietf.org/doc/draft-sato-soos-cap-rrs/"),
    ("docs", "arxiv", "https://arxiv.org/abs/2103.03198"),
    ("docs", "eur-lex", "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"),
    ("legal", "consultant.ru", "https://www.consultant.ru/"),
    ("legal", "publication.pravo.gov.ru", "http://publication.pravo.gov.ru/"),
    ("legal", "pravo.gov.ru", "http://pravo.gov.ru/"),
    ("legal", "vsrf.ru", "https://www.vsrf.ru/"),
    ("legal", "sudact.ru", "https://sudact.ru/"),
    ("legal", "kad.arbitr.ru", "https://kad.arbitr.ru/"),
    ("legal", "garant.ru", "https://www.garant.ru/"),
]


def probe(url: str, timeout: float = 12.0) -> tuple[str, str]:
    """Return (status, detail). status is one of ok / http-NNN / dns / tls / timeout / error."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ru,en;q=0.7"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(2048)
            return "ok", f"HTTP {resp.status}, {len(body)}+ bytes"
    except urllib.error.HTTPError as exc:
        return f"http-{exc.code}", exc.reason or ""
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, socket.gaierror):
            return "dns", str(reason)
        if isinstance(reason, ssl.SSLError):
            return "tls", str(reason)
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return "timeout", str(reason)
        return "error", str(reason)
    except (TimeoutError, socket.timeout):
        return "timeout", "no answer"
    except Exception as exc:  # noqa: BLE001 - report, never crash
        return "error", str(exc)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Report which hosts this machine can reach.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--only", choices=["search", "docs", "legal"], help="probe one group")
    args = ap.parse_args(argv)

    rows = []
    for group, label, url in TARGETS:
        if args.only and group != args.only:
            continue
        status, detail = probe(url)
        rows.append({"group": group, "host": label, "url": url, "status": status, "detail": detail})

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        width = max(len(r["host"]) for r in rows)
        for r in rows:
            print(f'{r["group"]:<7} {r["host"]:<{width}}  {r["status"]:<8}  {r["detail"][:70]}')

    reachable = sum(1 for r in rows if r["status"] == "ok")
    print(f"\nprobe-egress: {reachable}/{len(rows)} reachable")
    by_group: dict[str, list[int]] = {}
    for r in rows:
        ok, total = by_group.get(r["group"], [0, 0])
        by_group[r["group"]] = [ok + (r["status"] == "ok"), total + 1]
    for group, (ok, total) in sorted(by_group.items()):
        print(f"  {group:<7} {ok}/{total}")
    return 0 if reachable else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
