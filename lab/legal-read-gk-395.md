# Doctrinal read of art. 395 — what the text contains, compared with what we encoded

| | |
|---|---|
| date | 2026-10-29 |
| what this is | a comparison of our six atoms against the statute's six paragraphs as published, plus one practitioner note |
| what this is **not** | a legal review of the encoding. A review asks "is this how a lawyer would read it"; this asks "does the text contain more than we encoded". Only the second question can be answered from the web |
| sources opened | the full text of art. 395 (all six paragraphs) at `grazhkod.ru`, and a practitioner calculation note at `ya-advokat.ru`; Пленум ВС РФ № 7 п. 48 was opened earlier the same day |

## §1 Paragraph by paragraph

| Paragraph | What it says | Our atom | Consequence |
|---|---|---|---|
| п. 1 first sentence | a duty to pay interest on the sum of the debt for unlawful use / retention / delay | `a1` | covered |
| п. 1 second sentence | the rate is the Bank of Russia key rate in force in the relevant periods | `a2` | covered, and now quantified |
| п. 1 third sentence | **these rules apply unless a different rate is set by law or by contract** | — | **missing.** It is a defeat of `a2` (and of `a1`), and a broader one than the penalty in п. 4 |
| п. 2 | if the creditor's losses exceed the interest, the creditor may claim the excess | `a3` | covered |
| п. 3 | interest runs **until the day the sum is paid**, and there is no shorter period unless law or contract sets one | `a1` only, without an endpoint | **missing as a rule.** The quantity layer takes `period.to` from the statement; nothing encodes how `to` is determined |
| п. 4 | if the parties agreed a penalty for the same breach, the interest is not recoverable, unless law or contract provides otherwise | `a4` | covered, and now expressed as a defeat |
| п. 5 first sentence | compound interest is not allowed unless the law provides | `a5` | covered |
| п. 5 second sentence | **in entrepreneurial relations compound interest is not allowed unless the *law* provides** — a contract is not enough | `a5` | **collapsed.** One atom carries two rules with different carve-outs |
| п. 6 | the court may reduce the interest **on the debtor's application**, not below the amount computed at the п. 1 rate | `a6` | **partially covered.** We encoded the floor and the power, not the procedural trigger |

## §2 What the read changes

1. **Three atoms are missing and one is collapsed**: the general "different rate" carve-out (п. 1 sentence 3), the
   endpoint rule (п. 3), the debtor's application (п. 6), and the entrepreneurial nuance of п. 5.
2. **Coverage over our own atom set overstated completeness.** We reported 0.833 for a statement that encodes
   roughly two thirds of the normative content. The metric was never wrong — it measures the statement, as the
   report says — but the number reads as "almost complete" and it is not.
3. **The fix is not "add atoms until the number drops"**; it is to derive the atom set from the text rather than
   from intuition. The rule this suggests is recorded as P7 in `docs/29`: *one normative sentence, one atom, or a
   declared reason why not*.

## §3 What was done with it

`examples/12-gk-rf-395-doctrinal.lex.json` adds the three missing atoms and splits п. 5 into two:

| new atom | position | anchored span |
|---|---|---|
| `a7` | duty — interest runs to the day of payment | «взимаются по день уплаты суммы этих средств кредитору» |
| `a8` | power — a different rate may be set by law or contract, defeating `a2` | «если иной размер процентов не установлен законом или договором» |
| `a9` | power — the court reduces **on the debtor's application** | «суд по заявлению должника вправе уменьшить» |
| `a10` | duty — no compound interest unless the *law* provides (entrepreneurial case split out) | «применение сложных процентов не допускается» |

`a8` is declared with `applies: false` — the contract in this hypothetical does not set a different rate — so it
defeats `a2` only in principle, and the report must say `established` for `a2` while recording that a defeat exists.
That is exactly the distinction the four-valued status exists for.

## §4 Boundary

This note replaces the missing *human* read only in the sense that it is better than nothing: it is a comparison
against published text, and published text does not tell us whether a practising lawyer would accept our atom
boundaries. The falsifier F1/F4 in the charter remains open, and this note says so rather than closing it.
