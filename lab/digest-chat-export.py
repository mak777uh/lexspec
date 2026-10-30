"""Digest the Telegram export: what it is about, and the messages that touch our problem class.

7 022 messages over two years, 4 749 of them actual messages. Reading all of it is not the task; the task is to find
what is relevant to a legal checker whose weak points are provenance, verification and the boundary between a machine
check and a judgement. The digest writes a cache file so the analysis is repeatable without re-reading the export.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
from collections import Counter

SRC = pathlib.Path(os.environ.get("LEXSPEC_CHAT_EXPORT", "result.json"))
OUT = pathlib.Path(__file__).resolve().parent / "chat-export-summary.json"

# Themes we care about. Each is a set of stems, matched case-insensitively on the message text.
THEMES = {
    "verification": ["проверк", "верификац", "доказат", "proof", "validate", "проверя"],
    "formalisation": ["формализ", "спецификац", "spec", "lean", "coq", "tla", "z3", "smt"],
    "law": ["закон", "юрид", "прав", "договор", "контракт", "норматив", "регулят"],
    "standards": ["стандарт", "гост", "iso", "rfc", "wcag", "owasp", "nist"],
    "evaluation": ["бенчмарк", "benchmark", "метрик", "оценк", "eval", "измер"],
    "agents": ["агент", "agent", "harness", "tool call", "mcp"],
    "safety": ["безопасн", "safety", "security", "injection", "prompt injection", "уязвим"],
    "provenance": ["происхожден", "provenance", "аудит", "audit", "лог", "trace", "reproduc"],
}


def text_of(message: dict) -> str:
    t = message.get("text")
    if isinstance(t, str):
        return t
    if isinstance(t, list):
        return "".join(part if isinstance(part, str) else part.get("text", "") for part in t)
    return ""


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    messages = [m for m in data["messages"] if m.get("type") == "message"]

    counts: Counter = Counter()
    hits: dict[str, list[dict]] = {theme: [] for theme in THEMES}
    link_hosts: Counter = Counter()

    for message in messages:
        body = text_of(message)
        low = body.lower()
        for theme, stems in THEMES.items():
            if any(stem in low for stem in stems):
                counts[theme] += 1
                # Aggregates only. A chat export is other people's words; the repository stores counts, not quotes.
                hits[theme].append(None)
        for host in re.findall(r"https?://(?:www\.)?([^/\s:]+)", body):
            link_hosts[host.lower()] += 1

    OUT.write_text(
        json.dumps(
            {
                "source": str(SRC),
                "messages": len(messages),
                "range": [messages[0].get("date"), messages[-1].get("date")],
                "theme_counts": dict(counts.most_common()),
                "top_link_hosts": link_hosts.most_common(25),
                "hit_counts": {t: len(v) for t, v in hits.items() if v},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="",
    )

    print(f"messages: {len(messages)}  range: {messages[0].get('date','')[:10]} .. {messages[-1].get('date','')[:10]}")
    print("themes:", dict(counts.most_common()))
    print("top hosts:", link_hosts.most_common(12))
    print("digest written:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
