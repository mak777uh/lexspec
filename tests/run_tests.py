#!/usr/bin/env python3
"""run_tests — the machine's own argument that it works.

Standard library only, no test framework to install: `python tests/run_tests.py`.
Every assertion here is about observable behaviour of the CLI (exit code, report
fields, codes) rather than about internal functions, because the contract in
docs/10-SPEC-v0.1.md is a contract about what the tool says, not about how it is
built.

Two habits worth keeping when adding tests here:

  * Fixtures are built as dicts and written to a temporary directory, not checked
    in as files. A checked-in broken statement drifts (the corpus gets re-pinned,
    the fixture silently stops testing what its name says); a fixture built by a
    test is regenerated from the current corpus every run.
  * Numbers used in assertions are computed, never typed: the corpus digest is
    hashed from the file, the expected coverage is derived from atom counts by
    the test itself. A typed hash is a stale hash waiting to happen.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "lexcheck.py"
CHECK_EXAMPLES = ROOT / "tools" / "check_examples.py"
STATUS = ROOT / "tools" / "lexspec_status.py"
SECRETS = ROOT / "lab" / "check-secrets.py"
CORPUS_TEXT = "corpus/gk-rf-2026-10-01.txt"
EXPECTED = ROOT / "tests" / "expected.json"

SPAN_OK = "обязуется передать в обусловленный срок или сроки"
SPAN_OK_2 = "товары покупателю для использования в предпринимательской деятельности"
SPAN_AMBIGUOUS = "в соответствии с"  # occurs twice in the pinned excerpt
SPAN_ABSENT = "обязуется возместить убытки покупателя в полном объёме"

NOT_CLAIMED = [
    "legal validity",
    "completeness of the encoded law",
    "correctness of the corpus outside the pinned revision",
    # Added after the audit of 2026-10-29: a reader of one JSON report must not have to read the README to learn
    # that these four things are declared rather than checked.
    "anchor.article and corpus[].revision are declared, not verified",
    "conditions[] is prose and is not interpreted",
    "cross-tuple correlative agreement is not checked (the spec does not define its orientation)",
    "the normalisation policy is fixed by this tool, not declared per statement",
    "usefulness - no person or organisation outside this repository has used a verdict in a decision",
]


# --- helpers ---------------------------------------------------------------


def load_checker():
    """Import tools/lexcheck.py by path (tools/ is deliberately not a package)."""
    spec = importlib.util.spec_from_file_location("lexcheck_for_tests", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def corpus_digest() -> str:
    return hashlib.sha256((ROOT / CORPUS_TEXT).read_bytes()).hexdigest()


def run_tool(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def run_check(statement_path: Path, *extra: str, threshold: float | None = 0.8) -> tuple[int, dict | None, str]:
    args = [str(TOOL), str(statement_path), "--json", "--root", str(ROOT)]
    if threshold is not None:
        args += ["--coverage-threshold", str(threshold)]
    args += list(extra)
    completed = run_tool(*args)
    report = None
    if completed.stdout.strip():
        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError:
            report = None
    return completed.returncode, report, completed.stdout


def base_statement() -> dict:
    """One atom, fully closed and anchored: the shape every fixture starts from."""
    return {
        "lexspec": "0.1",
        "id": "fixture",
        "kind": "clause",
        "jurisdiction": ["RU"],
        "corpus": [
            {
                "id": "gk-rf",
                "title": "pinned excerpt",
                "revision": "2026-10-01",
                "text": CORPUS_TEXT,
                "text_sha256": corpus_digest(),
            }
        ],
        "terms": [
            {"name": "поставщик", "def": "d", "status": "closed"},
            {"name": "покупатель", "def": "d", "status": "closed"},
            {"name": "товары", "def": "d", "status": "closed"},
        ],
        "atoms": [
            {
                "id": "a1",
                "relation": "duty",
                "bearer": "поставщик",
                "counterparty": "покупатель",
                "action": {"verb": "передать", "object": "товары", "open": False},
                "conditions": [],
                "temporal": {"from": "2026-01-01", "until": None},
                "anchor": {"corpus": "gk-rf", "article": "ст. 506", "span": SPAN_OK},
            }
        ],
        "conflicts_policy": {"default": "report", "lex_specialis": []},
        "escapes": [],
    }


class FixtureCase(unittest.TestCase):
    """Shared plumbing: write a statement to a temp dir, run the CLI on it."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def check(self, document: dict, *extra: str, threshold: float | None = 0.8):
        path = self.tmp / "statement.lex.json"
        # write_bytes, not write_text: write_text would translate \n to CRLF on
        # Windows and every fixture would be refused by C0 for the wrong reason.
        path.write_bytes(json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8"))
        return run_check(path, *extra, threshold=threshold)

    def codes(self, report: dict) -> list[str]:
        return sorted({finding["code"] for finding in report["findings"]})

    def assert_codes(self, report: dict, expected: set[str]) -> None:
        self.assertEqual(sorted(expected), self.codes(report), msg=json.dumps(report["findings"], ensure_ascii=False, indent=2))


# --- canonical form --------------------------------------------------------


class CanonicalForm(FixtureCase):
    def test_canonical_hash_is_identical_across_two_runs(self):
        first = run_tool(str(TOOL), "examples/01-delivery-ok.lex.json", "--canonical")
        second = run_tool(str(TOOL), "examples/01-delivery-ok.lex.json", "--canonical")
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertRegex(first.stdout, r"\nsha256 [0-9a-f]{64}\n$")

    def test_canonical_form_is_a_fixed_point(self):
        """Re-canonicalising the canonical bytes must not change them."""
        first = run_tool(str(TOOL), "examples/01-delivery-ok.lex.json", "--canonical")
        text, digest_line = first.stdout.rsplit("\nsha256 ", 1)
        digest = digest_line.strip()
        checker = load_checker()
        reparsed = json.loads(text)
        self.assertEqual(digest, checker.canonical_sha256(reparsed))
        # And through the CLI again, from a file holding exactly those bytes.
        canonical_file = self.tmp / "canonical.lex.json"
        canonical_file.write_bytes(text.encode("utf-8"))
        again = run_tool(str(TOOL), str(canonical_file), "--canonical")
        self.assertEqual(0, again.returncode, again.stderr)
        self.assertTrue(again.stdout.rstrip().endswith(digest))

    def test_report_hash_equals_canonical_hash(self):
        canonical = run_tool(str(TOOL), "examples/01-delivery-ok.lex.json", "--canonical")
        digest = canonical.stdout.rstrip().rsplit("sha256 ", 1)[1]
        _code, report, _out = run_check(ROOT / "examples/01-delivery-ok.lex.json")
        self.assertEqual(digest, report["statement_sha256"])

    def test_float_makes_canonical_form_impossible(self):
        document = base_statement()
        document["confidence"] = 0.5  # unknown fields are allowed (§2), floats are not (§3.3)
        code, report, _out = self.check(document, threshold=0.0)
        self.assertEqual(1, code)
        self.assert_codes(report, {"C0_CANON"})
        self.assertIsNone(report["statement_sha256"])
        self.assertEqual("REFUSED", report["verdict"])

    def test_bom_is_c0(self):
        document = base_statement()
        payload = b"\xef\xbb\xbf" + json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8")
        path = self.tmp / "bom.lex.json"
        path.write_bytes(payload)
        code, report, _out = run_check(path, threshold=0.0)
        self.assertEqual(1, code)
        self.assertIn("C0_CANON", self.codes(report))

    def test_crlf_is_c0(self):
        document = base_statement()
        payload = json.dumps(document, ensure_ascii=False, indent=2).replace("\n", "\r\n").encode("utf-8")
        path = self.tmp / "crlf.lex.json"
        path.write_bytes(payload)
        code, report, _out = run_check(path, threshold=0.0)
        self.assertEqual(1, code)
        self.assertIn("C0_CANON", self.codes(report))

    def test_duplicate_object_key_is_a_parse_error(self):
        path = self.tmp / "dupes.lex.json"
        path.write_bytes(b'{"lexspec":"0.1","lexspec":"0.1"}')
        completed = run_tool(str(TOOL), str(path), "--json")
        self.assertEqual(2, completed.returncode)
        self.assertIn("duplicate object key", completed.stderr)

    def test_malformed_json_exits_2(self):
        path = self.tmp / "broken.lex.json"
        path.write_bytes(b"{not json")
        code, _report, _out = run_check(path)
        self.assertEqual(2, code)

    def test_nan_constant_exits_2(self):
        path = self.tmp / "nan.lex.json"
        path.write_bytes(b'{"lexspec":"0.1","x":NaN}')
        code, _report, _out = run_check(path)
        self.assertEqual(2, code)

    def test_missing_file_exits_2(self):
        code, _report, _out = run_check(self.tmp / "absent.lex.json")
        self.assertEqual(2, code)

    def test_usage_errors_exit_2(self):
        self.assertEqual(2, run_tool(str(TOOL)).returncode)
        self.assertEqual(2, run_tool(str(TOOL), "examples/01-delivery-ok.lex.json", "--json", "--canonical").returncode)
        self.assertEqual(2, run_tool(str(TOOL), "examples/01-delivery-ok.lex.json", "--coverage-threshold", "1.5").returncode)


# --- the shipped examples --------------------------------------------------


class ExampleVerdicts(FixtureCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = json.loads(EXPECTED.read_text(encoding="utf-8"))["examples"]

    def test_there_are_at_least_three_examples(self):
        examples = sorted(p.name for p in (ROOT / "examples").glob("*.lex.json"))
        self.assertGreaterEqual(len(examples), 3, examples)

    def test_required_examples_are_present(self):
        names = {path.name for path in (ROOT / "examples").glob("*.lex.json")}
        for required in (
            "01-delivery-ok.lex.json",
            "02-opposite-conflict.lex.json",
            "03-no-anchor.lex.json",
        ):
            self.assertIn(required, names)

    def test_every_example_is_recorded_in_expected_json(self):
        names = {path.name for path in (ROOT / "examples").glob("*.lex.json")}
        self.assertEqual(names, set(self.expected))

    def test_examples_match_recorded_expectations(self):
        for name, want in sorted(self.expected.items()):
            with self.subTest(example=name):
                code, report, out = run_check(ROOT / "examples" / name)
                self.assertIsNotNone(report, out)
                self.assertEqual(want["exit_code"], code)
                self.assertEqual(want["verdict"], report["verdict"])
                self.assertEqual(want["coverage"], report["coverage"])
                self.assertEqual(sorted(want["codes"]), self.codes(report))
                self.assertEqual(NOT_CLAIMED, report["not_claimed"])

    def test_examples_pin_the_corpus_that_ships_with_them(self):
        # Each example is checked against the corpus it names, not against one global corpus:
        # the repository now ships two pinned texts (a Russian civil-code excerpt and a GDPR
        # article), and a test that assumes a single file would either miss a wrong digest or
        # force every future example onto the same source.
        for path in sorted((ROOT / "examples").glob("*.lex.json")):
            with self.subTest(example=path.name):
                document = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(document["corpus"], "an example without a pinned corpus proves nothing")
                for entry in document["corpus"]:
                    pinned = ROOT / entry["text"]
                    self.assertTrue(pinned.is_file(), f"{path.name} names a corpus file that does not exist")
                    actual = hashlib.sha256(pinned.read_bytes()).hexdigest()
                    self.assertEqual(actual, entry["text_sha256"],
                                     f"{path.name} declares a digest the corpus does not have")

    def test_report_shape_is_the_documented_one(self):
        _code, report, _out = run_check(ROOT / "examples" / "01-delivery-ok.lex.json")
        for field in ("statement_id", "statement_sha256", "verdict", "coverage", "findings", "not_claimed"):
            self.assertIn(field, report)
        self.assertIn(report["verdict"], {"REFUSED", "CHECKED", "CHECKED_ANCHORED"})
        self.assertEqual(round(report["coverage"], 3), report["coverage"])
        for finding in report["findings"]:
            self.assertEqual({"code", "atom", "detail"}, set(finding))
        self.assertNotIn(str(ROOT), json.dumps(report, ensure_ascii=False))

    def test_human_output_carries_verdict_coverage_and_scope(self):
        completed = run_tool(str(TOOL), "examples/06-thin-coverage.lex.json")
        self.assertEqual(0, completed.returncode)
        for needle in ("verdict", "CHECKED", "coverage", "0.667", "THIN_COVERAGE", "not_claimed", "legal validity"):
            self.assertIn(needle, completed.stdout)

    def test_two_runs_produce_identical_reports(self):
        first = run_tool(str(TOOL), "examples/05-open-term.lex.json", "--json")
        second = run_tool(str(TOOL), "examples/05-open-term.lex.json", "--json")
        self.assertEqual(first.stdout, second.stdout)

    def test_several_files_give_an_array_and_one_refusal_fails_the_run(self):
        """`examples/*.lex.json` is what a shell expands, so it has to work."""
        mixed = run_tool(
            str(TOOL),
            "examples/01-delivery-ok.lex.json",
            "examples/02-opposite-conflict.lex.json",
            "--json",
        )
        self.assertEqual(1, mixed.returncode)
        payload = json.loads(mixed.stdout)
        self.assertIsInstance(payload, list)
        self.assertEqual(2, len(payload))
        self.assertEqual(["CHECKED_ANCHORED", "REFUSED"], [item["verdict"] for item in payload])

        passing = run_tool(
            str(TOOL), "examples/01-delivery-ok.lex.json", "examples/05-open-term.lex.json", "--json"
        )
        self.assertEqual(0, passing.returncode)
        self.assertEqual(2, len(json.loads(passing.stdout)))

    def test_check_examples_tool_agrees(self):
        completed = run_tool(str(CHECK_EXAMPLES))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


# --- one fixture per refusal code -----------------------------------------


class RefusalCodes(FixtureCase):
    """Each test isolates one code. threshold=0 removes THIN_COVERAGE from the noise."""

    def test_unknown_relation(self):
        document = base_statement()
        document["atoms"][0]["relation"] = "claim"
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S3_UNKNOWN_RELATION"})
        self.assertEqual("REFUSED", report["verdict"])

    def test_missing_counterparty_for_a_relative_relation(self):
        document = base_statement()
        document["atoms"][0]["counterparty"] = None  # duty is relative (§4.3)
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S3_MISSING_COUNTERPARTY"})

    def test_absolute_relation_may_omit_counterparty(self):
        """§4.3: immunity/power/disability against the world are not defects."""
        document = base_statement()
        document["atoms"][0]["relation"] = "power"
        document["atoms"][0]["counterparty"] = None
        code, report, _out = self.check(document, threshold=0.0)
        self.assertEqual(0, code)
        self.assert_codes(report, set())
        self.assertEqual("CHECKED_ANCHORED", report["verdict"])

    def test_opposite_relations_on_one_tuple(self):
        document = base_statement()
        twin = json.loads(json.dumps(document["atoms"][0]))
        twin["id"] = "a2"
        twin["relation"] = "no-right"  # opposite of duty
        twin["anchor"]["span"] = SPAN_OK_2
        document["atoms"].append(twin)
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S3_OPPOSITE_CONFLICT"})

    def test_opposites_do_not_conflict_across_disjoint_intervals(self):
        document = base_statement()
        document["atoms"][0]["temporal"] = {"from": "2026-01-01", "until": "2026-06-01"}
        twin = json.loads(json.dumps(document["atoms"][0]))
        twin["id"] = "a2"
        twin["relation"] = "no-right"
        twin["anchor"]["span"] = SPAN_OK_2
        twin["temporal"] = {"from": "2026-07-01", "until": None}
        document["atoms"].append(twin)
        code, report, _out = self.check(document, threshold=0.0)
        self.assertEqual(0, code, json.dumps(report["findings"], ensure_ascii=False))
        self.assert_codes(report, set())

    def test_undefined_reference(self):
        document = base_statement()
        document["atoms"][0]["bearer"] = "перевозчик"  # not in terms[]
        document["escapes"] = [{"atom": "a1", "reason": "S4_UNDEFINED_REF", "detail": "declared"}]
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S4_UNDEFINED_REF", "OPEN_TERM"})

    def test_undeclared_escape(self):
        document = base_statement()
        document["terms"][0]["status"] = "open"
        document["escapes"] = []
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"OPEN_TERM", "S4_UNDECLARED_ESCAPE"})

    def test_stale_escape(self):
        document = base_statement()  # atom is closed, yet an escape is declared
        document["escapes"] = [{"atom": "a1", "reason": "OPEN_TERM", "detail": "stale"}]
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S4_STALE_ESCAPE"})

    def test_malformed_atom_counts_in_the_denominator(self):
        """§8: an atom S1 rejected cannot be closed, so it must lower coverage."""
        document = base_statement()
        del document["atoms"][0]["bearer"]
        code, report, _out = self.check(document, threshold=0.0)
        self.assertEqual(1, report["atoms"]["total"])
        self.assertEqual(0, report["atoms"]["closed"])
        self.assertEqual(0.0, report["coverage"])
        self.assertEqual(1, code)
        open_term = next(f["detail"] for f in report["findings"] if f["code"] == "OPEN_TERM")
        self.assertIn("bearer", open_term, "the OPEN_TERM detail must name the cause")
        self.assertIn("S4_UNDECLARED_ESCAPE", self.codes(report))

    def test_escape_accounting_checks_membership_not_the_wording_of_reason(self):
        document = base_statement()
        del document["atoms"][0]["bearer"]
        document["escapes"] = [
            {"atom": "a1", "reason": "OPEN_TERM", "detail": "prose that need not match the computed cause"}
        ]
        _code, report, _out = self.check(document, threshold=0.0)
        self.assertEqual(["OPEN_TERM", "S1_SCHEMA"], self.codes(report))

    def test_empty_interval(self):
        document = base_statement()
        document["atoms"][0]["temporal"] = {"from": "2026-06-01", "until": "2026-05-01"}
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S5_EMPTY_INTERVAL"})

    def test_span_not_found(self):
        document = base_statement()
        document["atoms"][0]["anchor"]["span"] = SPAN_ABSENT
        document["escapes"] = [{"atom": "a1", "reason": "S2_SPAN_NOT_FOUND", "detail": "declared"}]
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S2_SPAN_NOT_FOUND", "OPEN_TERM"})

    def test_span_ambiguous(self):
        document = base_statement()
        document["atoms"][0]["anchor"]["span"] = SPAN_AMBIGUOUS
        document["escapes"] = [{"atom": "a1", "reason": "S2_SPAN_AMBIGUOUS", "detail": "declared"}]
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S2_SPAN_AMBIGUOUS", "OPEN_TERM"})

    def test_corpus_handle_that_names_nothing(self):
        document = base_statement()
        document["atoms"][0]["anchor"]["corpus"] = "gk-rf-1994"
        document["escapes"] = [{"atom": "a1", "reason": "S2_NO_CORPUS", "detail": "declared"}]
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S2_NO_CORPUS", "OPEN_TERM"})

    def test_corpus_path_outside_the_repository_is_refused(self):
        document = base_statement()
        document["corpus"][0]["text"] = "../outside.txt"
        _code, report, _out = self.check(document, threshold=0.0)
        self.assertIn("S1_SCHEMA", self.codes(report))

    def test_corpus_file_missing_is_its_own_code_not_a_hash_mismatch(self):
        """F-3-1: blaming the corpus for a resolution failure was a misdiagnosis."""
        document = base_statement()
        document["corpus"][0]["text"] = "corpus/does-not-exist.txt"
        document["escapes"] = [{"atom": "a1", "reason": "S2_CORPUS_NOT_FOUND", "detail": "declared"}]
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S2_CORPUS_NOT_FOUND", "OPEN_TERM"})
        self.assertNotIn("S2_HASH_MISMATCH", self.codes(report))
        detail = next(f["detail"] for f in report["findings"] if f["code"] == "S2_CORPUS_NOT_FOUND")
        self.assertIn("never compared", detail)

    def test_a_portable_tree_without_a_repository_marker_still_checks(self):
        """F-3-1 regression: the same bytes must yield the same verdict outside a repository."""
        statement = json.loads((ROOT / "examples" / "01-delivery-ok.lex.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "corpus").mkdir()
            for entry in statement["corpus"]:
                src = ROOT / entry["text"]
                (tmp_path / entry["text"]).write_bytes(src.read_bytes())
            (tmp_path / "examples").mkdir()
            target = tmp_path / "examples" / "portable.lex.json"
            target.write_text(json.dumps(statement, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
            # deliberately no --root: the point is the fallback, not an imposed base
            proc = subprocess.run([sys.executable, str(TOOL), str(target), "--json"], capture_output=True, text=True, encoding="utf-8")
            report = json.loads(proc.stdout)
            code = proc.returncode
        self.assertEqual(0, code, report)
        self.assertEqual("CHECKED_ANCHORED", report["verdict"], report)
        self.assertEqual(1.0, report["coverage"])
        self.assertEqual("statement", report["root_source"], "the fallback must be named in the report")

    def test_truncated_corpus_copy_triggers_hash_mismatch(self):
        """The pin is by content: a copy that was edited must not anchor anything."""
        tree = self.tmp / "tree"
        (tree / "corpus").mkdir(parents=True)
        original = (ROOT / CORPUS_TEXT).read_bytes()
        (tree / "corpus" / "gk-rf-2026-10-01.txt").write_bytes(original[:-40])
        document = base_statement()
        document["escapes"] = [{"atom": "a1", "reason": "S2_HASH_MISMATCH", "detail": "declared"}]
        statement = tree / "statement.lex.json"
        statement.write_bytes(json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8"))
        completed = run_tool(str(TOOL), str(statement), "--json", "--root", str(tree),
                             "--coverage-threshold", "0")
        report = json.loads(completed.stdout)
        self.assertEqual(1, completed.returncode)
        self.assert_codes(report, {"S2_HASH_MISMATCH", "OPEN_TERM"})
        self.assertEqual(0, report["atoms"]["anchored"])

    def test_conflict_under_report_policy(self):
        document = base_statement()
        twin = json.loads(json.dumps(document["atoms"][0]))
        twin["id"] = "a2"
        twin["relation"] = "right"  # correlative of duty on the same ordered pair
        twin["anchor"]["span"] = SPAN_OK_2
        document["atoms"].append(twin)
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S6_CONFLICT"})

    def test_conflict_unresolved_under_lex_specialis(self):
        document = base_statement()
        twin = json.loads(json.dumps(document["atoms"][0]))
        twin["id"] = "a2"
        twin["relation"] = "right"
        twin["anchor"]["span"] = SPAN_OK_2
        document["atoms"].append(twin)
        document["conflicts_policy"] = {"default": "lex_specialis", "lex_specialis": []}
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S6_UNRESOLVED_CONFLICT"})

    def test_conflict_resolved_by_naming_the_prevailing_atom(self):
        document = base_statement()
        twin = json.loads(json.dumps(document["atoms"][0]))
        twin["id"] = "a2"
        twin["relation"] = "right"
        twin["anchor"]["span"] = SPAN_OK_2
        document["atoms"].append(twin)
        document["conflicts_policy"] = {
            "default": "lex_specialis",
            "lex_specialis": [{"prevailing": "a1", "over": ["a2"], "reason": "specific provision"}],
        }
        code, report, _out = self.check(document, threshold=0.0)
        self.assertEqual(0, code, json.dumps(report["findings"], ensure_ascii=False))
        self.assert_codes(report, set())


# --- coverage arithmetic and the verdict ladder ----------------------------


class CoverageAndVerdicts(FixtureCase):
    def _three_atoms_one_open(self) -> dict:
        document = base_statement()
        second = json.loads(json.dumps(document["atoms"][0]))
        second["id"] = "a2"
        second["relation"] = "right"
        second["bearer"] = "покупатель"
        second["counterparty"] = "поставщик"
        second["anchor"]["span"] = SPAN_OK_2
        third = json.loads(json.dumps(document["atoms"][0]))
        third["id"] = "a3"
        third["action"] = {"verb": "исполнить", "object": "товары", "open": True}
        third["anchor"]["span"] = "Обязательства должны исполняться надлежащим образом"
        document["atoms"] = [document["atoms"][0], second, third]
        document["escapes"] = [{"atom": "a3", "reason": "OPEN_TERM", "detail": "action is open"}]
        return document

    def test_coverage_arithmetic_on_three_atoms(self):
        document = self._three_atoms_one_open()
        code, report, _out = self.check(document)
        self.assertEqual(3, report["atoms"]["total"])
        # 2 of 3 closed -> 0.666..., rounded to three decimals by the report.
        self.assertEqual(round(2 / 3, 3), report["coverage"])
        self.assertEqual(2, report["atoms"]["closed"])
        self.assertEqual(3, report["atoms"]["anchored"])
        self.assertEqual(0, code)
        self.assertEqual("CHECKED", report["verdict"])
        self.assertEqual(["OPEN_TERM", "THIN_COVERAGE"], self.codes(report))

    def test_coverage_is_unchanged_by_the_threshold_but_thin_is(self):
        document = self._three_atoms_one_open()
        _code, report_low, _out = self.check(document, threshold=0.5)
        self.assertEqual(round(2 / 3, 3), report_low["coverage"])
        self.assertEqual(["OPEN_TERM"], self.codes(report_low))  # no THIN at 0.5
        self.assertEqual("CHECKED", report_low["verdict"])  # the escape alone is enough

    def test_no_atoms_is_zero_coverage_and_never_a_pass(self):
        document = base_statement()
        document["atoms"] = []
        code, report, _out = self.check(document)
        self.assertEqual(0, report["coverage"])
        self.assertEqual(["THIN_COVERAGE"], self.codes(report))
        self.assertEqual("CHECKED", report["verdict"])
        self.assertEqual(0, code)

    def test_full_coverage_without_escapes_is_anchored(self):
        code, report, _out = self.check(base_statement())
        self.assertEqual(1.0, report["coverage"])
        self.assertEqual([], report["findings"])
        self.assertEqual("CHECKED_ANCHORED", report["verdict"])
        self.assertEqual(0, code)

    def test_stdout_json_and_exit_code_disagree_only_on_refusal(self):
        code, report, _out = self.check(base_statement())
        self.assertEqual(0, code)
        self.assertEqual("CHECKED_ANCHORED", report["verdict"])
        broken = base_statement()
        broken["atoms"][0]["relation"] = "nonsense"
        code, report, _out = self.check(broken)
        self.assertEqual(1, code)
        self.assertEqual("REFUSED", report["verdict"])


# --- the prose schema and the executable one -------------------------------


class SchemaAlignment(FixtureCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas" / "statement-0.1.json").read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_schema_declares_draft_2020_12(self):
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", self.schema["$schema"])

    def test_required_fields_match_the_validator(self):
        self.assertEqual(list(self.checker.REQUIRED_TOP), self.schema["required"])

    def test_relation_enum_matches_the_square(self):
        relation = self.schema["$defs"]["relation"]["enum"]
        self.assertEqual(list(self.checker.RELATIONS), relation)
        self.assertEqual(8, len(relation))

    def test_other_enums_match(self):
        self.assertEqual(list(self.checker.KINDS), self.schema["properties"]["kind"]["enum"])
        self.assertEqual(list(self.checker.TERM_STATUS), self.schema["$defs"]["term"]["properties"]["status"]["enum"])
        self.assertEqual(list(self.checker.POLICIES), self.schema["properties"]["conflicts_policy"]["properties"]["default"]["enum"])
        self.assertEqual(sorted(self.checker.ALL_CODES), sorted(self.schema["$defs"]["refusalCode"]["enum"]))

    def test_code_catalogue_is_closed_and_grouped(self):
        """A code added to the catalogue but not to a group would vanish from reports."""
        self.assertEqual(len(self.checker.CODE_ORDER), len(set(self.checker.CODE_ORDER)))
        self.assertEqual(set(self.checker.CODE_ORDER), self.checker.ALL_CODES)
        self.assertEqual(set(self.checker.CODE_CHECK), self.checker.ALL_CODES)
        self.assertEqual(self.checker.ALL_CODES - self.checker.ESCAPE_CODES, self.checker.REFUSAL_CODES)
        # two escapes plus one ceiling: S8_UNDECLARED_ARITHMETIC caps the verdict instead of refusing
        self.assertEqual(3, len(self.checker.ESCAPE_CODES))
        self.assertIn("S8_UNDECLARED_ARITHMETIC", self.checker.ESCAPE_CODES)

    def test_atom_keys_required_by_the_schema_are_required_by_the_checker(self):
        atom_required = self.schema["$defs"]["atom"]["required"]
        for key in atom_required:
            with self.subTest(missing=key):
                document = base_statement()
                del document["atoms"][0][key]
                _code, report, _out = self.check(document, threshold=0.0)
                self.assertIn("S1_SCHEMA", self.codes(report), f"removing atoms[0].{key} was not refused")

    def test_top_level_keys_required_by_the_schema_are_required_by_the_checker(self):
        for key in self.schema["required"]:
            with self.subTest(missing=key):
                document = base_statement()
                del document[key]
                _code, report, _out = self.check(document, threshold=0.0)
                self.assertIn("S1_SCHEMA", self.codes(report), f"removing {key} was not refused")

    def test_unknown_fields_are_ignored(self):
        """§2 is explicit: unknown fields are allowed and a checker must not fail on them."""
        document = base_statement()
        document["future_field"] = {"anything": ["at", "all"]}
        document["atoms"][0]["future_field"] = True
        code, report, _out = self.check(document)
        self.assertEqual(0, code)
        self.assertEqual("CHECKED_ANCHORED", report["verdict"])
        self.assertEqual([], report["findings"])


# --- guards and status -----------------------------------------------------


class Guards(FixtureCase):
    def test_repository_is_clean_of_secrets(self):
        completed = run_tool(str(SECRETS))
        self.assertEqual(0, completed.returncode, completed.stdout)

    def test_planted_token_is_reported_with_file_and_line(self):
        tree = self.tmp / "tree"
        tree.mkdir()
        # Assembled at runtime so this test file does not match its own pattern.
        token = "gh" + "p_" + "A1b2C3d4E5f6G7h8I9j0K1l2"
        (tree / "leak.txt").write_text("line one\nline two " + token + "\n", encoding="utf-8")
        completed = run_tool(str(SECRETS), "--root", str(tree))
        self.assertEqual(1, completed.returncode)
        self.assertIn("leak.txt:2:", completed.stdout)

    def test_absolute_windows_path_is_reported(self):
        tree = self.tmp / "tree"
        tree.mkdir()
        machine_path = "C" + ":" + chr(92) + "Users" + chr(92) + "someone"
        (tree / "note.md").write_text("see " + machine_path + "\n", encoding="utf-8")
        completed = run_tool(str(SECRETS), "--root", str(tree))
        self.assertEqual(1, completed.returncode)
        self.assertIn("absolute Windows path", completed.stdout)

    def test_sha256_with_context_is_not_a_secret(self):
        tree = self.tmp / "tree"
        tree.mkdir()
        digest = "ab" * 32
        # Both spellings the repository actually uses: a bare "\bsha256\b" test
        # would exempt neither "text_sha256" nor "statement_sha256".
        (tree / "pinned.json").write_text(
            '"text_sha256": "' + digest + '"\n"statement_sha256": "' + digest + '"\n',
            encoding="utf-8",
        )
        completed = run_tool(str(SECRETS), "--root", str(tree))
        self.assertEqual(0, completed.returncode, completed.stdout)

    def test_bare_64_hex_without_context_is_a_finding(self):
        tree = self.tmp / "tree"
        tree.mkdir()
        digest = "cd" * 32
        (tree / "key.txt").write_text(digest + "\n", encoding="utf-8")
        completed = run_tool(str(SECRETS), "--root", str(tree))
        self.assertEqual(1, completed.returncode)

    def test_status_block_is_stable_and_relative(self):
        first = run_tool(str(STATUS))
        second = run_tool(str(STATUS))
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        stripped = first.stdout
        self.assertNotIn(str(ROOT), stripped)
        self.assertIn("examples:", stripped)
        self.assertIn("digests match declarations: yes", stripped)
        self.assertIn("python tools/lexcheck.py", stripped)


# --- L5 quantities (docs/27) ------------------------------------------------


class QuantityLayer(FixtureCase):
    """The number layer: pinning, segmentation, and the ceiling that keeps an undeclared convention honest."""

    def load(self) -> dict:
        return json.loads((ROOT / "examples" / "10-gk-rf-395-quantified.lex.json").read_text(encoding="utf-8"))

    def test_the_quantified_statement_closes_the_rate_atom(self):
        code, report, _out = self.check(self.load())
        self.assertEqual(0.667, report["coverage"], "the rate atom closes; the defeat and the bounded power stay open")
        self.assertEqual("CHECKED", report["verdict"])
        self.assertEqual(["OPEN_TERM", "THIN_COVERAGE"], self.codes(report))

    def test_segmentation_reproduces_the_judgment_day_count(self):
        _code, report, _out = self.check(self.load())
        q1 = report["quantities"]["q1"]
        self.assertEqual(23, len(q1["segments"]), "rate changes, payments and the leap-year cut")
        self.assertEqual(1296, sum(s["days"] for s in q1["segments"]), "the act prints 1296 days in total")
        self.assertEqual(77, q1["segments"][0]["days"], "the act prints 77 days for the first row")
        self.assertEqual("2017-03-26", q1["segments"][0]["to"], "a segment ends the day before the next rate")

    def test_an_unpinned_series_is_refused(self):
        document = self.load()
        document["series"][0]["digest"] = "0" * 64
        _code, report, _out = self.check(document)
        self.assertIn("S8_SERIES_NOT_PINNED", self.codes(report))
        self.assertIn("S8_UNANCHORED_QUANTITY", self.codes(report))

    def test_undeclared_arithmetic_caps_the_verdict(self):
        document = self.load()
        document["quantities"][0]["period"]["day_count"] = "undeclared"
        _code, report, _out = self.check(document)
        self.assertIn("S8_UNDECLARED_ARITHMETIC", self.codes(report))
        self.assertEqual("CHECKED", report["verdict"], "an undeclared convention can never reach CHECKED_ANCHORED")

    def test_the_total_reproduces_the_judgment(self):
        """The whole point: our integer arithmetic must land on the figure the court awarded."""
        _code, report, _out = self.check(self.load())
        q1 = report["quantities"]["q1"]
        self.assertEqual(23, len(q1["segments"]), "the act prints 23 rows")
        self.assertEqual(20731362, q1["total_minor"], "207 313,62 roubles, in kopecks")

    def test_a_payment_reduces_the_base_from_the_next_day(self):
        _code, report, _out = self.check(self.load())
        by_date = {s["from"]: s for s in report["quantities"]["q1"]["segments"]}
        self.assertEqual(128110558, by_date["2018-03-26"]["base_minor"], "full principal before the payment")
        self.assertEqual(78110558, by_date["2018-07-28"]["base_minor"], "reduced from the day after 27.07.2018")
        self.assertEqual(28110558, by_date["2018-08-01"]["base_minor"], "reduced again after 31.07.2018")

    def test_the_year_is_cut_only_where_its_length_changes(self):
        _code, report, _out = self.check(self.load())
        starts = [s["from"] for s in report["quantities"]["q1"]["segments"]]
        self.assertIn("2020-01-01", starts, "366 begins here, and the act cuts here")
        self.assertNotIn("2018-01-01", starts, "365 to 365 is not a cut, and the act does not cut there")
        self.assertNotIn("2019-01-01", starts, "same reason")

    def test_a_period_outside_the_pin_is_a_segment_gap(self):
        document = self.load()
        document["quantities"][0]["period"]["from"] = "2016-01-01"
        _code, report, _out = self.check(document)
        self.assertIn("S8_SEGMENT_GAP", self.codes(report))

# --- L2b defeat (docs/13) ---------------------------------------------------


class DefeatLayer(FixtureCase):
    """Defeat records a relation and a declared applicability; it never computes which exception applies."""

    def load(self) -> dict:
        return json.loads((ROOT / "examples" / "11-gk-rf-395-defeat.lex.json").read_text(encoding="utf-8"))

    def test_the_defeated_position_is_refuted_and_the_defeater_stands(self):
        _code, report, _out = self.check(self.load())
        self.assertEqual("refuted", report["position_status"]["a1"], "a4 excepts a1, and a4 applies")
        self.assertEqual("established", report["position_status"]["a4"])
        self.assertEqual(0.833, report["coverage"], "both a1 and a4 are encoded now; only a6 stays open")

    def test_an_open_atom_can_never_be_reported_as_established(self):
        _code, report, _out = self.check(self.load())
        self.assertEqual("neither", report["position_status"]["a6"], "a6 is open, so the report cannot say it holds")

    def test_an_undefined_defeater_is_refused(self):
        document = self.load()
        for atom in document["atoms"]:
            if atom["id"] == "a4":
                atom["excepts"] = ["a99"]
        _code, report, _out = self.check(document)
        self.assertIn("S9_DEFEAT_UNDEFINED", self.codes(report))

    def test_a_cycle_between_two_atoms_is_refused(self):
        document = self.load()
        for atom in document["atoms"]:
            if atom["id"] == "a1":
                atom["excepts"] = ["a4"]
                atom["applies"] = True
        _code, report, _out = self.check(document)
        self.assertIn("S9_DEFEAT_CYCLE", self.codes(report))

    def test_silence_is_not_negation(self):
        """D4: if the defeater's applicability is not asserted, the report says neither and the checker refuses."""
        document = self.load()
        for atom in document["atoms"]:
            if atom["id"] == "a4":
                atom.pop("applies", None)
        _code, report, _out = self.check(document)
        self.assertIn("S9_APPLICABILITY_UNSTATED", self.codes(report))
        self.assertEqual("neither", report["position_status"]["a1"])


class SuiteShape(FixtureCase):
    """The suite's shape is part of its meaning: two classes with one name hid three arithmetic tests."""

    def test_no_test_class_is_defined_twice(self):
        source = (ROOT / "tests" / "run_tests.py").read_text(encoding="utf-8")
        names = re.findall(r"^class (\w+)\(", source, re.M)
        duplicates = {n for n in names if names.count(n) > 1}
        self.assertEqual(set(), duplicates, "a second definition shadows the first when the module is imported")

    def test_the_runner_block_is_last(self):
        source = (ROOT / "tests" / "run_tests.py").read_text(encoding="utf-8")
        # line-anchored: the test file contains the literal text of a runner block inside its own source strings,
        # and a plain .index() finds that one instead of the real block
        match = re.search(r"^if __name__ == ['\"]__main__['\"]:", source, re.M)
        self.assertIsNotNone(match, "no top-level runner block")
        self.assertNotIn("\nclass ", source[match.start():], "code after unittest.main() is dead when run as a script")


class OutputContract(FixtureCase):
    """A crash while printing must not share exit code 1 with a refusal."""

    def test_an_unwritable_stream_raises_output_failure(self):
        spec = __import__("importlib.util", fromlist=["util"]).spec_from_file_location("lexcheck", ROOT / "tools" / "lexcheck.py")
        module = __import__("importlib.util", fromlist=["util"]).module_from_spec(spec)
        spec.loader.exec_module(module)

        class Bad:
            def write(self, _text):
                raise UnicodeEncodeError("ascii", "", 0, 1, "no")

            def reconfigure(self, **_kwargs):
                pass

        with self.assertRaises(module.OutputFailure):
            module._emit("x", Bad())

    def test_the_documented_exit_code_is_three(self):
        source = (ROOT / "tools" / "lexcheck.py").read_text(encoding="utf-8")
        self.assertIn("except OutputFailure", source)
        self.assertRegex(source, r"return 3")


class TwinAgreement(FixtureCase):
    """Two implementations of the same arithmetic, written to disagree if either drifts (ADR-0002, docs/31 §3)."""

    def test_the_twin_agrees_with_the_checker_on_the_judgment(self):
        twin = ROOT / "tools" / "lexcheck_twin.py"
        proc = subprocess.run(
            [sys.executable, str(twin), str(ROOT / "examples" / "10-gk-rf-395-quantified.lex.json")],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("20731362", proc.stdout, "the twin must land on the figure the court awarded")

    def test_the_twin_uses_a_different_arithmetic_path(self):
        source = (ROOT / "tools" / "lexcheck_twin.py").read_text(encoding="utf-8")
        checker = (ROOT / "tools" / "lexcheck.py").read_text(encoding="utf-8")
        self.assertIn("divmod", source, "the twin rounds with integer division")
        self.assertIn("Decimal", checker, "the checker rounds with Decimal")
        self.assertNotIn("from decimal", source.lower(), "if the twin imported Decimal it would not be a second opinion")


class ReportPage(FixtureCase):
    """A reader-facing artefact that adds no dependency surface: one HTML file, no JavaScript, no CDN."""

    def test_the_page_carries_the_verdict_and_the_boundary(self):
        out = self.tmp / "report.html"
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "report_html.py"),
             str(ROOT / "examples" / "01-delivery-ok.lex.json"), "--out", str(out)],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        page = out.read_text(encoding="utf-8")
        self.assertIn("CHECKED_ANCHORED", page)
        self.assertIn("legal validity", page, "the not_claimed block must travel with the verdict")
        self.assertIn("usefulness", page)

    def test_the_page_loads_nothing_from_the_network(self):
        out = self.tmp / "report.html"
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "report_html.py"),
             str(ROOT / "examples" / "10-gk-rf-395-quantified.lex.json"), "--out", str(out)],
            capture_output=True, text=True, encoding="utf-8",
        )
        page = out.read_text(encoding="utf-8")
        self.assertNotIn("http://", page, "no external resource may be required to read a verdict")
        self.assertNotIn("https://", page)
        self.assertLess(len(page), 60_000, "a report page must stay small enough to email")
        self.assertIn("20731362", page, "the quantity total is part of the evidence, not a footnote")


if __name__ == "__main__":
    unittest.main(verbosity=2)
