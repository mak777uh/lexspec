#!/usr/bin/env python3
"""lexcheck — reference checker for LexSpec v0.1.

Why this file exists. A LexSpec statement is a legal claim written so that a
machine can find defects in it. The checker does not know law: it knows whether
the document is well formed (S1), whether its citations point at exactly one
place in a text pinned by sha256 (S2), whether its Hohfeld layer is coherent
(S3, S6), whether its vocabulary is closed (S4) and whether its dates are sane
(S5). Legal validity, completeness of the encoded law and the correctness of
the corpus outside the pinned revision are *not* checked — every report says so
in `not_claimed`, because a verdict quoted without that list is a different
claim than the one this tool made.

Two design rules come from docs/10-SPEC-v0.1.md and are worth naming:

  * refuse, never warn, on S2: a citation that can re-point itself is not
    evidence, so ambiguity is a refusal and not a note;
  * a finding is a statement about the *input*, never about the checker's mood,
    so every finding carries a code from the closed vocabulary plus the atom it
    is about (or null for statement-level findings).

Known, deliberate gap (v0.1): docs/10-SPEC-v0.1.md §4.3 says a correlative pair,
*when written out*, is checked for agreement and a mismatch is S6_CONFLICT.
S6 here compares atoms that share the exact `(bearer, verb, object, counterparty)`
tuple, which is the combinatorial contradiction the square justifies. It does not
check cross-tuple correlative agreement (A's `right` against B vs B's `duty`
toward A), because the spec does not define the orientation of a correlative
instance and guessing would produce refusals the author cannot act on. This gap
is recorded in tools/SELFTEST.md rather than papered over.

Exit codes: 0 passing verdict, 1 REFUSED, 2 usage or parse error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

SCHEMA_VERSION = "0.1"
DEFAULT_THRESHOLD = 0.8

# --- the Hohfeld square (spec §4.1) -----------------------------------------
# Order is the spec's order, not alphabetical: it is what the docs table shows.
RELATIONS = (
    "right",
    "duty",
    "privilege",
    "no-right",
    "power",
    "liability",
    "immunity",
    "disability",
)

CORRELATIVE = {
    "right": "duty",
    "duty": "right",
    "privilege": "no-right",
    "no-right": "privilege",
    "power": "liability",
    "liability": "power",
    "immunity": "disability",
    "disability": "immunity",
}

OPPOSITE = {
    "right": "privilege",
    "privilege": "right",
    "duty": "no-right",
    "no-right": "duty",
    "power": "immunity",
    "immunity": "power",
    "liability": "disability",
    "disability": "liability",
}

# §4.3: these three may be asserted "against the world" and may omit
# counterparty. `liability` is the correlative of `power` but the spec does not
# list it as absolute, so it still needs a counterparty — that asymmetry is the
# document's, and S3 follows the document.
ABSOLUTE_CAPABLE = frozenset({"power", "immunity", "disability"})

POLICIES = ("report", "lex_specialis", "lex_posterior")
KINDS = ("norm", "clause", "scenario")
TERM_STATUS = ("closed", "open")

# Top-level keys a statement must carry (spec §2). Kept next to the validator and
# compared with schemas/statement-0.1.json by tests/run_tests.py, so the prose
# schema and the executable one cannot drift apart silently.
REQUIRED_TOP = (
    "lexspec",
    "id",
    "kind",
    "jurisdiction",
    "corpus",
    "terms",
    "atoms",
    "conflicts_policy",
    "escapes",
)

# --- code vocabulary (docs/11-REFUSAL-CODES.md), closed ----------------------
# Group ids are the spec's check numbers, not code names: the report's `checks`
# map says which layer failed, and inventing a code-shaped name for a group
# (like "S7_COVERAGE") would put a string in every report that is not a code.
CHECK_ORDER = ("C0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9")

# Codes in the order docs/11-REFUSAL-CODES.md lists them. This order is also the
# order findings are reported in, and the order the code-coverage table in
# tools/SELFTEST.md uses: a catalogue a reader can read top to bottom.
CODE_ORDER = (
    "C0_CANON",
    "S1_SCHEMA",
    "S2_NO_CORPUS",
    "S2_HASH_MISMATCH",
    "S2_CORPUS_NOT_FOUND",
    "S2_CORPUS_UNREADABLE",
    "S2_REVISION_MISMATCH",
    "S2_REVISION_UNCHECKED",
    "S2_CONTEXT_MISMATCH",
    "S2_CONTEXT_MISSING",
    "S8_SERIES_NOT_PINNED",
    "S8_UNANCHORED_QUANTITY",
    "S8_SEGMENT_GAP",
    "S8_UNDECLARED_ARITHMETIC",
    "S9_DEFEAT_UNDEFINED",
    "S9_DEFEAT_CYCLE",
    "S9_APPLICABILITY_UNSTATED",
    "S2_SPAN_NOT_FOUND",
    "S2_SPAN_AMBIGUOUS",
    "S3_UNKNOWN_RELATION",
    "S3_MISSING_COUNTERPARTY",
    "S3_OPPOSITE_CONFLICT",
    "S4_UNDEFINED_REF",
    "OPEN_TERM",
    "S4_UNDECLARED_ESCAPE",
    "S4_STALE_ESCAPE",
    "S5_EMPTY_INTERVAL",
    "S6_CONFLICT",
    "S6_UNRESOLVED_CONFLICT",
    "THIN_COVERAGE",
)

ALL_CODES = frozenset(CODE_ORDER)

# Codes that lower the verdict to CHECKED but do not refuse the statement: they
# say "the encoding is incomplete", not "the document is wrong".
# S8_UNDECLARED_ARITHMETIC is a ceiling, not a stoppage (docs/27 §3): it caps the verdict at CHECKED and
# must never turn into a refusal, or a statement with a declared encoding but an undeclared convention
# would read as broken.
ESCAPE_CODES = frozenset({"OPEN_TERM", "THIN_COVERAGE", "S8_UNDECLARED_ARITHMETIC"})

# Everything else refuses. Derived rather than listed twice, so a new code cannot
# be added to the catalogue and forgotten in one of the two sets.
REFUSAL_CODES = ALL_CODES - ESCAPE_CODES

CODE_CHECK = {
    "C0_CANON": "C0",
    "S1_SCHEMA": "S1",
    "S2_NO_CORPUS": "S2",
    "S2_HASH_MISMATCH": "S2",
    "S2_CORPUS_NOT_FOUND": "S2",
    "S2_CORPUS_UNREADABLE": "S2",
    "S2_REVISION_MISMATCH": "S2",
    "S2_REVISION_UNCHECKED": "S2",
    "S2_CONTEXT_MISMATCH": "S2",
    "S2_CONTEXT_MISSING": "S2",
    "S8_SERIES_NOT_PINNED": "S8",
    "S8_UNANCHORED_QUANTITY": "S8",
    "S8_SEGMENT_GAP": "S8",
    "S8_UNDECLARED_ARITHMETIC": "S8",
    "S9_DEFEAT_UNDEFINED": "S9",
    "S9_DEFEAT_CYCLE": "S9",
    "S9_APPLICABILITY_UNSTATED": "S9",
    "S2_SPAN_NOT_FOUND": "S2",
    "S2_SPAN_AMBIGUOUS": "S2",
    "S3_UNKNOWN_RELATION": "S3",
    "S3_MISSING_COUNTERPARTY": "S3",
    "S3_OPPOSITE_CONFLICT": "S3",
    "S4_UNDEFINED_REF": "S4",
    "OPEN_TERM": "S4",
    "S4_UNDECLARED_ESCAPE": "S4",
    "S4_STALE_ESCAPE": "S4",
    "S5_EMPTY_INTERVAL": "S5",
    "S6_CONFLICT": "S6",
    "S6_UNRESOLVED_CONFLICT": "S6",
    "THIN_COVERAGE": "S7",
}

# Every code must belong to exactly one check group. Checked at import time
# because a missing group would make the report silently omit a layer.
if set(CODE_CHECK) != ALL_CODES:  # pragma: no cover - programming error
    raise AssertionError(
        f"CODE_CHECK does not cover the catalogue: {sorted(ALL_CODES ^ set(CODE_CHECK))}"
    )

# Exact strings, exact order (spec §9). The report is not allowed to reword them.
NOT_CLAIMED = [
    "legal validity",
    "completeness of the encoded law",
    "correctness of the corpus outside the pinned revision",
    "anchor.article and corpus[].revision are declared, not verified",
    "conditions[] is prose and is not interpreted",
    "cross-tuple correlative agreement is not checked (the spec does not define its orientation)",
    "the normalisation policy is fixed by this tool, not declared per statement",
]

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
ATOM_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
JURISDICTION_RE = re.compile(r"^[A-Z]{2,3}(?:-[A-Z0-9]{1,8})?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ESCAPE_REASON_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


class ParseError(Exception):
    """Input could not be read as JSON. Exit code 2: nothing to report on."""


class CanonError(Exception):
    """Input parsed but has no reproducible canonical form (C0_CANON)."""


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def _nfc(value: str) -> str:
    """Compare strings by NFC so that visually identical names are one name.

    Deliberately applied to comparisons only, never to the canonical form: the
    hash is over the bytes the author signed, and normalising it would make the
    tool's identity claim differ from the author's text.
    """
    return unicodedata.normalize("NFC", value)


def _is_text(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _parse_iso_date(value: object) -> date | None:
    """Return a date only for a real YYYY-MM-DD calendar day.

    A syntactically shaped non-date such as 2026-02-31 is a schema defect, not a
    time defect, so it must not reach S5.
    """
    if not isinstance(value, str) or not ISO_DATE_RE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _no_duplicate_keys(pairs):
    """Reject duplicate object keys: silent last-wins is how a signature lies."""
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate object key {key!r}")
        seen[key] = value
    return seen


def _reject_constant(name):
    raise ValueError(f"non-standard JSON constant {name!r} (NaN/Infinity are not JSON)")


def read_statement(path: Path) -> tuple[bytes, object]:
    """Read and parse one statement, once, returning its bytes and its value.

    Bytes are returned alongside the value because C0 is a property of the file
    (BOM, CRLF), not of the parsed object. Raises ParseError, never returns junk:
    a report needs a document to be a report *about* something.
    """
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ParseError(f"cannot read {path.name}: {exc}") from exc
    try:
        text = raw.decode("utf-8-sig")  # a BOM is tolerated here and refused by C0
    except UnicodeDecodeError as exc:
        raise ParseError(f"{path.name}: not valid UTF-8: {exc}") from exc
    try:
        document = json.loads(
            text, object_pairs_hook=_no_duplicate_keys, parse_constant=_reject_constant
        )
    except ValueError as exc:  # JSONDecodeError subclasses ValueError
        raise ParseError(f"{path.name}: not valid JSON: {exc}") from exc
    return raw, document


def _canonical_flags(raw: bytes) -> list[str]:
    """Byte-level properties that make the canonical form irreproducible.

    Checked on the file, not on the parsed object: a BOM or CRLF is invisible
    after parsing but changes the bytes another tool would hash.
    """
    flags = []
    if raw.startswith(b"\xef\xbb\xbf"):
        flags.append("file starts with a UTF-8 BOM (spec §3.1: no BOM)")
    if b"\r\n" in raw:
        flags.append("file contains CRLF line endings (spec §3.1: LF only)")
    return flags


def _reject_floats(value: object, path: str = "$") -> None:
    """Forbid floats anywhere (spec §3.3): ratios are computed, never stored."""
    if isinstance(value, float):
        raise CanonError(f"floating-point number at {path}; spec §3.3 forbids floats")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_floats(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_floats(item, f"{path}[{index}]")


def canonical_text(document: object) -> str:
    """The canonical byte form of a statement (spec §3), as a str.

    Keys are sorted at every depth, separators are minimal, non-ASCII is emitted
    literally. Array order is preserved on purpose: identity is over the bytes
    the author signed, not over an equivalence class.
    """
    _reject_floats(document)
    return json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_sha256(document: object) -> str:
    return hashlib.sha256(canonical_text(document).encode("utf-8")).hexdigest()


def find_repo_root(start: Path) -> tuple[Path, str]:
    """Walk up until a repository marker is found; say which marker decided.

    Markers: `.git` or `docs/10-SPEC-v0.1.md`. If neither exists we stop at the
    statement's own directory — but we now say so in the report (`root_source`),
    because finding F-3-1 in flowguard's review showed that a silent fallback
    turns a resolution problem into a false accusation against the corpus.
    """
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate, "marker:.git"
        if (candidate / "docs" / "10-SPEC-v0.1.md").is_file():
            return candidate, "marker:docs/10-SPEC-v0.1.md"
    return current, "statement"


def _display_path(path: Path, root: Path) -> str:
    """Repository-relative, forward-slashed path; basename if outside the root.

    Report paths must not leak absolute paths of whoever ran the tool: the same
    report has to be quotable in a public repository.
    """
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.name


def _is_repo_relative(declared: str) -> bool:
    """True for a path that stays inside the repository (spec §5: root-relative)."""
    candidate = Path(declared)
    if candidate.is_absolute() or re.match(r"^[A-Za-z]:", declared):
        return False
    if declared.startswith(("/", "\\")):
        return False
    return all(part != ".." for part in candidate.parts)


def _resolve_corpus_path(root: Path, declared: str, statement_dir: Path | None = None) -> tuple[Path | None, str]:
    """Resolve `corpus[].text` by searching upward, and say which base won.

    Finding F-3-1: a copy of the tree without a repository marker used to fail,
    because the only base tried was the fallback root. A portable tree is the
    normal way a stranger checks their own document, so the search order is:
    the root, then the statement's directory and every parent of it. The first
    existing path wins; nothing is invented.
    """
    if not _is_repo_relative(declared):
        return None, "escapes-root"
    candidates: list[Path] = [root / Path(declared)]
    if statement_dir is not None:
        base = statement_dir.resolve()
        for candidate in (base, *base.parents):
            path = candidate / Path(declared)
            if path not in candidates:
                candidates.append(path)
    for path in candidates:
        if path.is_file():
            return path, "found"
    return None, "not-found"


# ---------------------------------------------------------------------------
# findings
# ---------------------------------------------------------------------------


class Findings:
    """Ordered findings, sorted into spec order at the end (docs/11 §"Order")."""

    def __init__(self) -> None:
        self._items: list[dict] = []
        self._sequence = 0

    def add(self, code: str, atom: str | None, detail: str) -> None:
        if code not in ALL_CODES:
            raise AssertionError(f"unknown code {code!r}: the vocabulary is closed")
        self._items.append(
            {"code": code, "atom": atom, "detail": detail, "_seq": self._sequence}
        )
        self._sequence += 1

    def items(self) -> list[dict]:
        """Raw findings in insertion order; severity is a property of the code."""
        return list(self._items)

    def refusals(self) -> list[dict]:
        return [item for item in self._items if item["code"] in REFUSAL_CODES]

    def escapes(self) -> list[dict]:
        return [item for item in self._items if item["code"] in ESCAPE_CODES]

    def ordered(self, atom_order: dict[str, int]) -> list[dict]:
        """Spec order, then document order of atoms, then insertion order."""

        def key(item):
            check = CODE_CHECK[item["code"]]
            atom_index = atom_order.get(item["atom"], -1) if item["atom"] else -1
            return (CHECK_ORDER.index(check), atom_index, item["_seq"])

        return [
            {"code": item["code"], "atom": item["atom"], "detail": item["detail"]}
            for item in sorted(self._items, key=key)
        ]


# ---------------------------------------------------------------------------
# S1 — is this a statement at all
# ---------------------------------------------------------------------------


class Statement:
    """S1_SCHEMA validation plus the sanitised view that later checks need.

    Why one pass: later checks all want the same well-typed fields, and a second
    pass would drift from the first. A field that fails here is left out of the
    view, so a later check skips it instead of crashing on a wrong type. That is
    the difference between a refusal and a traceback, and only one of them is a
    report.
    """

    def __init__(self, document: object, findings: Findings) -> None:
        self.findings = findings
        self.raw = document
        self.is_object = isinstance(document, dict)
        doc: dict = document if self.is_object else {}

        self.atoms: list[dict] = []
        self.atom_ids: list[str] = []
        self.terms: dict[str, dict] = {}
        self.corpus: dict[str, dict] = {}
        # Ids that were *declared* even if the entry itself failed S1. Kept so
        # that an atom citing a malformed corpus is not ALSO told the corpus does
        # not exist — one defect, one code.
        self.corpus_declared_ids: set[str] = set()
        self.policy: str | None = None
        self.lex_specialis: list[dict] = []
        self.escapes: list[dict] = []
        # L5 collections (docs/27). Carried verbatim; the quantity pass validates them, because
        # a malformed quantity is a defect of the number, not of the document's shape.
        self.series: list[dict] = [x for x in doc.get("series", []) if isinstance(x, dict)] \
            if isinstance(doc.get("series"), list) else []
        self.quantities: list[dict] = [x for x in doc.get("quantities", []) if isinstance(x, dict)] \
            if isinstance(doc.get("quantities"), list) else []
        self.declared_escape_ids: set[str] = set()

        if not self.is_object:
            self.findings.add("S1_SCHEMA", None, "$: document must be a JSON object")
            self.id = None
            self.kind = None
            self.jurisdiction = []
            return

        self.id = self._check_id(doc)
        self.kind = self._check_kind(doc)
        self.jurisdiction = self._check_jurisdiction(doc)
        self._check_version(doc)
        self._check_corpus(doc)
        self._check_terms(doc)
        self._check_atoms(doc)
        self._check_policy(doc)
        self._check_escapes(doc)

    # -- helpers ----------------------------------------------------------
    def _err(self, atom: str | None, detail: str) -> None:
        self.findings.add("S1_SCHEMA", atom, detail)

    def _check_version(self, doc: dict) -> None:
        version = doc.get("lexspec")
        if version is None:
            self._err(None, "lexspec: required field is missing")
        elif version != SCHEMA_VERSION:
            self._err(None, f"lexspec: expected {SCHEMA_VERSION!r}, got {version!r}")

    def _check_id(self, doc: dict) -> str | None:
        value = doc.get("id")
        if value is None:
            self._err(None, "id: required field is missing")
            return None
        if not isinstance(value, str):
            self._err(None, f"id: expected string, got {type(value).__name__}")
            return None
        if not ID_RE.match(value) or len(value) > 128:
            self._err(None, f"id: {value!r} is not a lowercase slug ([a-z0-9._-], starting alphanumeric)")
        return value

    def _check_kind(self, doc: dict) -> str | None:
        value = doc.get("kind")
        if value is None:
            self._err(None, "kind: required field is missing")
            return None
        if value not in KINDS:
            self._err(None, f"kind: {value!r} is not one of {list(KINDS)}")
            return None
        return value

    def _check_jurisdiction(self, doc: dict) -> list[str]:
        value = doc.get("jurisdiction")
        if value is None:
            self._err(None, "jurisdiction: required field is missing")
            return []
        if not isinstance(value, list):
            self._err(None, "jurisdiction: expected array")
            return []
        if not value:
            # §2: "a statement about no jurisdiction is refused".
            self._err(None, "jurisdiction: must name at least one code")
            return []
        seen = set()
        for index, code in enumerate(value):
            if not isinstance(code, str) or not JURISDICTION_RE.match(code):
                self._err(None, f"jurisdiction[{index}]: {code!r} is not an uppercase code like 'RU'")
                continue
            if code in seen:
                self._err(None, f"jurisdiction[{index}]: duplicate code {code!r}")
            seen.add(code)
        return [code for code in value if isinstance(code, str)]

    def _check_corpus(self, doc: dict) -> None:
        value = doc.get("corpus")
        if value is None:
            self._err(None, "corpus: required field is missing")
            return
        if not isinstance(value, list) or not value:
            self._err(None, "corpus: must be a non-empty array")
            return
        for index, entry in enumerate(value):
            path = f"corpus[{index}]"
            if not isinstance(entry, dict):
                self._err(None, f"{path}: expected object")
                continue
            cid = entry.get("id")
            if not _is_text(cid):
                self._err(None, f"{path}.id: required non-empty string")
                cid = None
            elif not ID_RE.match(cid):
                self._err(None, f"{path}.id: {cid!r} is not a lowercase slug")
            elif cid in self.corpus:
                self._err(None, f"{path}.id: duplicate corpus id {cid!r}")
            if not _is_text(entry.get("title")):
                self._err(None, f"{path}.title: required non-empty string")
            revision = entry.get("revision")
            if not isinstance(revision, str):
                self._err(None, f"{path}.revision: required YYYY-MM-DD string")
            elif _parse_iso_date(revision) is None:
                self._err(None, f"{path}.revision: {revision!r} is not a YYYY-MM-DD calendar date")
            text = entry.get("text")
            if not _is_text(text):
                self._err(None, f"{path}.text: required non-empty string")
            elif not _is_repo_relative(text):
                self._err(
                    None,
                    f"{path}.text: {text!r} must be relative to the repository root, without drive letters or '..'",
                )
            digest = entry.get("text_sha256")
            digest_ok = isinstance(digest, str) and bool(SHA256_RE.match(digest))
            if not digest_ok:
                self._err(None, f"{path}.text_sha256: required 64-character lowercase hex sha256")
            if isinstance(cid, str):
                self.corpus_declared_ids.add(cid)
                # A corpus entry that already failed S1 is not handed to S2: one
                # defect, one code. The atom citing it is simply left un-anchored.
                if cid not in self.corpus and _is_text(text) and _is_repo_relative(text) and digest_ok:
                    self.corpus[cid] = entry

    def _check_terms(self, doc: dict) -> None:
        value = doc.get("terms")
        if value is None:
            self._err(None, "terms: required field is missing")
            return
        if not isinstance(value, list):
            self._err(None, "terms: expected array")
            return
        for index, entry in enumerate(value):
            path = f"terms[{index}]"
            if not isinstance(entry, dict):
                self._err(None, f"{path}: expected object")
                continue
            name = entry.get("name")
            if not _is_text(name):
                self._err(None, f"{path}.name: required non-empty string")
            elif _nfc(name) in self.terms:
                self._err(None, f"{path}.name: duplicate term {name!r}")
            if not _is_text(entry.get("def")):
                self._err(None, f"{path}.def: required non-empty string")
            if entry.get("status") not in TERM_STATUS:
                self._err(None, f"{path}.status: {entry.get('status')!r} is not one of {list(TERM_STATUS)}")
            if _is_text(name) and _nfc(name) not in self.terms:
                self.terms[_nfc(name)] = entry

    def _check_atoms(self, doc: dict) -> None:
        value = doc.get("atoms")
        if value is None:
            self._err(None, "atoms: required field is missing (an empty array is allowed)")
            return
        if not isinstance(value, list):
            self._err(None, "atoms: expected array")
            return
        for index, entry in enumerate(value):
            path = f"atoms[{index}]"
            if not isinstance(entry, dict):
                self._err(None, f"{path}: expected object")
                continue
            aid = entry.get("id")
            label = aid if _is_text(aid) else None
            if not _is_text(aid):
                self._err(None, f"{path}.id: required non-empty string")
            elif not ATOM_ID_RE.match(aid):
                self._err(label, f"{path}.id: {aid!r} is not a lowercase slug")
            elif aid in self.atom_ids:
                self._err(label, f"{path}.id: duplicate atom id {aid!r}")
            else:
                self.atom_ids.append(aid)

            # The enum lives in S3, not S1: a typo in the square has its own
            # code (S3_UNKNOWN_RELATION), and one defect must not be two codes.
            if not isinstance(entry.get("relation"), str):
                self._err(label, f"{path}.relation: required string naming a Hohfeld position")

            if "counterparty" not in entry:
                self._err(label, f"{path}.counterparty: required key (null is allowed where the relation is absolute)")
            else:
                counterparty = entry.get("counterparty")
                if counterparty is not None and not _is_text(counterparty):
                    self._err(label, f"{path}.counterparty: expected string or null")

            if not _is_text(entry.get("bearer")):
                self._err(label, f"{path}.bearer: required non-empty string naming a term")

            action = entry.get("action")
            if not isinstance(action, dict):
                self._err(label, f"{path}.action: required object {{verb, object, open}}")
            else:
                for field in ("verb", "object"):
                    if not _is_text(action.get(field)):
                        self._err(label, f"{path}.action.{field}: required non-empty string")
                if not isinstance(action.get("open"), bool):
                    self._err(label, f"{path}.action.open: required boolean")

            conditions = entry.get("conditions")
            if not isinstance(conditions, list):
                self._err(label, f"{path}.conditions: required array (may be empty)")
            else:
                for cindex, condition in enumerate(conditions):
                    if not _is_text(condition):
                        self._err(label, f"{path}.conditions[{cindex}]: expected non-empty string")

            temporal = entry.get("temporal")
            if not isinstance(temporal, dict):
                self._err(label, f"{path}.temporal: required object {{from, until}}")
            else:
                if _parse_iso_date(temporal.get("from")) is None:
                    self._err(label, f"{path}.temporal.from: {temporal.get('from')!r} is not a YYYY-MM-DD calendar date")
                if "until" not in temporal:
                    self._err(label, f"{path}.temporal.until: required key (null means 'no declared end')")
                elif temporal.get("until") is not None and _parse_iso_date(temporal.get("until")) is None:
                    self._err(label, f"{path}.temporal.until: {temporal.get('until')!r} is not a YYYY-MM-DD calendar date or null")

            anchor = entry.get("anchor")
            if not isinstance(anchor, dict):
                self._err(label, f"{path}.anchor: required object {{corpus, article, span}}")
            else:
                for field in ("corpus", "article", "span"):
                    if not _is_text(anchor.get(field)):
                        self._err(label, f"{path}.anchor.{field}: required non-empty string")
                note = anchor.get("note")
                if note is not None and not isinstance(note, str):
                    self._err(label, f"{path}.anchor.note: expected string")

            self.atoms.append(entry)

    def _check_policy(self, doc: dict) -> None:
        policy = doc.get("conflicts_policy")
        if not isinstance(policy, dict):
            self._err(None, "conflicts_policy: required object {default, lex_specialis}")
            return
        default = policy.get("default")
        if default not in POLICIES:
            self._err(None, f"conflicts_policy.default: {default!r} is not one of {list(POLICIES)}")
        else:
            self.policy = default
        entries = policy.get("lex_specialis")
        if entries is None:
            self._err(None, "conflicts_policy.lex_specialis: required array (may be empty)")
            return
        if not isinstance(entries, list):
            self._err(None, "conflicts_policy.lex_specialis: expected array")
            return
        for index, entry in enumerate(entries):
            path = f"conflicts_policy.lex_specialis[{index}]"
            if not isinstance(entry, dict):
                self._err(None, f"{path}: expected object {{prevailing, over}}")
                continue
            prevailing = entry.get("prevailing")
            if not _is_text(prevailing):
                self._err(None, f"{path}.prevailing: required atom id")
            elif prevailing not in self.atom_ids:
                self._err(None, f"{path}.prevailing: {prevailing!r} is not a declared atom id")
            over = entry.get("over")
            if not isinstance(over, list) or not over:
                self._err(None, f"{path}.over: required non-empty array of atom ids")
            else:
                for oindex, other in enumerate(over):
                    if not _is_text(other):
                        self._err(None, f"{path}.over[{oindex}]: expected atom id")
                    elif other not in self.atom_ids:
                        self._err(None, f"{path}.over[{oindex}]: {other!r} is not a declared atom id")
            reason = entry.get("reason")
            if reason is not None and not isinstance(reason, str):
                self._err(None, f"{path}.reason: expected string")
        self.lex_specialis = [entry for entry in entries if isinstance(entry, dict)]

    def _check_escapes(self, doc: dict) -> None:
        value = doc.get("escapes")
        if value is None:
            self._err(None, "escapes: required field is missing (declare [] when nothing is open)")
            return
        if not isinstance(value, list):
            self._err(None, "escapes: expected array")
            return
        for index, entry in enumerate(value):
            path = f"escapes[{index}]"
            if not isinstance(entry, dict):
                self._err(None, f"{path}: expected object {{atom, reason, detail}}")
                continue
            aid = entry.get("atom")
            if not _is_text(aid):
                self._err(None, f"{path}.atom: required atom id")
            elif aid not in self.atom_ids:
                self._err(aid, f"{path}.atom: {aid!r} is not a declared atom id")
            elif aid in self.declared_escape_ids:
                self._err(aid, f"{path}.atom: duplicate escape for atom {aid!r}")
            else:
                self.declared_escape_ids.add(aid)
            reason = entry.get("reason")
            if not isinstance(reason, str) or not ESCAPE_REASON_RE.match(reason):
                self._err(aid if _is_text(aid) else None, f"{path}.reason: expected an UPPER_SNAKE code")
            elif reason not in ALL_CODES:
                self._err(aid if _is_text(aid) else None, f"{path}.reason: {reason!r} is not a code from docs/11-REFUSAL-CODES.md")
            if not _is_text(entry.get("detail")):
                self._err(aid if _is_text(aid) else None, f"{path}.detail: required non-empty string")
            self.escapes.append(entry)


# ---------------------------------------------------------------------------
# per-atom identity used by S3, S5, S6, S7
# ---------------------------------------------------------------------------


def atom_identity(atom: dict) -> dict | None:
    """The (tuple, relation, interval) view of an atom, or None if unusable.

    None means "a check that needs this cannot run", never "this atom is fine":
    every caller treats it as skip, and S1/S5 already reported the defect.
    """
    bearer = atom.get("bearer")
    action = atom.get("action")
    temporal = atom.get("temporal")
    if not isinstance(bearer, str) or not isinstance(action, dict) or not isinstance(temporal, dict):
        return None
    verb = action.get("verb")
    obj = action.get("object")
    if not isinstance(verb, str) or not isinstance(obj, str):
        return None
    counterparty = atom.get("counterparty")
    if counterparty is not None and not isinstance(counterparty, str):
        return None
    start = _parse_iso_date(temporal.get("from"))
    if start is None:
        return None
    until_raw = temporal.get("until")
    if until_raw is None:
        end = None
    else:
        end = _parse_iso_date(until_raw)
        if end is None:
            return None
    return {
        "tuple": (
            _nfc(bearer),
            _nfc(verb),
            _nfc(obj),
            None if counterparty is None else _nfc(counterparty),
        ),
        "relation": atom.get("relation"),
        "start": start,
        "end": end,
    }


def _overlap(a: dict, b: dict) -> bool:
    """Closed-interval overlap; until=null is unbounded (spec §6)."""
    a_end = a["end"] or date.max
    b_end = b["end"] or date.max
    return a["start"] <= b_end and b["start"] <= a_end


def _interval_label(identity: dict) -> str:
    end = identity["end"].isoformat() if identity["end"] else "open"
    return f"{identity['start'].isoformat()}..{end}"


def _tuple_label(identity: dict) -> str:
    bearer, verb, obj, counterparty = identity["tuple"]
    return f"({bearer}, {verb}, {obj}, {counterparty if counterparty is not None else 'world'})"


# ---------------------------------------------------------------------------
# S2 — anchoring
# ---------------------------------------------------------------------------


def load_corpora(
    root: Path, statement: Statement, findings: Findings, statement_dir: Path | None = None
) -> dict[str, dict]:
    """Hash and decode every declared corpus. Returns {id: {"text", "usable"}}.

    The pin is by content, never by URL (spec §5), so this is the only place
    that decides whether a corpus may be used for span search. A corpus that
    cannot be verified is reported once, at statement level, and every atom that
    cites it is left un-anchored — no per-atom duplicate of the same defect.
    """
    loaded: dict[str, dict] = {}
    for cid, entry in statement.corpus.items():
        declared = entry.get("text")
        digest = entry.get("text_sha256")
        if not isinstance(declared, str) or not isinstance(digest, str):
            loaded[cid] = {"text": None, "usable": False}
            continue
        path, resolved = _resolve_corpus_path(root, declared, statement_dir)
        if resolved == "escapes-root":
            findings.add("S2_NO_CORPUS", None, f"corpus {cid!r}: text path {declared!r} escapes the repository root")
            loaded[cid] = {"text": None, "usable": False}
            continue
        if path is None:
            # A missing file is not a wrong hash. Saying "hash mismatch" here told
            # the reader their corpus had been substituted when in fact the path
            # never resolved — see finding F-3-1.
            findings.add(
                "S2_CORPUS_NOT_FOUND",
                None,
                f"corpus {cid!r}: no file at {declared!r}, searched from the repository root and upward from the statement; "
                f"the declared sha256 was never compared",
            )
            loaded[cid] = {"text": None, "usable": False}
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            findings.add(
                "S2_CORPUS_UNREADABLE",
                None,
                f"corpus {cid!r}: file {_display_path(path, root)!r} exists but could not be read, so no hash was compared",
            )
            loaded[cid] = {"text": None, "usable": False}
            continue
        actual = hashlib.sha256(raw).hexdigest()
        if actual != digest:
            findings.add(
                "S2_HASH_MISMATCH",
                None,
                f"corpus {cid!r}: declared text_sha256 {digest} but file hashes to {actual}; re-pin, never edit the hash alone",
            )
            loaded[cid] = {"text": None, "usable": False}
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            findings.add(
                "S2_CORPUS_UNREADABLE",
                None,
                f"corpus {cid!r}: the declared sha256 MATCHES the file, but its bytes are not valid UTF-8, so no span "
                f"can be searched in it; re-pinning would be the wrong remedy",
            )
            loaded[cid] = {"text": None, "usable": False}
            continue
        loaded[cid] = {"text": text, "usable": True}
    return loaded


def _normalize(text: str) -> str:
    """Spec §5 rule 0: LF, collapsed whitespace, decoded entities, no markup.

    The W3C TextQuoteSelector requires the text to be normalised before recording, and a quote that fails only
    because the source wraps is our defect, not the author's. The same policy is implemented in
    tools/span_hint.py; they must agree, which is why both are stated as the same rule.
    """
    import html as _html

    text = _html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _find_regions(haystack: str, needle: str) -> list[int]:
    out: list[int] = []
    start = 0
    while True:
        hit = haystack.find(needle, start)
        if hit == -1:
            return out
        out.append(hit)
        start = hit + 1


def check_anchors(
    statement: Statement, corpora: dict[str, dict], findings: Findings
) -> dict[str, bool]:
    """S2 per atom. Returns {atom_id: anchored}."""
    anchored: dict[str, bool] = {}
    for atom in statement.atoms:
        aid = atom.get("id")
        if not isinstance(aid, str):
            continue  # S1 refused the id; there is nothing to key this on
        anchor = atom.get("anchor")
        if not isinstance(anchor, dict):
            anchored[aid] = False
            continue
        cid = anchor.get("corpus")
        span = anchor.get("span")
        if not isinstance(cid, str) or not isinstance(span, str) or not span:
            anchored[aid] = False
            continue
        corpus = corpora.get(cid)
        if corpus is None:
            if cid in statement.corpus_declared_ids:
                # The corpus entry exists but failed S1, so there is no text to
                # search. S1 already refused; do not restate it as a missing corpus.
                anchored[aid] = False
                continue
            findings.add("S2_NO_CORPUS", aid, f"anchor.corpus {cid!r} names no corpus[] entry in this statement")
            anchored[aid] = False
            continue
        if not corpus["usable"]:
            # Already reported at statement level; the atom is simply not anchored.
            anchored[aid] = False
            continue
        # Spec §5 rule 0: normalise before matching. A quote that is correct after collapsing a line break must
        # anchor; refusing it was our defect, and the detail says so instead of blaming the text.
        haystack = _normalize(corpus["text"])
        needle = _normalize(span)
        occurrences = len(_find_regions(haystack, needle))
        if occurrences == 0:
            raw_hit = corpus["text"].count(span)
            detail = f"span does not occur in corpus {cid!r} even after normalisation: {span[:80]!r}"
            detail += (
                f"; it occurs {raw_hit} time(s) in the raw text"
                if raw_hit
                else "; it occurs 0 times in the raw text either"
            )
            findings.add("S2_SPAN_NOT_FOUND", aid, detail)
            anchored[aid] = False
        elif occurrences > 1:
            findings.add(
                "S2_SPAN_AMBIGUOUS",
                aid,
                f"span selects {occurrences} regions in corpus {cid!r} after normalisation; a citation that can "
                f"re-point is not evidence (spec §5 rule 4)",
            )
            anchored[aid] = False
        else:
            # Context is part of the anchor (spec §5): if a statement supplies it, it must match; if the span is
            # shorter than 40 normalised characters, context is required, because that is the only regime where
            # ambiguity was ever observed (docs/29 P4: 11 of 604 short quotes, 0 of 585 long ones).
            prefix = atom.get("anchor", {}).get("prefix")
            suffix = atom.get("anchor", {}).get("suffix")
            if prefix or suffix:
                position = _find_regions(haystack, needle)[0]
                end = position + len(needle)
                # Context is expressed in normalised characters: the text is normalised before recording, so the
                # window is a normalised window too.
                pn = _normalize(prefix).strip() if prefix else ''
                sn = _normalize(suffix).strip() if suffix else ''
                # A normalised window may begin or end on a space, and the stored context is stripped, so both
                # sides are trimmed before comparison: the question is whether the context matches, not whether
                # its whitespace happens to line up.
                ok_prefix = not pn or haystack[max(0, position - len(pn) - 4) : position].rstrip().endswith(pn)
                ok_suffix = not sn or haystack[end : end + len(sn) + 4].lstrip().startswith(sn)
                if not (ok_prefix and ok_suffix):
                    findings.add(
                        "S2_CONTEXT_MISMATCH",
                        aid,
                        "the declared prefix/suffix do not surround the span in the pinned text; context that is "
                        "not checked is decoration",
                    )
                    anchored[aid] = False
                    continue
            elif len(needle) < 40:
                findings.add(
                    "S2_CONTEXT_MISSING",
                    aid,
                    f"the span is {len(needle)} characters after normalisation; below 40 a 32-character prefix and "
                    f"suffix are required (spec §5, measured in docs/29 P4)",
                )
                anchored[aid] = False
                continue
            anchored[aid] = True
    return anchored


# ---------------------------------------------------------------------------
# S3 / S5 / S6 — the square, time, incompatibility
# ---------------------------------------------------------------------------


def check_hohfeld(statement: Statement, findings: Findings) -> dict[str, dict]:
    """S3. Returns {atom_id: identity} for the atoms S6 can compare."""
    identities: dict[str, dict] = {}
    for atom in statement.atoms:
        aid = atom.get("id") if isinstance(atom.get("id"), str) else None
        relation = atom.get("relation")
        if not isinstance(relation, str):
            continue  # S1 already refused the type
        if relation not in RELATIONS:
            findings.add(
                "S3_UNKNOWN_RELATION",
                aid,
                f"relation {relation!r} is not one of the eight Hohfeld positions",
            )
            continue
        counterparty = atom.get("counterparty")
        if counterparty is None and relation not in ABSOLUTE_CAPABLE:
            findings.add(
                "S3_MISSING_COUNTERPARTY",
                aid,
                f"relation {relation!r} is relative: it needs a counterparty (absolute relations are "
                f"{sorted(ABSOLUTE_CAPABLE)})",
            )
        identity = atom_identity(atom)
        if identity is not None:
            identities[aid] = identity

    # Opposite pairs on the same tuple over overlapping time (spec §4.2). This is
    # the check the whole layer exists for: "A may do X" next to "A may not do X".
    order = [aid for aid in identities]
    for i, first_id in enumerate(order):
        first = identities[first_id]
        for second_id in order[i + 1 :]:
            second = identities[second_id]
            if first["tuple"] != second["tuple"]:
                continue
            if OPPOSITE.get(first["relation"]) != second["relation"]:
                continue
            if not _overlap(first, second):
                continue
            findings.add(
                "S3_OPPOSITE_CONFLICT",
                second_id,
                f"{first_id} asserts {first['relation']!r} and {second_id} asserts its opposite "
                f"{second['relation']!r} for {_tuple_label(first)} over overlapping time "
                f"({_interval_label(first)} / {_interval_label(second)})",
            )
    return identities


def check_temporal(statement: Statement, findings: Findings) -> None:
    """S5. Date *format* is S1's business; S5 is about the interval being empty."""
    for atom in statement.atoms:
        aid = atom.get("id") if isinstance(atom.get("id"), str) else None
        temporal = atom.get("temporal")
        if not isinstance(temporal, dict):
            continue
        start = _parse_iso_date(temporal.get("from"))
        end = _parse_iso_date(temporal.get("until")) if temporal.get("until") is not None else None
        if start is None or (temporal.get("until") is not None and end is None):
            continue  # S1 already refused the format
        if end is not None and start > end:
            findings.add(
                "S5_EMPTY_INTERVAL",
                aid,
                f"temporal.from {start.isoformat()} is after temporal.until {end.isoformat()}: the interval is empty",
            )


def _resolved_by_specialis(statement: Statement, first_id: str, second_id: str) -> bool:
    """True when lex_specialis names a winner for this pair, in either direction."""
    for entry in statement.lex_specialis:
        prevailing = entry.get("prevailing")
        over = entry.get("over")
        if not isinstance(prevailing, str) or not isinstance(over, list):
            continue
        if prevailing == first_id and second_id in over:
            return True
        if prevailing == second_id and first_id in over:
            return True
    return False


def check_conflicts(statement: Statement, identities: dict[str, dict], findings: Findings) -> None:
    """S6. Correlative mismatch on one ordered pair, resolved only by the policy.

    Why this and not "any two distinct relations on one tuple": the pair the
    checker can judge without inventing a compatibility matrix is the one
    docs/10-SPEC-v0.1.md §4.3 names — a correlative *written out* and checked for
    agreement. If A has a `right` against B that B delivers, the correlative is
    B's `duty` toward A; writing that duty on A's own side of the same ordered
    pair does not agree with the claim, and the document is asserting two things
    about one pair of parties over the same act.

    Opposite relations on one tuple are *not* handled here: those are the hard
    contradictions of S3, which no policy can cure, and one defect must not
    produce two codes.
    """
    policy = statement.policy
    if policy is None:
        return  # S1 refused the policy; a conflict verdict would be ungrounded
    order = list(identities)
    for i, first_id in enumerate(order):
        first = identities[first_id]
        for second_id in order[i + 1 :]:
            second = identities[second_id]
            if first["tuple"] != second["tuple"]:
                continue
            if CORRELATIVE.get(first["relation"]) != second["relation"]:
                continue
            if not _overlap(first, second):
                continue
            label = _tuple_label(first)
            detail = (
                f"{first_id} asserts {first['relation']!r} for {label} and {second_id} asserts its "
                f"correlative {second['relation']!r} for the same ordered pair over overlapping time "
                f"({_interval_label(first)} / {_interval_label(second)}); a correlative is held by the "
                f"other party, not by the same one"
            )
            if policy == "report":
                findings.add("S6_CONFLICT", second_id, f"{detail}; conflicts_policy.default is 'report'")
            elif policy == "lex_specialis":
                if not _resolved_by_specialis(statement, first_id, second_id):
                    findings.add(
                        "S6_UNRESOLVED_CONFLICT",
                        second_id,
                        f"{detail}; policy 'lex_specialis' requires the pair to be named in "
                        f"conflicts_policy.lex_specialis with a prevailing atom",
                    )
            elif policy == "lex_posterior":
                if first["start"] == second["start"]:
                    findings.add(
                        "S6_UNRESOLVED_CONFLICT",
                        second_id,
                        f"{detail}; policy 'lex_posterior' cannot order atoms that start on the same day "
                        f"({first['start'].isoformat()})",
                    )


# ---------------------------------------------------------------------------
# S4 — closure and escape accounting
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# L5 — quantities (docs/27). Integer arithmetic only: rates in ten-thousandths of
# a percent, money in minor units, dates as ordinals.
# ---------------------------------------------------------------------------


def _series_paths(
    root: Path, statement: "Statement", findings: "Findings", loaded_corpora: dict
) -> dict[str, dict]:
    """Load and verify every declared series. A series without a verifiable pin is unusable."""
    loaded: dict[str, dict] = {}
    for entry in getattr(statement, "series", []):
        sid = entry.get("id")
        declared = entry.get("path")
        digest = entry.get("digest")
        if not isinstance(sid, str) or not isinstance(declared, str) or not isinstance(digest, str):
            findings.add("S8_SERIES_NOT_PINNED", None, f"series {sid!r}: id, path and digest are required")
            continue
        if not _is_repo_relative(declared):
            findings.add(
                "S8_SERIES_NOT_PINNED",
                None,
                f"series {sid!r}: path {declared!r} escapes the repository root; a pin must be a path inside it",
            )
            continue
        path = root / Path(declared)
        if not path.is_file():
            findings.add("S8_SERIES_NOT_PINNED", None, f"series {sid!r}: pinned file {declared!r} is missing")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            findings.add(
                "S8_SERIES_NOT_PINNED",
                None,
                f"series {sid!r}: declared digest {digest} but file hashes to {actual}",
            )
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            points = [(p["date"], int(p["value_bp"])) for p in data["points"]]
        except Exception:  # noqa: BLE001 - a malformed pin is not a usable source
            findings.add("S8_SERIES_NOT_PINNED", None, f"series {sid!r}: pinned file is not a usable series")
            continue

        # The basis is checked exactly as an atom's anchor is: a provenance claim that is not verified is a
        # sentence, and the audit of 2026-10-29 found the shipped example pointing at a span that existed nowhere.
        basis = entry.get("basis") or {}
        b_corpus, b_span = basis.get("corpus"), basis.get("span")
        if isinstance(b_corpus, str) and isinstance(b_span, str):
            target = statement.corpus.get(b_corpus)
            if target is None:
                findings.add(
                    "S2_NO_CORPUS", None, f"series {sid!r}: basis.corpus {b_corpus!r} names no corpus entry"
                )
            elif not (loaded_corpora.get(b_corpus) or {}).get("usable", False):
                pass  # already reported at corpus level
            else:
                haystack = _normalize(loaded_corpora[b_corpus]["text"])
                needle = _normalize(b_span)
                hits = _find_regions(haystack, needle)
                if not hits:
                    findings.add(
                        "S2_SPAN_NOT_FOUND",
                        None,
                        f"series {sid!r}: basis span does not occur in corpus {b_corpus!r} after normalisation; "
                        f"the number's provenance is asserted, not verified",
                    )
                elif len(hits) > 1:
                    findings.add(
                        "S2_SPAN_AMBIGUOUS",
                        None,
                        f"series {sid!r}: basis span selects {len(hits)} regions in corpus {b_corpus!r}",
                    )
        points.sort()
        loaded[sid] = {"points": points, "publisher": data.get("publisher")}
    return loaded


def _rate_at(points: list[tuple[str, int]], day: str) -> int | None:
    value = None
    for date, bp in points:
        if date <= day:
            value = bp
        else:
            break
    return value


def _segments(
    points: list[tuple[str, int]],
    start: str,
    end: str,
    payments: list[dict] | None = None,
    cut_years: bool = False,
) -> list[dict]:
    """Cut [start, end] at every rate change and, when asked, at every payment.

    A payment reduces the base from the day after it was made: the judgment prints a 27.07.2018 payment and a
    reduced base starting 28.07.2018, and a second payment on 31.07.2018 with the final base from 01.08.2018.
    Boundaries are inclusive on both ends, because that is how a court writes a period.
    """
    import datetime as _dt

    def shift(date: str, days: int) -> str:
        y, m, d = (int(x) for x in date.split("-"))
        return (_dt.date(y, m, d) + _dt.timedelta(days=days)).isoformat()

    boundaries = [start]
    if cut_years:
        # actual/actual changes the denominator on 1 January, so a period must be cut there even when the
        # rate does not change. The judgment prints exactly that: 16.12-31.12.2019 at 365, 01.01-09.02.2020
        # at 366, both at 6.25 %.
        def leap(y: int) -> bool:
            return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0

        year = int(start[:4])
        while f"{year + 1}-01-01" <= end:
            # only when the length of the year actually changes: 2018 and 2019 are both 365 days, and the
            # judgment does not cut there either - it cuts only at 01.01.2020, where 366 begins.
            if leap(year) != leap(year + 1):
                boundaries.append(f"{year + 1}-01-01")
            year += 1
    for date, _bp in points:
        if start < date <= end and date not in boundaries:
            boundaries.append(date)
    for payment in payments or []:
        day = payment.get("date")
        if isinstance(day, str) and start < day <= end:
            effective = shift(day, 1)
            if effective <= end and effective not in boundaries:
                boundaries.append(effective)
    boundaries.sort()

    out = []
    for i, begin in enumerate(boundaries):
        stop = shift(boundaries[i + 1], -1) if i + 1 < len(boundaries) else end
        out.append({"from": begin, "to": stop, "days": _days(begin, stop), "value_bp": _rate_at(points, begin)})
    return out


def _money_minor(spec: dict) -> int | None:
    """A literal amount in minor units: {value, scale}. Integer only - a float never enters this path."""
    value, scale = spec.get("value"), spec.get("scale")
    if not isinstance(value, int) or not isinstance(scale, int) or not 0 <= scale <= 6:
        return None
    return value


def _apply_payments(base_minor: int, payments: list[dict], begin: str) -> int:
    """The base in force on `begin`: every payment dated strictly before it has reduced the principal."""
    out = base_minor
    for payment in payments:
        day, amount = payment.get("date"), payment.get("value")
        if isinstance(day, str) and isinstance(amount, int) and day < begin:
            out -= amount
    return out


def _interest_minor(base_minor: int, days: int, value_bp: int, days_in_year: int, digits: int):
    """base * days * (value_bp / 10000 %) / days_in_year, rounded half-up to `digits` places.

    Decimal from integers, never float: the canonical form forbids floats and so does this arithmetic.
    """
    from decimal import Decimal, ROUND_HALF_UP

    rate = Decimal(value_bp) / Decimal(10000) / Decimal(100)
    value = Decimal(base_minor) * Decimal(days) * rate / Decimal(days_in_year)
    # money is integer kopecks: the rounding is to the nearest kopeck, not to a fraction of one.
    quantum = Decimal(1)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def _ordinal(date: str) -> int:
    import datetime as _dt
    y, m, d = (int(x) for x in date.split("-"))
    return _dt.date(y, m, d).toordinal()


def _days(begin: str, stop: str) -> int:
    return _ordinal(stop) - _ordinal(begin) + 1


def check_quantities(
    root: Path, statement: "Statement", findings: "Findings", loaded_corpora: dict
) -> dict[str, dict]:
    """Evaluate every quantity. Returns {id: {"ok": bool, "segments": [...], "amount": int|None}}."""
    series = _series_paths(root, statement, findings, loaded_corpora)
    results: dict[str, dict] = {}
    for quantity in getattr(statement, "quantities", []):
        qid = quantity.get("id")
        kind = quantity.get("kind")
        if not isinstance(qid, str) or kind not in ("literal", "rate_of"):
            findings.add("S8_UNANCHORED_QUANTITY", None, f"quantity {qid!r}: id and a known kind are required")
            results[str(qid)] = {"ok": False}
            continue
        if kind == "literal":
            if not isinstance(quantity.get("value"), int):
                findings.add("S8_UNANCHORED_QUANTITY", None, f"quantity {qid!r}: a literal needs an integer value")
                results[qid] = {"ok": False}
                continue
            results[qid] = {"ok": True, "kind": "literal", "amount": quantity["value"], "segments": []}
            continue

        sid = quantity.get("series")
        period = quantity.get("period") or {}
        source = series.get(sid)
        if source is None:
            findings.add(
                "S8_SERIES_NOT_PINNED",
                None,
                f"quantity {qid!r}: series {sid!r} is not a verifiable pinned series",
            )
            results[qid] = {"ok": False}
            continue
        begin, stop = period.get("from"), period.get("to")
        if not (isinstance(begin, str) and isinstance(stop, str)):
            findings.add("S8_SEGMENT_GAP", None, f"quantity {qid!r}: period.from and period.to are required")
            results[qid] = {"ok": False}
            continue
        payments = [p for p in (quantity.get("payments") or []) if isinstance(p, dict)]
        segments = _segments(
            source["points"], begin, stop, payments,
            cut_years=(period.get("day_count") == "actual/actual"),
        )
        gap = [s for s in segments if s["value_bp"] is None]
        if gap:
            findings.add(
                "S8_SEGMENT_GAP",
                None,
                f"quantity {qid!r}: the series has no value for {gap[0]['from']}..{gap[0]['to']}",
            )
            results[qid] = {"ok": False, "segments": segments}
            continue
        day_count = (period.get("day_count") or "undeclared")
        rounding = (quantity.get("rounding") or {}).get("mode") or "undeclared"
        if day_count == "undeclared" or rounding == "undeclared":
            findings.add(
                "S8_UNDECLARED_ARITHMETIC",
                None,
                f"quantity {qid!r}: day_count={day_count!r}, rounding={rounding!r}; the verdict is capped at CHECKED "
                f"(docs/27 §3). Declare both with a basis and the cap lifts without touching code",
            )
        base_spec = quantity.get("base_amount")
        base_minor = _money_minor(base_spec) if isinstance(base_spec, dict) else None
        digits = int((quantity.get("rounding") or {}).get("digits", 2))
        amount = None
        total = None
        if base_minor is not None and day_count == "actual/actual" and rounding == "half_up":
            amount = []
            total = 0
            for segment in segments:
                today = segment["from"]
                base_today = _apply_payments(base_minor, payments, today)
                year = int(today[:4])
                leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
                days_in_year = 366 if leap else 365
                interest = _interest_minor(base_today, segment["days"], segment["value_bp"], days_in_year, digits)
                segment["base_minor"] = base_today
                segment["days_in_year"] = days_in_year
                segment["interest"] = str(interest)
                amount.append(str(interest))
                total += int(interest)
            segments = segments
        results[qid] = {
            "ok": True,
            "kind": "rate_of",
            "segments": segments,
            "day_count": day_count,
            "rounding": rounding,
            "base": quantity.get("base"),
            "total_minor": total,
        }
    return results


# ---------------------------------------------------------------------------
# L2b — defeat (docs/13 §3). Records which position defeats which, and refuses
# when the applicability fact needed to decide is absent.
# ---------------------------------------------------------------------------


def check_revisions(statement: "Statement", corpora: dict[str, dict], findings: "Findings") -> None:
    """A revision declared in a statement must agree with the revision in the corpus file's own header.

    The audit of 2026-10-29 found `revision` was only shape-checked as a date: a statement could claim any edition
    and the verdict did not change. A declaration nobody compares is a sentence, and the report's own claim is that
    a verdict is about (statement, encoding, corpus@revision).
    """
    import re as _re

    header_line = _re.compile(r"^#\s*REVISION:\s*(.+)$", _re.M)
    for cid, entry in statement.corpus.items():
        declared = entry.get("revision")
        loaded = corpora.get(cid) or {}
        text = loaded.get("text")
        if not isinstance(declared, str) or not text:
            continue
        match = header_line.search(text[:2000])
        if not match:
            findings.add(
                "S2_REVISION_UNCHECKED",
                None,
                f"corpus {cid!r}: revision {declared!r} is declared, but the file carries no '# REVISION:' header to "
                f"compare it with",
            )
            continue
        stated = match.group(1).strip()
        if declared not in stated:
            findings.add(
                "S2_REVISION_MISMATCH",
                None,
                f"corpus {cid!r}: statement declares revision {declared!r}, the file's header says {stated!r}",
            )


def check_defeat(statement: "Statement", findings: "Findings") -> dict[str, str]:
    """Return {atom_id: established | refuted | both | neither}.

    The four values are the report's, not the atom's (Arxo's result model): an atom states a position, the report
    states what came of it given the asserted applicability. Nothing here decides whether an exception *should*
    apply — that remains an asserted fact with a citation, and D4 says an unasserted fact is a refusal rather
    than a silent negation.
    """
    atoms = {a.get("id"): a for a in statement.atoms if isinstance(a.get("id"), str)}
    defeated_by: dict[str, list[str]] = {}
    for aid, atom in atoms.items():
        excepts = atom.get("excepts")
        if excepts is None:
            continue
        if not isinstance(excepts, list):
            findings.add("S9_DEFEAT_UNDEFINED", aid, "excepts: expected an array of atom ids")
            continue
        for target in excepts:
            if not isinstance(target, str) or target not in atoms:
                findings.add("S9_DEFEAT_UNDEFINED", aid, f"excepts names {target!r}, which is not an atom here")
                continue
            if target == aid:
                findings.add("S9_DEFEAT_CYCLE", aid, "an atom cannot except itself")
                continue
            defeated_by.setdefault(target, []).append(aid)

    # cycles over the defeat relation: a defeats b, b defeats a
    for target, defeaters in defeated_by.items():
        for defeater in defeaters:
            if target in defeated_by.get(defeater, []):
                findings.add(
                    "S9_DEFEAT_CYCLE",
                    defeater,
                    f"{defeater!r} excepts {target!r} while {target!r} excepts {defeater!r}; priority is not a way "
                    f"out of a cycle, it is a way to choose inside one",
                )

    status: dict[str, str] = {}
    for aid, atom in atoms.items():
        holders = defeated_by.get(aid, [])
        asserted = [d for d in holders if atoms.get(d, {}).get("applies") is True]
        unknown = [d for d in holders if atoms.get(d, {}).get("applies") is None]
        if unknown:
            findings.add(
                "S9_APPLICABILITY_UNSTATED",
                aid,
                f"{aid!r} is defeated by {unknown[0]!r}, whose applicability is not asserted; silence is not "
                f"negation (D4) - set applies: true or false with a citation",
            )
            status[aid] = "neither"
        elif asserted:
            status[aid] = "refuted"
        elif atom.get("applies") is False:
            status[aid] = "neither"
        else:
            status[aid] = "established"
    return status


def check_closure(
    statement: Statement,
    anchored: dict[str, bool],
    findings: Findings,
    quantities: dict[str, dict] | None = None,
) -> list[dict]:
    """S4. Returns one entry per atom: {"id", "index", "reasons"}.

    Closure is the five-part test of spec §8. Every atom in the statement is
    walked — including atoms S1 refused, because §8 says a malformed atom cannot
    be closed and must therefore lower coverage instead of vanishing from the
    arithmetic. When a closure input is missing altogether, the reason names that
    instead of pretending the atom is open for a substantive reason: the detail
    of an OPEN_TERM is supposed to tell an author what to fix.

    Escape accounting is membership-only (§8: the checker verifies that
    `escapes[]` lists the atom, not the wording of its `reason`), which is why a
    declared escape whose prose disagrees with the computed cause is still
    accepted.
    """
    entries: list[dict] = []
    for index, atom in enumerate(statement.atoms):
        aid = atom.get("id") if isinstance(atom.get("id"), str) else None
        reasons: list[str] = []

        quantity_id = atom.get("quantity")
        if isinstance(quantity_id, str) and quantities is not None:
            outcome = quantities.get(quantity_id, {"ok": False})
            if not outcome.get("ok", False):
                findings.add(
                    "S8_UNANCHORED_QUANTITY",
                    aid,
                    f"atom cites quantity {quantity_id!r}, which did not evaluate; a number that cannot be traced "
                    f"leaves the atom open",
                )
                reasons.append(f"quantity {quantity_id!r} did not evaluate")

        def term_problem(field: str, value: object, *, required: bool) -> None:
            if value is None and not required:
                return  # an absent counterparty is not a closure defect (§8.2)
            if not isinstance(value, str) or value.strip() == "":
                reasons.append(f"{field} is missing or not a string (S1_SCHEMA)")
                return
            term = statement.terms.get(_nfc(value))
            if term is None:
                findings.add(
                    "S4_UNDEFINED_REF",
                    aid,
                    f"{field} {value!r} is not defined in terms[]; define it or declare it open and escape the atom",
                )
                reasons.append(f"{field} {value!r} is undefined")
            elif term.get("status") == "open":
                reasons.append(f"{field} {value!r} is an open term")

        term_problem("bearer", atom.get("bearer"), required=True)
        term_problem("counterparty", atom.get("counterparty"), required=False)

        action = atom.get("action")
        if not isinstance(action, dict):
            reasons.append("action is missing (S1_SCHEMA), so action.open and action.object cannot be read")
        else:
            term_problem("action.object", action.get("object"), required=True)
            if action.get("open") is True:
                reasons.append("action.open is true")
            elif not isinstance(action.get("open"), bool):
                reasons.append("action.open is not a boolean (S1_SCHEMA)")

        anchor = atom.get("anchor")
        anchor_shape_ok = (
            isinstance(anchor, dict)
            and isinstance(anchor.get("corpus"), str)
            and isinstance(anchor.get("span"), str)
        )
        if not anchor_shape_ok:
            reasons.append("anchor is missing or incomplete (S1_SCHEMA), so the atom cannot be anchored")
        elif not anchored.get(aid, False):
            reasons.append("atom is not anchored")

        entries.append({"id": aid, "index": index, "reasons": reasons})
        if reasons:
            findings.add("OPEN_TERM", aid, "; ".join(reasons))

    closed_ids = {entry["id"] for entry in entries if not entry["reasons"] and entry["id"] is not None}
    declared = statement.declared_escape_ids

    for entry in entries:
        if not entry["reasons"]:
            continue
        aid = entry["id"]
        if aid is None:
            findings.add(
                "S4_UNDECLARED_ESCAPE",
                None,
                f"atoms[{entry['index']}] is not closed ({'; '.join(entry['reasons'])}) and has no id, "
                f"so escapes[] cannot list it",
            )
        elif aid not in declared:
            findings.add(
                "S4_UNDECLARED_ESCAPE",
                aid,
                f"atom is not closed ({'; '.join(entry['reasons'])}) but escapes[] does not list it; "
                f"an undeclared escape silently reduces coverage in the author's favour",
            )

    for aid in sorted(closed_ids & declared):
        findings.add(
            "S4_STALE_ESCAPE",
            aid,
            "escapes[] lists this atom but the checker computed it as closed; "
            "a stale escape makes the report look more cautious than the encoding is",
        )
    return entries


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------


def _check_statuses(findings: Findings) -> dict[str, str]:
    """Per-check summary: fail / escape / pass, in spec order.

    Reports both severities so a reader can see that, say, S2 passed while S4
    recorded an escape — the verdict alone does not say which layer is thin.
    """
    statuses = {}
    for check in CHECK_ORDER:
        items = [item for item in findings.items() if CODE_CHECK[item["code"]] == check]
        if any(item["code"] in REFUSAL_CODES for item in items):
            statuses[check] = "fail"
        elif items:
            statuses[check] = "escape"
        else:
            statuses[check] = "pass"
    return statuses


def analyze_file(
    path: Path, threshold: float = DEFAULT_THRESHOLD, root: Path | None = None
) -> dict:
    """Check one statement file and return the report dict.

    Raises ParseError only when there is no document to report on at all. Every
    other defect becomes a finding, because a report that says nothing is worse
    than one that says "REFUSED, and here is why".
    """
    if not (0.0 <= threshold <= 1.0):
        raise ValueError("coverage threshold must be between 0.0 and 1.0")

    raw, document = read_statement(path)
    findings = Findings()
    for flag in _canonical_flags(raw):
        findings.add("C0_CANON", None, flag)

    canonical_ok = True
    canonical_hash: str | None = None
    try:
        text = canonical_text(document)
        # C0 asserts reproducibility, so assert it: a second pass over the
        # canonical bytes must be a fixed point (spec §3, "computing it twice").
        if canonical_text(json.loads(text)) != text:
            canonical_ok = False
            findings.add("C0_CANON", None, "canonical form is not a fixed point: re-serialising it changed the bytes")
        canonical_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    except CanonError as exc:
        canonical_ok = False
        findings.add("C0_CANON", None, str(exc))

    if root is None:
        root, root_source = find_repo_root(path.parent)
    else:
        root_source = "explicit"
    statement = Statement(document, findings)
    atom_order = {}
    for index, atom in enumerate(statement.atoms):
        aid = atom.get("id")
        if isinstance(aid, str) and aid not in atom_order:
            atom_order[aid] = index

    corpora = load_corpora(root, statement, findings, path.parent)
    anchored = check_anchors(statement, corpora, findings)
    identities = check_hohfeld(statement, findings)
    check_temporal(statement, findings)
    check_conflicts(statement, identities, findings)
    check_revisions(statement, corpora, findings)
    position_status = check_defeat(statement, findings)
    quantities = check_quantities(root, statement, findings, corpora)
    closure = check_closure(statement, anchored, findings, quantities)

    # The denominator is every atom in the statement (§8), including atoms S1
    # refused: a malformed atom cannot be closed, so it must not vanish from the
    # arithmetic. `closure` has one entry per atom, so len() and len(atoms) agree.
    # An atom that is not closed cannot be reported as established: closure is about the encoding, and an
    # open atom is exactly the case where the encoding does not yet say what the position is.
    for entry in closure:
        if entry['reasons'] and entry.get('id') in position_status:
            position_status[entry['id']] = 'neither'

    total = len(statement.atoms)
    closed = sum(1 for entry in closure if not entry["reasons"])
    coverage_exact = (closed / total) if total else 0.0
    coverage = round(coverage_exact, 3)
    # The threshold must decide on the exact value: comparing a rounded number makes the boundary depend on a
    # display convention (audit finding 16).
    if coverage_exact < threshold:
        findings.add(
            "THIN_COVERAGE",
            None,
            f"coverage {coverage:.3f} is below the threshold {threshold:.3f}: {closed}/{total} atoms closed. "
            f"THIN_COVERAGE is not a defect in the law; it says the encoding is too thin for the verdict requested",
        )

    # The threshold is a reporting metric, not a verdict rule (ADR-0010). Coverage below 1.0 already
    # implies a declared escape, and an escape already caps the verdict at CHECKED, so the threshold
    # term could never decide anything. flowguard's review asked for a case where it does; there is none.
    undeclared_arithmetic = any(f["code"] == "S8_UNDECLARED_ARITHMETIC" for f in findings.items())
    if findings.refusals():
        verdict = "REFUSED"
    elif findings.escapes() or undeclared_arithmetic:
        verdict = "CHECKED"
    else:
        verdict = "CHECKED_ANCHORED"

    return {
        "lexspec": SCHEMA_VERSION,
        "statement_id": statement.id,
        "statement_path": _display_path(path, root),
        "statement_sha256": canonical_hash if canonical_ok else None,
        "verdict": verdict,
        "coverage": coverage,
        "coverage_threshold": threshold,
        "coverage_threshold_role": "reporting-only (ADR-0010)",
        "root_source": root_source,
        "atoms": {
            "total": total,
            "closed": closed,
            "anchored": sum(1 for value in anchored.values() if value),
        },
        "corpus": [
            {
                "id": cid,
                "text": _display_path(root / str(entry.get("text", "")), root),
                "text_sha256": entry.get("text_sha256"),
                "revision": entry.get("revision"),
                "usable": loaded.get("usable", False) if isinstance(loaded, dict) else False,
            }
            for cid, entry in statement.corpus.items()
            for loaded in [corpora.get(cid, {})]
        ],
        "quantities": quantities,
        "position_status": position_status,
        "findings": findings.ordered(atom_order),
        "checks": _check_statuses(findings),
        "not_claimed": list(NOT_CLAIMED),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _render_human(report: dict) -> str:
    """Human output. Ordered so that a verdict cannot be quoted without its scope."""
    lines = []
    statement_id = report["statement_id"] if report["statement_id"] is not None else "(no id)"
    lines.append(f"statement        {statement_id}")
    lines.append(f"file             {report['statement_path']}")
    digest = report["statement_sha256"] or "(none: canonical form failed)"
    lines.append(f"statement_sha256 {digest}")
    lines.append(f"verdict          {report['verdict']}")
    atoms = report["atoms"]
    lines.append(
        f"coverage         {report['coverage']:.3f} of atoms closed "
        f"(threshold {report['coverage_threshold']:.3f}; "
        f"{atoms['closed']}/{atoms['total']} closed, {atoms['anchored']}/{atoms['total']} anchored)"
    )

    findings = report["findings"]
    if findings:
        refusals = sum(1 for f in findings if f["code"] in REFUSAL_CODES)
        escapes = len(findings) - refusals
        lines.append(f"findings         {len(findings)} ({refusals} refusal(s), {escapes} escape(s))")
        for finding in findings:
            severity = "REFUSED" if finding["code"] in REFUSAL_CODES else "escape"
            atom = finding["atom"] or "-"
            lines.append(f"  {severity:<8} {finding['code']:<24} {atom:<6} {finding['detail']}")
    else:
        lines.append("findings         none")
    lines.append("not_claimed      " + "; ".join(report["not_claimed"]))
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lexcheck",
        description="Check one LexSpec v0.1 statement. Exit 0 pass, 1 REFUSED, 2 usage or parse error.",
    )
    parser.add_argument(
        "statement",
        nargs="+",
        help="one or more *.lex.json statements; with several files the --json report is an array",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit the machine-readable report")
    parser.add_argument(
        "--coverage-threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        metavar="F",
        help=f"coverage floor for CHECKED_ANCHORED (default {DEFAULT_THRESHOLD}); report it with the verdict",
    )
    parser.add_argument(
        "--canonical",
        action="store_true",
        help="print the canonical form and sha256 instead of checking",
    )
    parser.add_argument(
        "--root",
        default=None,
        metavar="DIR",
        help="repository root for corpus paths (default: walk up to .git or docs/10-SPEC-v0.1.md)",
    )
    return parser


def _force_utf8_stdio() -> None:
    """Print UTF-8 regardless of the console code page.

    On a non-UTF-8 stdout (cp1251/cp1252 on Windows, and the default for redirected stdout on an en-US host) every
    report with Cyrillic in it died with UnicodeEncodeError, printed nothing, and exited 1 - the same code REFUSED
    uses. A crash and a refusal must not be the same signal.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="strict")
        except (AttributeError, ValueError):  # pragma: no cover - exotic stream
            pass


class OutputFailure(Exception):
    """Raised when a report cannot be written; carries exit code 3, never 1."""


def _emit(text: str, stream=None) -> None:
    stream = stream or sys.stdout
    try:
        stream.write(text)
        if not text.endswith("\n"):
            stream.write("\n")
    except UnicodeEncodeError as exc:
        raise OutputFailure(f"cannot write UTF-8 to stdout: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    """Exit codes: 0 passed, 1 refused, 2 usage, **3 could not write the report**.

    Code 3 exists because a crash and a refusal must never be the same signal: a pipeline that treats 1
    as "the statement was refused" would read a broken pipe as a legal finding.
    """
    try:
        return _main_body(argv)
    except OutputFailure as failure:
        try:
            sys.stderr.write(f"lexcheck: {failure}\n")
        except Exception:  # noqa: BLE001 - nothing left to report with
            pass
        return 3


def _main_body(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.as_json and args.canonical:
        print("lexcheck: error: --json and --canonical are mutually exclusive", file=sys.stderr)
        return 2
    if not (0.0 <= args.coverage_threshold <= 1.0):
        print("lexcheck: error: --coverage-threshold must be between 0.0 and 1.0", file=sys.stderr)
        return 2
    _force_utf8_stdio()

    paths = [Path(value) for value in args.statement]
    for path in paths:
        if not path.is_file():
            print(f"lexcheck: error: no such file: {path}", file=sys.stderr)
            return 2
    if args.canonical and len(paths) != 1:
        # A digest is per document; printing several would produce output that no
        # signature tool can consume without splitting it first.
        print("lexcheck: error: --canonical takes exactly one statement", file=sys.stderr)
        return 2

    root = Path(args.root) if args.root else None

    if args.canonical:
        # Canonical mode validates nothing but reproducibility: it is the tool a
        # signature is computed with, not the tool that judges.
        path = paths[0]
        try:
            raw, document = read_statement(path)
            text = canonical_text(document)
        except ParseError as exc:
            print(f"lexcheck: error: {exc}", file=sys.stderr)
            return 2
        except CanonError as exc:
            print(f"lexcheck: error: {exc}", file=sys.stderr)
            return 1
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        _emit(text)
        _emit(f"sha256 {digest}")
        for flag in _canonical_flags(raw):
            print(f"lexcheck: warning: {flag}", file=sys.stderr)
        return 0

    reports = []
    for path in paths:
        try:
            reports.append(analyze_file(path, args.coverage_threshold, root))
        except ParseError as exc:
            print(f"lexcheck: error: {exc}", file=sys.stderr)
            if args.as_json:
                _emit(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
            return 2
        except OSError as exc:
            print(f"lexcheck: error: {exc}", file=sys.stderr)
            return 2

    if args.as_json:
        # One file keeps the documented single-object report; several files are
        # printed as an array so that examples/*.lex.json works as one command.
        payload = reports[0] if len(reports) == 1 else reports
        _emit(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(_render_human(report) for report in reports))

    refused = any(report["verdict"] == "REFUSED" for report in reports)
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
