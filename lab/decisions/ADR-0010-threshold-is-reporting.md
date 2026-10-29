# ADR-0010 — The coverage threshold is a reporting metric, not a verdict rule

| | |
|---|---|
| date | 2026-10-29 |
| status | accepted |
| changes | `docs/10` §9 (verdict table), `tools/lexcheck.py` (verdict computation), `docs/11` (new code) |
| raised by | flowguard-spec, review round 1 (`interop/reviews/2026-10-28-flowguard-reviews-lexspec.md`) |

## The question

flowguard asked for a statement in which the coverage threshold decides the verdict while `escapes` does not.
Their reasoning: `CHECKED_ANCHORED` requires no escapes **and** coverage ≥ threshold; an open atom must be declared
in `escapes` (`S4_UNDECLARED_ESCAPE`); therefore coverage < 1.0 implies at least one escape, and one escape already
caps the verdict at `CHECKED`. So the threshold term can never be the deciding one.

## Verification

Read the code rather than the description (`tools/lexcheck.py`, verdict block):

```
if findings.refusals():          REFUSED
elif findings.escapes() or coverage < threshold:   CHECKED
else:                            CHECKED_ANCHORED
```

For the threshold to decide, one would need `findings.escapes()` false and `coverage < threshold` true. An atom is
closed only when it is anchored and its relations resolve; an atom that is not closed **is** an escape, and an
undeclared one is refused. So the first branch already excludes the second, and flowguard is right: the threshold
is decoration.

**There is no such statement.** The test `test_coverage_is_unchanged_by_the_threshold_but_thin_is` had already
recorded the symptom ("the escape alone is enough") without drawing the conclusion.

## Decision

1. The verdict no longer consults the threshold. `CHECKED_ANCHORED` requires: no refusals, no escapes, every atom
   closed and anchored.
2. `--coverage-threshold` stays, with `THIN_COVERAGE` and `coverage_threshold` in the report, and the report now
   says `coverage_threshold_role: "reporting-only (ADR-0010)"`. A number that cannot flip a verdict is still useful
   to a reader and to CI; it must not pretend to be a rule.
3. `docs/10` §9 says this in words, so the next reader does not have to reverse-engineer the branch.

## What would reopen it

If a future verdict tier makes partial coverage meaningful — for instance `CHECKED_ANCHORED` allowed with declared
escapes above a high threshold — the threshold becomes a rule again, and this ADR must be superseded rather than
edited.

## Also decided in the same pass: finding F-3-1

Not a threshold question but the same review, and it belongs in the record: the verdict depended on whether the tree
sat inside a repository marker (`find_repo_root` fell back to the statement's directory, `corpus/...` stopped
resolving, and the report said `S2_HASH_MISMATCH` — blaming the corpus). Fixed by resolving corpus paths upward
from the statement as well as from the root, by naming the base in the report (`root_source`), and by giving a
missing file its own code `S2_CORPUS_NOT_FOUND` instead of a hash error. Regression test: a copy of example 01 in a
directory with no `.git` and no `docs/` must still reach `CHECKED_ANCHORED`.
