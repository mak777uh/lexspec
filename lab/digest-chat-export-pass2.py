"""Second pass: word-boundary legal patterns, because the first pass matched 'прав' inside 'правильно'.

This is the same defect the repository keeps finding in its own guards, one level down: a count over a badly chosen
term set is a number that looks like a measurement. 'прав' matched 150 messages; almost all of them were 'правильно',
'правда', 'право' in the sense of 'right/correct'. Boundary-anchored patterns fix it, and the difference between the
two counts is the measurement error of the first pass.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
from collections import Counter

SRC = pathlib.Path(os.environ.get("LEXSPEC_CHAT_EXPORT", "result.json"))
OUT = pathlib.Path(__file__).resolve().parent / "chat-export-summary.json"

LEGAL = re.compile(
    r"\b(закон[а-я]*|юридическ[а-я]+|правов[а-я]+|правоотношени[а-я]+|договор[а-я]*|контракт[а-я]+|"
    r"нормативн[а-я]+|регулятор[а-я]*|регламент[а-я]*|судебн[а-я]+|иск[а-я]{1,3}|штраф[а-я]*|"
    r"лицензи[а-я]+|комплаенс|compliance|legal|law|statute|regulation)\b",
    re.I,
)
ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})")


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

    legal: list[dict] = []
    papers: Counter = Counter()
    for message in messages:
        body = text_of(message)
        if LEGAL.search(body):
            legal.append({"date": (message.get("date") or "")[:10]})
        for pid in ARXIV.findall(body):
            papers[pid] += 1

    digest = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else {}
    digest["pass2"] = {
        "legal_precise": len(legal),
        "legal_first_pass": digest.get("theme_counts", {}).get("law", 0),
        "legal_message_dates": [item["date"] for item in legal[:200]],
        "top_arxiv_ids": papers.most_common(20),
    }
    OUT.write_text(json.dumps(digest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")

    print(f"legal messages, boundary-anchored: {len(legal)}")
    print(f"legal messages, first pass (stem 'прав'): {digest.get('theme_counts', {}).get('law', 0)}")
    print("\ntop arXiv ids by mention:")
    for pid, n in papers.most_common(10):
        print(f"  {n:>3}x  {pid}")
    print("\nsample legal messages:")
    for item in legal[:8]:
        print(f"  {item['date']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
