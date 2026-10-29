"""check-spec.py — mechanical consistency guard for the specification.

The owner's condition for shipping software: the specification must be *clear and non-contradictory* first.
Clarity cannot be automated; contradiction largely can, because the documents and the executable contract
overlap. This tool finds every overlap where they disagree and says which side is which.

Checks, none of them stylistic:

  A. codes      every code the checker knows == the schema's refusalCode enum == docs/11; each code's group is
                named in the spec
  B. fields     every top-level field and every $defs object field is documented in spec §2, and the spec
                documents no field that the schema lacks
  C. relations  the eight Hohfeld names agree across schema, checker and spec §4.1
  D. squares    CORRELATIVE / OPPOSITE in the checker agree with the table in spec §4.1
  E. verdicts   the three verdict strings agree across checker, spec §9 and README
  F. examples   LF only, no BOM, no floats, corpus digests match the bytes
  G. glossary   every term defined in spec §1 is used in the body
  H. refs       every $ref in the schema resolves to an existing definition

Exit: 0 clean, 1 findings, 2 usage. Standard library only.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "10-SPEC-v0.1.md"
CODES = ROOT / "docs" / "11-REFUSAL-CODES.md"
SCHEMA = ROOT / "schemas" / "statement-0.1.json"
CHECKER = ROOT / "tools" / "lexcheck.py"
README = ROOT / "README.md"
EXAMPLES = ROOT / "examples"

RELATIONS = {
    "right", "duty", "privilege", "no-right",
    "power", "liability", "immunity", "disability",
}

findings: list[tuple[str, str]] = []


def add(check: str, detail: str) -> None:
    findings.append((check, detail))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ------------------------------------------------------------------ A. codes

def checker_codes() -> set[str]:
    """Codes the checker knows, read from its own tables — never from comments."""
    src = read(CHECKER)
    order = re.search(r"CODE_ORDER\s*=\s*\((.*?)\)", src, re.S)
    if not order:
        add("A", "CODE_ORDER tuple not found in the checker")
        return set()
    codes = set(re.findall(r'"([A-Z0-9_]+)"', order.group(1)))
    esc = re.search(r"ESCAPE_CODES\s*=\s*frozenset\(\{(.*?)\}\)", src, re.S)
    if esc:
        codes |= set(re.findall(r'"([A-Z0-9_]+)"', esc.group(1)))
    return codes


def catalogue_codes() -> set[str]:
    tokens = set(re.findall(r"`([A-Z0-9][A-Z0-9_]*)`", read(CODES)))
    return {
        c for c in tokens
        if re.fullmatch(r"(?:C0|S[1-7])_[A-Z0-9_]+", c) or c in {"OPEN_TERM", "THIN_COVERAGE"}
    }


def schema_codes() -> set[str]:
    defs = json.loads(read(SCHEMA)).get("$defs", {})
    return set(defs.get("refusalCode", {}).get("enum", []))


def check_codes() -> None:
    emitted, documented, schema = checker_codes(), catalogue_codes(), schema_codes()
    for c in sorted(emitted - documented):
        add("A", f"the checker knows {c} but docs/11 does not catalogue it")
    for c in sorted(documented - emitted):
        add("A", f"docs/11 catalogues {c} but the checker never emits it")
    for c in sorted(emitted - schema):
        add("A", f"the checker knows {c} but the schema's refusalCode enum does not allow it")
    for c in sorted(schema - emitted):
        add("A", f"the schema allows {c} but the checker has no such code")
    spec = read(SPEC)
    for c in sorted(emitted):
        group = c.split("_")[0]
        if group not in spec:
            add("A", f"code group {group} is not named anywhere in the spec")


# ------------------------------------------------------------------ B. fields

def spec_section(name: str) -> str:
    m = re.search(r"## §2 Document model(.*?)(?=\n## )", read(SPEC), re.S)
    if not m:
        add("B", "spec §2 not found")
        return ""
    body = m.group(1)
    if name == "top":
        m3 = re.search(r"```[a-z]*\n(.*?)```", body, re.S)
        return m3.group(1) if m3 else ""
    # a block is the first fenced listing after its label. The label may carry a parenthetical before the
    # colon (e.g. "`SeriesRef` (planned for v0.1.1):"), so text between the name and the colon is tolerated;
    # prose after the closing fence must never be read as fields.
    m2 = re.search(rf"`{name}`[^\n]*:\s*\n+```[a-z]*\n(.*?)```", body, re.S)
    return m2.group(1) if m2 else ""


def fields_in(text: str) -> set[str]:
    out = set()
    for line in text.splitlines():
        m = re.match(r"\s*([a-z][a-z0-9_]{1,})\b", line)
        if m:
            out.add(m.group(1))
    return out


def check_fields() -> None:
    schema = json.loads(read(SCHEMA))
    documented_top = fields_in(spec_section("top"))
    for f in sorted(set(schema.get("properties", {})) - documented_top):
        add("B", f"schema top-level field not documented in spec §2: {f}")
    for f in sorted(documented_top - set(schema.get("properties", {}))):
        add("B", f"spec §2 documents a top-level field the schema lacks: {f}")

    blocks = {"CorpusRef": "corpusRef", "Term": "term", "Atom": "atom", "Escape": "escape",
              "SeriesRef": "seriesRef", "Quantity": "quantity"}
    defs = schema.get("$defs", {})
    for spec_name, def_name in blocks.items():
        doc = fields_in(spec_section(spec_name))
        if not doc:
            add("B", f"spec §2 block `{spec_name}` not found or empty")
            continue
        real = set(defs.get(def_name, {}).get("properties", {}))
        for f in sorted(real - doc):
            add("B", f"{def_name}: field {f!r} is in the schema, undocumented in spec §2")
        for f in sorted(doc - real):
            add("B", f"{def_name}: spec §2 documents {f!r}, absent from the schema")


# ------------------------------------------------------------------ C/D. relations and squares

def spec_rows() -> list[tuple[str, str, str]]:
    body = re.search(r"### §4\.1(.*?)\n###", read(SPEC), re.S)
    if not body:
        add("D", "spec §4.1 not found")
        return []
    return re.findall(r"^\|\s*`([a-z-]+)`\s*\|\s*`([a-z-]+)`\s*\|\s*`([a-z-]+)`\s*\|", body.group(1), re.M)


def check_relations() -> None:
    schema = json.loads(read(SCHEMA))
    enum = set(schema.get("$defs", {}).get("relation", {}).get("enum", []))
    src = read(CHECKER)
    cor_block = re.search(r"CORRELATIVE\s*=\s*\{(.*?)\n\}", src, re.S)
    opp_block = re.search(r"OPPOSITE\s*=\s*\{(.*?)\n\}", src, re.S)
    cor = dict(re.findall(r'"([a-z-]+)"\s*:\s*"([a-z-]+)"', cor_block.group(1))) if cor_block else {}
    opp = dict(re.findall(r'"([a-z-]+)"\s*:\s*"([a-z-]+)"', opp_block.group(1))) if opp_block else {}

    if enum != RELATIONS:
        add("C", f"schema relation enum is not the eight positions: {sorted(enum)}")
    if set(cor) != RELATIONS:
        add("C", f"checker CORRELATIVE does not cover the eight positions: {sorted(set(cor))}")
    if set(opp) != RELATIONS:
        add("C", f"checker OPPOSITE does not cover the eight positions: {sorted(set(opp))}")

    rows = spec_rows()
    if len(rows) != 8:
        add("D", f"spec §4.1 table has {len(rows)} rows, expected 8")
    for pos, correlative, opposite in rows:
        if cor.get(pos) != correlative:
            add("D", f"correlative mismatch for {pos}: spec {correlative!r}, checker {cor.get(pos)!r}")
        if opp.get(pos) != opposite:
            add("D", f"opposite mismatch for {pos}: spec {opposite!r}, checker {opp.get(pos)!r}")
    if {r[0] for r in rows} != RELATIONS:
        add("D", f"spec §4.1 does not cover the eight positions: {sorted({r[0] for r in rows})}")


# ------------------------------------------------------------------ E. verdicts

def check_verdicts() -> None:
    spec = set(re.findall(r"`(REFUSED|CHECKED|CHECKED_ANCHORED)`", read(SPEC)))
    checker = set(re.findall(r'"(REFUSED|CHECKED|CHECKED_ANCHORED)"', read(CHECKER)))
    readme = set(re.findall(r"`(REFUSED|CHECKED|CHECKED_ANCHORED)`", read(README)))
    if len(spec) != 3:
        add("E", f"spec should name exactly three verdicts, found {len(spec)}: {sorted(spec)}")
    for name, got in (("checker", checker), ("README", readme)):
        if got - spec:
            add("E", f"{name} names verdicts the spec does not: {sorted(got - spec)}")


# ------------------------------------------------------------------ F. examples

def check_examples() -> None:
    for path in sorted(EXAMPLES.glob("*.lex.json")):
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            add("F", f"{path.name}: UTF-8 BOM present (spec §3.1 forbids it)")
        if b"\r\n" in raw:
            add("F", f"{path.name}: CRLF line endings (spec §3.1 requires LF)")
        try:
            doc = json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            add("F", f"{path.name}: not parseable as JSON: {exc}")
            continue
        for entry in doc.get("corpus", []):
            target = ROOT / str(entry.get("text", ""))
            if not target.is_file():
                add("F", f"{path.name}: corpus file missing: {entry.get('text')}")
                continue
            if hashlib.sha256(target.read_bytes()).hexdigest() != entry.get("text_sha256"):
                add("F", f"{path.name}: corpus digest mismatch for {entry.get('text')}")
        if re.search(r'"[a-z_]+"\s*:\s*-?\d+\.\d', raw.decode("utf-8", "replace")):
            add("F", f"{path.name}: a floating-point number appears where the spec forbids one")


# ------------------------------------------------------------------ G. glossary

def check_glossary() -> None:
    spec = read(SPEC)
    m = re.search(r"## §1 Vocabulary(.*?)(?=\n## )", spec, re.S)
    if not m:
        add("G", "spec §1 Vocabulary not found")
        return
    terms = re.findall(r"^\|\s*\*\*([^*|]+)\*\*\s*\|", m.group(1), re.M)
    if not terms:
        add("G", "no glossary rows found in spec §1")
    body = spec[m.end():]
    for t in terms:
        if t.strip().lower() not in body.lower():
            add("G", f"glossary term defined but never used in the body: {t.strip()}")


# ------------------------------------------------------------------ H. refs

def check_refs() -> None:
    schema = json.loads(read(SCHEMA))
    defs = set(schema.get("$defs", {}))
    for m in re.finditer(r'"\$ref"\s*:\s*"#/\$defs/([A-Za-z0-9_]+)"', read(SCHEMA)):
        if m.group(1) not in defs:
            add("H", f"$ref to a definition that does not exist: $defs/{m.group(1)}")


def main(argv: list[str]) -> int:
    check_codes()
    check_fields()
    check_relations()
    check_verdicts()
    check_examples()
    check_glossary()
    check_refs()

    if findings:
        groups = sorted({c for c, _ in findings})
        for check, detail in findings:
            print(f"{check}: {detail}")
        print(f"check-spec: {len(findings)} finding(s) in groups {groups}")
        return 1
    print("check-spec: clean - codes, fields, relations, squares, verdicts, examples, glossary and refs agree")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
