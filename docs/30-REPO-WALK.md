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
that rule, and we should be ready for it to find drift: our own README carries numbers (60 tests, 9 examples,
20 atoms) that are recomputed by `tools/lexspec_status.py` but not automatically compared to the prose.

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
