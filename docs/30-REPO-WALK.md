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
that rule, and we should be ready for it to find drift: our own status output carries numbers (74 tests, 12 examples, 52 atoms, 38 closed) that are recomputed by `tools/lexspec_status.py` but not automatically compared to the prose.

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


---

## §9 External audit of 2026-10-29, and what it changed here

A neighbouring agent audited this repository by reading the tree, without running anything, and filed five findings.
All five were correct. This section records them in their own words, because an audit's value is in the defect, not
in the reply.

| sev | finding | what was wrong | what was done |
|---|---|---|---|
| **HIGH** | `lab/check-prose-numbers.py` `_run_test_suite()` | the resolver read `Ran N tests` and returned N **regardless of the exit code**, so a red suite still satisfied the sentence "N tests pass". The claim is about passing; the resolver only measured volume | the resolver now requires exit 0 **and** `OK`; a red run becomes a `suite-red` finding naming the failure instead of a number. The rule is a pure function and is unit-tested with synthetic output (three cases) |
| **MEDIUM** | `CLAIMS` coverage | three registered claims over ~40 documents, and no reverse direction: a new number in the prose was invisible. The status triple also omitted `closed`, which the resolver already computed | added `closed` to the triple; added `unregistered_numbers()`, which scans living documents for count-adjacent numbers and reports those with neither a claim nor a whitelisted reason; extended `FORBIDDEN.files` to the workflow itself |
| **MEDIUM** | `lab/selftest-prose.py` | three checks in a file whose docstring says a checker that only prints "ok" is decoration — two of three claims and one resolver had never been seen red | the self-test now derives one mutation per registered claim from the guard's own `CLAIMS`, plus the three suite-green cases, the stale phrase, the unregistered count and the mirror. **10 checks, count computed** |
| **LOW** | `guards.yml` header | "Why these four steps" over eleven invocations — the comment had outlived its count, which is exactly the class `FORBIDDEN` exists for | header rewritten without a number, and `guards.yml` added to `FORBIDDEN.files` so the mechanism now guards the contour it describes |
| **LOW** | `README.ru.md` | the mirror rule was declared and had no instrument | added `mirror_numbers()`: the same normalise-then-compare idea as spec §5 rule 0, applied to two files. **First run found the real problem: only counts are comparable, and the mirror carries none of them — it has drifted by content, not by digits.** Recorded below as an open item |

### What the audit found that we had not

Two things worth naming, because both are structural rather than clerical:

1. **A guard can measure the wrong quantity and still be green.** "74 tests pass" was checked against "the suite
   printed 74", and the difference between those sentences is the difference between a measurement and a ritual.
2. **A self-test that names its own cases tests only those cases.** The previous version hard-coded one mutation; the
   audit's phrase for it — two of three claims never seen red — is now the shape of the fix: the cases are derived
   from the guard, so adding a claim adds a check.

### Open, and honestly not fixed here

`README.ru.md` has drifted by content: the English README gained documents 23–30 and the mirror did not. The number
instrument cannot see that, and neither can any number instrument — it is a translation-maintenance debt. The options
are to regenerate the mirror from the canonical file or to declare it a summary rather than a mirror; until one is
chosen, the sentence "where they disagree, this one wins" is true and unenforced.


---

## §10 Cross-audit exchange, 2026-10-29 — four reviews out

The owner asked for an exchange: each project audits the others and leaves a note in `cross-audit/`. Four notes went
out today, each with reproducing commands, each stating what was not checked, and none of them changing anything in
the host repository except that one file.

| repository | commit | headline finding |
|---|---|---|
| `harness` | `dca2e9b` | gates exist and are green (9/9, plus `selftest`), but **no workflow runs them on push**; `CLAIMS.md`'s header declares six columns while 34 of 38 rows carry seven, and `gate_claims` never compares shape, so the gate is green on a table it does not describe |
| `VecDHT` | `61a9767` | its 16 guards all have self-tests and all are wired — the strongest contour in the family — but the **test counts in the `verify.yml` header have drifted by 40** (claimed 764, tree 804: orders 16→24, index 117→118, node 203→208, net 102→105, cli 79→102) |
| `flowguard-spec` | `64e9008` | `lab/check-interop.py` is tracked and **never called** by `guards.yml` (eight steps, not one of them interop) |
| `-` (morphogenesis) | `0b3afb1` | eight test modules and **no executor**; `pytest` prescribed in the README, `torch` imported in 24 places, no pinned environment; two root files both declare v5.5-EXP FINAL Rev.7 at 211 KB and 362 KB with suffixes that name nothing |

### What the exchange already gave us

Writing someone else's audit is a better test of your own discipline than reading it. Three things came back
immediately:

1. **`harness`'s gate list is better shaped than ours.** Nine named gates, each returning a list of problems, and
   `selftest` plants defects to prove the gates can fail. We have the same idea spread across four scripts; theirs is
   one command with one exit code.
2. **`VecDHT`'s meta-guard is the thing we were missing this morning.** `check-guard-selftests.py` takes the guard
   list **from the directory by prefix**, not from a list inside itself, and separates "no selftest" from "selftest
   not wired". Our audit this morning found exactly the failure it prevents: a self-test that names its own cases
   tests only those cases. Their device is the general form.
3. **A number with a command is still not checked.** `VecDHT` prints the grep commands next to 764 — and the number
   drifted anyway. That is the strongest argument yet for the rule we adopted today: a count in prose needs a
   resolver, not a citation.

### What we owe back, in the same currency

- `harness`: name the seventh column or drop it, and add the arity check to `gate_claims`; give the gates an executor.
- `VecDHT`: either drop the exact counts from the CI header or add `check-ci-numbers.py`; and state the counting rule
  so that a stranger's count and theirs cannot differ by definition.
- `flowguard-spec`: wire `check-interop.py` or say in `AGENTS.md` why it is manual; add the two-README number check.
- `-`: one workflow, one current-spec pointer.

### Boundary

These four reviews are written by us, not by their authors, and a review says as much about the reviewer's priorities
as about the subject. Each note lists what was not opened; none of them ran a foreign test suite, and none changed a
foreign file except the note itself.
