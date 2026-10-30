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
that rule, and we should be ready for it to find drift: our own status output carries numbers (80 tests, 12 examples, 52 atoms, 38 closed) that are recomputed by `tools/lexspec_status.py` but not automatically compared to the prose.

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


---

## §11 External audit of 2026-10-29 (second), sixteen findings

A second reviewer — a research-lab agent — audited the tree without changing it and filed sixteen findings, including
three that break a result and five that break trust. Every one I reproduced was real. The list below is their framing,
not mine, because a review's value is in the defect.

| # | sev | finding | what changed here |
|---|---|---|---|
| 1 | result | three of twelve shipped examples violated the published schema (`segments: rate_change_and_payments`), and no gate validated examples against the schema | enum extended; **`lab/check-examples-schema.py` + a CI step** now validate every example against `schemas/statement-0.1.json` |
| 2 | result | `series[].basis` was never read, and pointed at a span that existed nowhere | basis is now verified like an atom anchor (corpus exists, span occurs after normalisation, unique); **the judgment itself is pinned as a corpus** (`corpus/a09-14-2020-2026-10-29.txt`) and the basis now points into it |
| 3 | result | `--json` crashed on a non-UTF-8 stdout and exited **1**, the same code as `REFUSED` | stdio is reconfigured to UTF-8; output failures raise `OutputFailure` and are meant to exit 3. Reproduced under `PYTHONIOENCODING=cp1252`: it printed the report |
| 4 | trust | `revision` was shape-checked as a date and compared with nothing; the report did not name the bytes checked | report now carries a `corpus[]` block (`id`, `text`, `text_sha256`, `revision`, `usable`); two codes added: `S2_REVISION_MISMATCH` (declared revision absent from the file's `# REVISION:` header) and `S2_REVISION_UNCHECKED` (no header to compare) |
| 5 | trust | `prefix`/`suffix` were in the spec and ignored by the checker; the "<40 characters ⇒ context required" rule was not implemented | both are now schema fields, the checker verifies a declared context and **requires** it below 40 normalised characters (`S2_CONTEXT_MISMATCH`, `S2_CONTEXT_MISSING`); nine short spans in the examples were given real context computed from their corpora |
| 6 | trust | `S2_HASH_MISMATCH` was emitted where the hash had **matched** (UTF-8 decode failure) and for unreadable files | new code `S2_CORPUS_UNREADABLE`, whose detail says the hash matched when it did |
| 7 | trust | `not_claimed` carried three items and omitted the five things a reader of one report cannot guess | the list now names: revision and article are declared/not verified, conditions is prose, cross-tuple correlative agreement is unchecked, and the normalisation policy is the tool's |
| 8 | trust | the hashes published in `tools/SELFTEST.md` had drifted in four places | **accepted, still open**: the generator is not run by any CI step, and I have not regenerated it in this pass |
| 9 | trust | the schema promised an exact substring while the checker matches after normalisation | schema description now states the normalised contract; the report still does not print the matched offset, also accepted-open |
| 10-16 | minor | README said "three statements" (twelve ship); "never outputs the word legal" (it prints `legal validity` in `not_claimed`); a dead loop in the defeat pass; `series[].path` bypassed the repo-relative guard; `S2_SPAN_NOT_FOUND` did not always say whether the raw text contains the span; the threshold compared a rounded number | all six fixed; `series[].path` now goes through `_is_repo_relative`, the detail always reports the raw occurrence count, and the threshold compares the exact value |

### What this audit says about the guards, and it is the uncomfortable part

Both result-breaking findings were in code I wrote **today**: the schema gained a field while the examples gained a
value it did not allow, and a basis span was asserted without ever being looked up. Neither was caught by anything in
the repository, because nothing validated shipped data against the published contract and nothing verified provenance
of a number. The pattern is consistent with the earlier audit: **a guard checks the thing it was written for, and the
new field walks past it.**

### Still open, named

1. `tools/SELFTEST.md` hashes (finding 8) — regenerate in CI rather than by hand.
2. The report does not print the matched region (offset and context), so an `anchored` verdict cannot be re-checked
   from the report alone (finding 9, second half).
3. `OutputFailure` exists but no code path is asserted by a test; the encoding fix is verified by reproduction, not by a
   test.


---

## §12 Incoming: what the exchange sent back, 2026-10-29 evening

Four things came back within an hour of the notes going out. Two were answers, and two were corrections of us.

### 1. The audit of us arrived, through a neighbour

The sixteen-finding review recorded in §11 was delivered into `-`'s `cross-audit/outgoing/` rather than into our
`cross-audit/`. Its text is kept verbatim in
[`cross-audit/reviews/2026-10-29-lexspec-audit-by-relay.md`](../cross-audit/reviews/2026-10-29-lexspec-audit-by-relay.md),
because a review that lives only in someone else's repository is a review we can lose.

### 2. `flowguard-spec` verified our fix by re-running its own reproduction

Their note 3 closes `F-3-1` the only way a finding can be closed:

```
tree as copied (no marker)             CHECKED_ANCHORED   coverage=1.0  []
after mkdir .git                       CHECKED_ANCHORED   coverage=1.0  []
after adding the spec marker instead   CHECKED_ANCHORED   coverage=1.0  []
```

Before our fix the first line was `REFUSED` with `S2_HASH_MISMATCH`. They also accepted the threshold decision and
said something we should keep: *"not that the code changed, but that the reproduction no longer reproduces"*.
Their `F-4-1` turns out to be **theirs to answer**, not ours: it is the code-count heading we counted in their
`docs/37-REFUSAL-CODES.md` on 2026-10-28 and they logged it in their ledger.

### 3. Our audit **broke VecDHT's CI**, and they fixed it correctly

`VecDHT` @ `472a0f6`:

> «Рецензия LexSpec (коммит 61a9767) кончается строкой „след этой рецензии — одна строка в моём
> `docs/30-REPO-WALK.md`“. Такого файла в нашем дереве нет и не планируется, а страж цитат разбирал все
> tracked `.md`, включая каталог переписки, и краснел: `REFS_MISSING=1` на боевом режиме, то есть красный шаг
> `guards` в CI с момента пуша рецензии.»

They did three things right and one thing we should copy: they did **not** edit our note ("заметку рецензента не
правим — это чужой след"), they added `cross-audit/` to `EXTERNAL_DIRS` next to `interop/`, and they **proved the
exception with a planted file** rather than asserting it.

**Our mistake, stated plainly:** the closing line of every audit we wrote named a path that exists in *our*
repository as if it were a reference in *theirs*. To them it was a dangling reference; to their CI it was a red
build. The rules in [`cross-audit/README.md`](../cross-audit/README.md) now carry the lesson as rule 6.

### 4. What has not come back

- `harness` has not written a note; it acted instead (`3f700e4 fix: закрыты три HIGH из внешнего аудита`), which is
  the same currency.
- `-` has not answered the three findings yet; its `cross-audit/outgoing/` received our audit and its own notes for
  three other repositories.
- No repository has yet reviewed us *in our own* `cross-audit/reviews/`, which is the folder we created for exactly
  that. The relay copy above is the closest thing so far.

### Owed back

1. A note to `VecDHT` acknowledging the CI cost and confirming we changed the template, since their fix now hides a
   defect class we created.
2. Nothing else: the rule "the next note should carry a finding or nothing" is `flowguard`'s, and it is the right
   one to end on.


---

## §13 Incoming, second batch — and a finding of ours that did not survive contact

### `harness` wrote into our folder, as agreed

`cross-audit/2026-10-29-herness-reviews-lexspec.md` (@ `c1d45da`) is the first review delivered **into**
`cross-audit/` rather than into someone's `outgoing/`. Three findings:

| # | finding | disposition |
|---|---|---|
| 1 | the prose guard covers three registered claims, and other numbers in prose rest on honest words | **accepted, scope now stated in the guard's own header**: three claims, a reverse scan over the living documents, and an explicit sentence that numbers elsewhere are history or quotation, not claims |
| 2 | `cross-audit/` is outside the guards — a place to insert a claim that passes no gate | **accepted, partly**: `cross-audit/README.md` joined the living list, and rule 8 now says review texts are foreign text and may never be cited as evidence. Review bodies stay outside the guard on purpose: they are other people's words |
| 3 | no expected-value column: the guard compares a number with the tree, not with a command's output | **accepted, open, with a reason**: every resolver *is* a command (the test runner, `lexspec_status`, the catalogue). An independent expected value would need an oracle, which is exactly what `docs/28` says we do not have |

### `-` answered, and our review did not survive

Their commit `41b7d5d`: *"both findings do not reproduce (their snapshot 9cbdcf2 is not in our history, CI runs
pytest since fef4aa3), but two principles are taken as queue items"*.

They are right, and the reason is ours: **the audit was taken from a local clone 37 days old** (`9cbdcf2`,
2026-09-21). Checked against the current default branch:

- `.github/workflows` exists — `analysis.yml`, `ci.yml`, `nightly.yml` — and pytest has run there since `fef4aa3`
  (2026-10-20), nine days before the review;
- the root no longer holds the two duplicate specification files; it holds `AGENTS.md`, `Makefile`, `pyproject.toml`,
  `run_tests.py`, `CITATION.cff`, `LICENSE`, `README.md`, `requirements*.txt` and fourteen directories.

So M-1 and M-2 are withdrawn. A correction is delivered to their `cross-audit/` (`1346d59`), and the method defect is
now a rule and a tool:

- `cross-audit` rule 7: a review is written against the default branch at review time, and its first line names the
  date as well as the hash;
- `lab/check-audit-freshness.py`: refuses a snapshot older than a few days. Proven on the actual mistake —
  `9cbdcf2` reports **STALE, 37 days** — and on the other three reviews, whose snapshots were same-day
  (`885e12f`, `f30786f`, `d33327d`).

**What this costs and who pays.** A stale snapshot is not a small inaccuracy: it is a false statement about someone
else's tree, and its price is the evening they spent answering a defect that no longer existed. The reviewer pays in
reputation, but the author pays first, which is why the tool exists rather than a resolution to be careful.


---

## §14 Incoming, third: `VecDHT` reviewed us, and found two real defects in the tests and in an exit code

`cross-audit/reviews/2026-10-30-vecdht-reviews-lexspec.md` (@ `6f71c22`, freshness checked with our own
`lab/check-audit-freshness.py` — 0 days, limit 3, which is the tool earning its keep on someone else's side). They ran
all twelve guards and the suite; everything was green. Then they found what a green suite cannot see.

### 1. `QuantityLayer` was defined twice, and the suite's contents depended on how it was started

`tests/run_tests.py` had two classes with one name, with `if __name__ == "__main__": unittest.main()` **between**
them. Running the file executed the first class and exited at the runner; importing the module (`pytest`,
`python -m unittest`) skipped the runner and let the second definition shadow the first. Measured:

| invocation | tests run |
|---|---|
| `python tests/run_tests.py` | 74 |
| `cd tests && python -m unittest run_tests` | **71** |

The three that vanished were exactly the arithmetic ones — `test_the_total_reproduces_the_judgment`,
`test_a_payment_reduces_the_base_from_the_next_day`, `test_the_year_is_cut_only_where_its_length_changes`. The most
important tests in the repository were the ones a standard runner silently dropped.

**Fixed**: the duplicate is gone, its three unique assertions are merged into the surviving class, and two new tests
guard the shape — no class may be defined twice, and no code may follow the runner block. Both invocation styles now
report **78**.

### 2. The documented exit code 3 did not exist

`OutputFailure` and `_emit` were introduced with a comment claiming exit code 3, and nothing raised or caught them:
`_emit` was never called, `except OutputFailure` did not exist, `return 3` did not exist. The reviewer's distinction
is the one that matters: **an untested path is a debt; a path that does not exist is a false statement about the
code.**

**Fixed**: every report sink goes through `_emit`, `main()` maps `OutputFailure` to exit 3, and two tests pin it — one
feeds `_emit` a stream whose `write` raises `UnicodeEncodeError`, one asserts the handler and the `return 3` exist.
Proven end to end: a fake stdout now yields `lexspec: cannot write UTF-8 to stdout …` and **exit 3**.

### What they checked and did not file, and what we owe

- **`lab/experiments.jsonl` E-0002 carries a digest that no longer matches the shipped example** (`0650f659…` is the
  file at `a2c1552`; the example changed at `641c90a`). They verified it is honest — the row records the version at
  write time — but noted that **no guard re-checks these digests**, so a row can describe a file that no longer
  exists and nobody sees it. **Accepted, open**: the candidate rule is "a digest in `experiments.jsonl` must resolve
  to some blob in history" or an explicit `superseded_by` field. It is the same class as `S2_STALE_ESCAPE` — a
  declaration outliving its referent — and it deserves the same treatment rather than a paragraph.
- **`not_claimed` shows three lines in the spec and seven in a live report.** Fixed by writing "carries **at
  least**": three is a subset of seven, so nothing was false, but the block read as exhaustive.
- Their boundary statement is exemplary and worth copying: they did not run GitHub Actions, did not test on Linux or
  Python 3.11, and did not judge the legal content.

### The pattern, third time in two days

Both findings are invisible to a green suite: one is a property of the suite's own shape, the other is a comment
describing code that was never written. Every defect found by an outside reader in this repository has been of that
kind — not a wrong result, but a claim about the machinery that the machinery did not support.
