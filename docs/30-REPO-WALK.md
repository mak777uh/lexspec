# 30 — Repository walk, 2026-10-29

The owner asked for a periodic walk over our repositories — to coordinate and to take insights, not to comment on
other people's work. This is the first walk recorded in this repository, and the format is deliberately boring:
what moved, what concerns us, what we take, what we now owe.

Cadence written here so it is not re-invented: **after any review addressed to us, and at least once every two
working sessions.** A walk without an entry does not count as a walk.

---

## 1. `flowguard-spec` — a review of us, and it found a real defect

Review round 1 (`interop/reviews/2026-10-28-flowguard-reviews-lexspec.md`, against our `2c74648`) is the most
valuable artifact produced about this project so far, because it is the only one where someone ran our tool against
our claims and broke something.

**Kept (their six probes):** duplicate `atom.id`, hand-written `coverage`, unknown top-level field, edited corpus
with a stale digest, open atom without an escape, ambiguous anchor — all refusals, not warnings. They note this
matches the two ways they themselves broke their own gate, which is the strongest form of agreement available.

**Finding F-3-1 — accepted, fixed, closed with a regression test** in this session: the verdict depended on whether
the tree sat inside a repository marker. With no marker the root fell back to the statement's directory, `corpus/…`
stopped resolving, and the report said `S2_HASH_MISMATCH` — blaming the corpus for a resolution problem.
Why our own probes missed it: **every test ran from inside the repository**, so we only ever tested the case we
lived in. That is recorded as a failure of imagination, not of code.

**Question about the coverage threshold — they were right, the threshold decided nothing.** Coverage below 1.0
implies a declared escape, an escape already caps the verdict, so the threshold term could never be the deciding
one. Closed as [ADR-0010](../lab/decisions/ADR-0010-threshold-is-reporting.md); the threshold is now a reporting
metric and says so in the report. Their rule — "an invariant that cannot flip a verdict is decoration" — is adopted
verbatim.

**Also kept from them:** "a finding without a reproducing command is not a finding", and "‘could not break it’ is
evidence of an attempt, not of correctness". Both are shorter than our phrasings and therefore better.

---

## 2. `VecDHT` — a third participant appeared in the channel

`interop/2026-10-28-xcheck-to-vecdht.md` introduces **`xcheck` v0.1**, an external consistency contour pinned by
hash, which cross-checks numbers in prose against the tree across the five repositories. It is not a repository and
it edits nothing; it leaves one note per repository.

This matters for us in one specific way: `xcheck` checks *"числа в прозе против дерева"* — precisely the rule
`AGENTS.md` §1 imposes on us ("a number without a command is not a result"). We should expect a machine check of
that rule, and we should be ready for it to find drift: our own status output carries numbers (69 tests, 10 examples, 36 atoms) that are recomputed by `tools/lexspec_status.py` but not automatically compared to the prose.

**Action queued:** add a probe to our own suite that compares the numbers in `README.md` with
`lexspec_status.py`, so `xcheck` finds nothing when it arrives. That is cheaper than answering a note about it.

---

## 3. `cases` — a direct analogue of our anchor rule

Case 603, addendum: *"model proved True instead of the pinned statement; gate rebuilt to check the statement"*, and
case 604: four statements, one failed on a wrong collateral source.

This is the same failure we designed against: a model that proves something true about the *neighbourhood* of the
claim rather than the claim. Their remedy — rebuild the gate to read the pinned statement — is the same shape as
our `S2_SPAN_*`. Their case 604 is useful evidence for principle P2: one of four statements failed on a source, not
on a proof.

**Action queued:** read case 603's gate code before stage 3 (defeat), because the pattern "prove the pinned thing,
not the nearby true thing" is exactly what a defeat mechanism must not weaken.

---

## 4. `harness` — a protocol called L1-vs-L2

`docs: P10 — запрос и границы замера в одном файле`, `E-0009 протокол L1 против L2`, and a "контрольный срез" with
a verified sampling calculation. Their L1/L2 vocabulary is about measurement layers, not our architecture layers,
but the pattern is the same discipline: **state the request and the boundary of the measurement in one file**.

**Action queued:** read E-0009 before we design the next experiment; if their protocol separates "what was asked"
from "what was measured", adopt the separation in `lab/experiment.py` (we already store `principle`, but not the
question the experiment answers).

---

## 5. `-` (morphogenesis) — witness tables

Recent commits register a *witness table* for published numbers (`paper_witness.py`, `library/witnesses/arxiv.json`)
and mark a prequel as `archived_invalid` when CI blocked it, and launch a patch series because "the binding
constraint is budding mass, not its energy price".

Two takeaways. First, `archived_invalid` is a better pattern than deleting a failed artifact: ours is append-only
too, and this is the vocabulary for it. Second, their commit messages name the **binding constraint** — that is a
habit we could adopt for our own commits, since ours tend to describe the change rather than the constraint it
relieves.

---

## 6. `lexspec` — what this walk changed here

| Change | Where |
|---|---|
| `S2_CORPUS_NOT_FOUND` added; corpus paths resolve upward from the statement; `root_source` in the report | `tools/lexcheck.py`, `docs/11` |
| threshold removed from the verdict path | `tools/lexcheck.py`, `docs/10` §9, [ADR-0010](../lab/decisions/ADR-0010-threshold-is-reporting.md) |
| regression test for a portable tree without a marker | `tests/run_tests.py` |
| reply to the review | [`interop/2026-10-29-lexspec-to-flowguard-02.md`](../interop/2026-10-29-lexspec-to-flowguard-02.md) |

## 7. What we owe, in order

1. A prose-vs-tree number check in our own suite (before `xcheck` finds it).
2. Read `cases` 603's gate and `harness` E-0009 before stage 3.
3. Machine-check the eight Hohfeld positions — nobody has, including the reviewer, and we say so in writing.


---

## §8 Second pass, 2026-10-29 — what was read and what it changed here

### `cases` 603 — a parser that produced two false positives

The report is a triage of 24 bounty tasks, and its honest result is "none closed by automation". Two details matter
for us more than the result:

1. **Their first model-driven attempt failed to produce a compiling proof**, and the case records that rather than
   the intention. That is the same discipline as our `[unverified]` marks.
2. **Triaging produced two parser false positives**, which they documented. We hit the identical class the same day:
   the PDF text of judgment А09-14/2020 glued adjacent numbers together, my first parser read "10863281105.58" as an
   interest figure, and the total therefore could not be reproduced. Their two false positives and our two glued
   rows are the same failure: a parser that is confident and wrong, and a report that shows it only if you look.

**Adopted:** when a number comes out of an extraction, record how many rows parsed *and how many were discarded*.
Our quantity layer's acceptance test now needs that count, not just the total ([`docs/27`](27-QUANTITY-LAYER.md) §6).

### `harness` P10 — the request and its boundary in one file

Their protocol puts, in a single document, the request given to five models, what is **not** in the question, the
answer rules (no invented URLs, every claim with a source and a date, evidence type per item), and a "what is
already fixed" section that is explicitly not up for discussion.

**Adopted for our question rounds** ([`docs/23`](23-METHOD-LOOP.md), [`docs/24`](24-ROUND-03-QUESTIONS.md)): each
round now carries a `не входит` list and an evidence-type column, so an answer cannot satisfy a question it was
never asked while leaving the real one open.

### `flowguard` — the reviewer's own gap

Their review ends with what they did **not** check, and first on the list is the combinatorics of the eight
positions. That is now done here: `lab/check-hohfeld.py`.

### The Hohfeld check, 2026-10-29

Eight positions, two maps, eight laws:

| Law | Statement |
|---|---|
| L1 | totality and closure — every position has one correlative and one opposite, both among the eight |
| L2 | correlative is an involution: `C(C(x)) = x` |
| L3 | opposite is an involution: `O(O(x)) = x` |
| L4 | the square commutes: `O(C(x)) = C(O(x))` |
| L5 | no fixed points: `C(x) ≠ x`, `O(x) ≠ x` |
| L6 | the four correlative pairs are disjoint and cover the eight |
| L7 | both squares are closed under both maps and do not overlap |
| L8 | the spec's table and the code's table agree cell by cell |

**Result: all eight hold** for our table. The value is not the pass but the specificity: L4 is the law that catches a
plausible-looking wrong table — one edited cell usually keeps L2 and L3 true and breaks commutation — and
`lab/selftest-hohfeld.py` proves the guard fires on three mutations (broken involution, opposite outside its square,
code diverging from spec), 4 of 4 including the unmutated control.

**Boundary, stated so it is not overclaimed:** this checks that our table is an instance of the *standard reading*
of Hohfeld's algebra. It does not check that the algebra is the right model of any particular legal system, and it
says nothing about whether the atoms written with these positions are correct.
