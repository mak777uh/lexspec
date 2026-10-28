"""Tests for tools/span_hint.py — the tool that turns a human quote into byte-exact bytes.

Each test is a real failure we hit: a quote crossing a line break, a quote carrying an entity, a quote that is
genuinely repeated, and a quote from the wrong revision. Standard library only.

Run: python tests/run_span_tests.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "span_hint.py"

CORPUS = (
    "# SOURCE: test fixture\n"
    "1. Поставщик обязуется передать в обусловленный срок или\n"
    "сроки производимые или закупаемые им товары покупателю.\n"
    "2. Покупатель вправе требовать передачи товаров досрочно.\n"
    "3. Кавычки и сущности: &laquo;поставка&raquo;.\n"
    "4. 11111 zzzzz товары покупателю. qqqqq 22222\n"
    "5. 33333 zzzzz товары покупателю. qqqqq 44444\n"
)


def run(args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(TOOL), *args, "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"_stdout": proc.stdout, "_stderr": proc.stderr}
    return proc.returncode, payload


class SpanHint(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.corpus = Path(cls.tmp.name) / "corpus.txt"
        cls.corpus.write_text(CORPUS, encoding="utf-8", newline="")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_quote_crossing_a_line_break_is_recovered(self) -> None:
        """The dominant real failure: the sentence wraps, the paste does not."""
        quote = "Поставщик обязуется передать в обусловленный срок или сроки производимые"
        code, report = run(["--corpus", str(self.corpus), "--quote", quote])
        self.assertEqual(0, code, report)
        self.assertTrue(report["ok"])
        self.assertIn("срок или\nсроки", report["span"], "the span must contain the original line break")
        self.assertNotIn(quote, CORPUS, "the fixture must actually contain the wrap, or the test proves nothing")

    def test_entities_are_normalised_in_the_quote_and_the_corpus(self) -> None:
        code, report = run(["--corpus", str(self.corpus), "--quote", "«поставка»"])
        self.assertEqual(0, code, report)
        self.assertTrue(report["ok"])
        self.assertIn("&laquo;", report["span"])

    def test_a_genuinely_repeated_quote_needs_context(self) -> None:
        """Two occurrences behind identical short context; only a wider window separates them."""
        quote = "zzzzz товары покупателю"
        # no context: the two regions are indistinguishable
        code, report = run(["--corpus", str(self.corpus), "--quote", quote, "--context", "0"])
        self.assertEqual(1, code, report)
        self.assertFalse(report["ok"])
        self.assertEqual(2, report["regions"])
        self.assertEqual(2, report["regions_with_context"])
        # a window wide enough to see 11111 vs 33333 separates them
        code2, report2 = run(["--corpus", str(self.corpus), "--quote", quote, "--context", "12"])
        self.assertEqual(0, code2, report2)
        self.assertEqual(1, report2["regions_with_context"])

    def test_a_quote_that_is_unique_given_its_own_context_is_accepted(self) -> None:
        """A repeated phrase is fine if the surrounding text distinguishes the intended occurrence."""
        code, report = run(["--corpus", str(self.corpus), "--quote", "товары покупателю", "--context", "5"])
        self.assertEqual(0, code, report)
        self.assertGreater(report["regions"], 1, "the phrase itself must still occur more than once")
        self.assertEqual(1, report["regions_with_context"])

    def test_a_quote_from_the_wrong_revision_is_reported_with_a_hint(self) -> None:
        code, report = run(["--corpus", str(self.corpus), "--quote", "Продавец обязуется возместить убытки"])
        self.assertEqual(1, code, report)
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["regions"])
        self.assertIn("hint", report)

    def test_exit_code_two_on_missing_corpus(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOL), "--corpus", str(Path(self.tmp.name) / "nope.txt"), "--quote", "x"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, proc.returncode)


if __name__ == "__main__":
    unittest.main(verbosity=2)
