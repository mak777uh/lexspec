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

    def test_corpus_file_missing_is_a_hash_mismatch(self):
        """No bytes means the pin cannot be verified, and the remedy is re-pinning."""
        document = base_statement()
        document["corpus"][0]["text"] = "corpus/does-not-exist.txt"
        document["escapes"] = [{"atom": "a1", "reason": "S2_HASH_MISMATCH", "detail": "declared"}]
        _code, report, _out = self.check(document, threshold=0.0)
        self.assert_codes(report, {"S2_HASH_MISMATCH", "OPEN_TERM"})

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
        self.assertEqual(2, len(self.checker.ESCAPE_CODES))

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
