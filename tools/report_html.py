"""report_html.py — render a checker report as one self-contained HTML file, with no dependencies.

Why this exists, and why it is not a web application: the owner brought a stack recommendation from a chat (Python
backend, React, shadcn + TanStack, NestJS for larger, Hono for small). The recommendation is community experience —
"проверено", "легко интегрируются моделями" — and this repository's rule is that an opinion is recorded as an opinion.
What it does contain, though, is a real observation: an agent-generated UI is generated code, and generated code is a
hypothesis until something checks it.

So the first reader-facing artefact is the smallest one that can carry a verdict: **one HTML file, no JavaScript, no
CDN, no framework**, generated from the JSON report and safe to email. It answers the question a lawyer or a judge
actually has — what was checked, against which bytes, what was not claimed — without adding a dependency surface that
would itself need checking.

Usage
    python tools/report_html.py examples/01-delivery-ok.lex.json            # writes next to the report
    python tools/report_html.py examples/01-delivery-ok.lex.json --out page.html

Exit: 0 written, 1 the statement did not produce a report, 2 usage.
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "tools" / "lexcheck.py"

STYLE = """
body{font:16px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:52rem;margin:2.5rem auto;padding:0 1rem;color:#111}
h1{font-size:1.5rem;margin:0 0 .2rem}h2{font-size:1.05rem;margin:2rem 0 .5rem;text-transform:uppercase;letter-spacing:.04em;color:#444}
table{border-collapse:collapse;width:100%;margin:.5rem 0}td,th{border-bottom:1px solid #e5e5e5;padding:.4rem .5rem;text-align:left;vertical-align:top}
th{font-weight:600;color:#555;font-size:.85rem;text-transform:uppercase;letter-spacing:.03em}
.verdict{display:inline-block;padding:.15rem .6rem;border-radius:.25rem;font-weight:600;font-size:.95rem}
.ok{background:#e7f6ec;color:#146c2e}.warn{background:#fff4e5;color:#8a4b00}.bad{background:#fdeaea;color:#8f1d1d}
.mono{font-family:ui-monospace,Consolas,monospace;font-size:.86rem;word-break:break-all}
.boundary{background:#f6f6f6;border-left:3px solid #bbb;padding:.7rem .9rem;margin-top:2rem}
.muted{color:#666;font-size:.9rem}
"""


def classify(verdict: str) -> str:
    return {"CHECKED_ANCHORED": "ok", "CHECKED": "warn", "REFUSED": "bad"}.get(verdict, "warn")


def render(report: dict, statement_name: str) -> str:
    verdict = report.get("verdict", "?")
    atoms = report.get("atoms", {})
    corpus = report.get("corpus", [])
    findings = report.get("findings", [])
    status = report.get("position_status", {})
    quantities = report.get("quantities", {})
    escaped = html.escape

    rows_findings = "".join(
        f"<tr><td class='mono'>{escaped(str(f.get('code')))}</td><td>{escaped(str(f.get('atom') or '—'))}</td>"
        f"<td>{escaped(str(f.get('detail') or ''))}</td></tr>"
        for f in findings
    ) or "<tr><td colspan='3' class='muted'>none</td></tr>"

    rows_corpus = "".join(
        f"<tr><td class='mono'>{escaped(str(c.get('id')))}</td><td class='mono'>{escaped(str(c.get('text')))}</td>"
        f"<td class='mono'>{escaped(str(c.get('text_sha256')))}</td><td>{escaped(str(c.get('revision')))}</td></tr>"
        for c in corpus
    ) or "<tr><td colspan='4' class='muted'>none</td></tr>"

    rows_positions = "".join(
        f"<tr><td class='mono'>{escaped(str(k))}</td><td>{escaped(str(v))}</td></tr>" for k, v in status.items()
    ) or "<tr><td colspan='2' class='muted'>none</td></tr>"

    rows_quantities = ""
    for qid, value in quantities.items():
        segments = value.get("segments") or []
        total = value.get("total_minor")
        rows_quantities += (
            f"<tr><td class='mono'>{escaped(str(qid))}</td><td>{len(segments)}</td>"
            f"<td class='mono'>{escaped(str(total))}</td>"
            f"<td>{escaped(str(value.get('day_count')))} / {escaped(str(value.get('rounding')))}</td></tr>"
        )
    if not rows_quantities:
        rows_quantities = "<tr><td colspan='4' class='muted'>no quantities</td></tr>"

    boundary = "".join(f"<li>{escaped(str(item))}</li>" for item in report.get("not_claimed", []))

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>LexSpec report — {escaped(statement_name)}</title>
<style>{STYLE}</style></head>
<body>
<h1>LexSpec report</h1>
<p class="muted">{escaped(statement_name)} · generated from the checker's own JSON, unedited</p>
<p><span class="verdict {classify(verdict)}">{escaped(verdict)}</span>
<span class="muted">coverage {escaped(str(report.get('coverage')))} · {atoms.get('closed', '?')}/{atoms.get('total', '?')} atoms closed ·
{atoms.get('anchored', '?')} anchored</span></p>

<h2>What was checked against which bytes</h2>
<table><tr><th>corpus</th><th>file</th><th>sha256</th><th>revision</th></tr>{rows_corpus}</table>

<h2>Findings</h2>
<table><tr><th>code</th><th>atom</th><th>detail</th></tr>{rows_findings}</table>

<h2>Positions</h2>
<table><tr><th>atom</th><th>status</th></tr>{rows_positions}</table>

<h2>Quantities</h2>
<table><tr><th>id</th><th>segments</th><th>total (minor units)</th><th>day count / rounding</th></tr>{rows_quantities}</table>

<div class="boundary">
<strong>Not claimed by this report, in its own words:</strong>
<ul>{boundary}</ul>
</div>
<p class="muted">This page is a rendering. The authoritative artefact is the JSON report and the command that produced it:
<code>python tools/lexcheck.py {escaped(statement_name)} --json</code>.</p>
</body></html>
"""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Render a checker report as one self-contained HTML file.")
    ap.add_argument("statement")
    ap.add_argument("--out", help="output path (default: alongside the statement, .html)")
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args(argv)

    statement = Path(args.statement).resolve()
    if not statement.is_file():
        print(f"report_html: no such statement: {statement}", file=sys.stderr)
        return 2

    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(statement), "--json", "--root", args.root],
        capture_output=True, text=True, encoding="utf-8",
    )
    if not proc.stdout.strip():
        print("report_html: the checker produced no report", file=sys.stderr)
        return 1
    report = json.loads(proc.stdout)

    out = Path(args.out) if args.out else statement.with_suffix(".html")
    out.write_text(render(report, statement.name), encoding="utf-8", newline="")
    print(f"report_html: wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
