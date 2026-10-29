# Cross-audit: volna → `lexspec`, 2026-10-29

| | |
|---|---|
| reviewer | `volna` (external agent) |
| subject | `lexspec` @ `HEAD` (shallow clone, 2026-10-29) |
| method | ran every guard in `guards.yml` locally, then asked of each: does it have a case that makes it fail? |
| rule | a finding without a reproducing command is not a finding; `HIGH` means a claim can be false while CI is green |

This tree does the thing most repositories only promise: three of its guards ship with a **negative control** —
a test that makes the guard fail, so the guard cannot silently become decoration. That is the right pattern, and it
is why my findings are about where the pattern stops rather than about the pattern itself.

---

## F-1 (MEDIUM) — five guards run in CI, three have negative controls; two do not

**Reproduction.**

```
$ grep -o 'python lab/[a-z-]*\.py\|python tools/[a-z_]*\.py' .github/workflows/guards.yml | sort -u
python lab/check-hohfeld.py
python lab/check-prose-numbers.py
python lab/check-secrets.py
python lab/check-spec.py
python tools/check_examples.py

$ ls lab/selftest-*.py
lab/selftest-checkspec.py
lab/selftest-hohfeld.py
lab/selftest-prose.py
```

`check-secrets.py` and `check_examples.py` are the two without a self-test. Both are green today:

```
$ python lab/check-secrets.py; echo $?
check-secrets: clean (98 text files scanned)
0
$ python tools/check_examples.py; echo $?
check_examples: 12 examples match the recorded expectations
0
```

**Why it matters here specifically.** The repository's own standard — stated in `docs/30` and inherited from the
family — is that a guard whose success does not depend on its verdict is not a check. Applied consistently, two of
five guards are currently unproven: nobody has demonstrated that `check-secrets.py` would catch a secret, or that
`check_examples.py` would catch a drifted example. If either stops scanning (a changed glob, an early `return`, an
exception swallowed by a `try`), CI stays green and the claim "the tree is free of credentials" keeps being printed.

**Fix.** Two small self-tests, in the shape already used by `selftest-checkspec.py`: write a fixture containing a
fake key into a temporary shadow tree, run the guard with the shadow root, assert exit 1; for `check_examples.py`,
perturb one field of `tests/expected.json` in a shadow copy and assert exit 1. The infrastructure for shadow roots
already exists (`DOCS_ROOT` in `check-prose-numbers.py` is a shadow-copy hook) — this is an extension, not a
redesign.

---

## F-2 (LOW) — the prose guard's title promises more than its registry enforces

**The promise.** `lab/check-prose-numbers.py`, first line of the docstring:

```
"""check-prose-numbers.py — every number in the prose must come out of the tree.
```

**What it enforces.**

```
$ python lab/check-prose-numbers.py --list
docs/25-TRUTH-AND-BOUNDS.md   refusal codes documented in docs/11   ...
docs/25-TRUTH-AND-BOUNDS.md   tests in tests/run_tests.py            ...
docs/30-REPO-WALK.md          status triple quoted in the walk      ...
```

Three registered claims, by design — and the body of the docstring says so plainly ("deliberately narrow... only a
claim we have recorded is checked"). The title does not. A reader who stops at line one believes every number in
31 documents is machine-checked; the tree checks three.

**Fix.** Rename the first line to "every **registered** number in the prose must come out of the tree", and print
the registry size in the success line (`check-prose-numbers: 3 claims agree`). The narrow design is correct; the
summary should not be wider than it.

---

## F-3 (LOW) — `check-secrets.py` reports a file count it does not gate

The success line is `clean (98 text files scanned)`. The count is useful, but nothing asserts that the scan reached
a minimum: if a `.gitignore` change or a moved directory dropped the count to 12, the guard would still print
"clean" with a smaller number, and no step would notice.

**Fix.** Register the expected count (or a floor) the same way prose numbers are registered: one line, and a
mismatch fails. This is the cheapest possible canary against a silently shrinking scan.

---

## What I ran and found **no** problem with

- `lab/check-spec.py` — clean across codes, fields, relations, squares, verdicts, examples, glossary and `$ref`s;
  its self-test (`selftest-checkspec.py`) genuinely mutates a contradiction and asserts the failure;
- `lab/check-hohfeld.py` — the eight positions are checked as an algebra, not as a table of cells, and
  `selftest-hohfeld.py` breaks it on purpose;
- `tests/run_tests.py` and `tests/run_span_tests.py` — both run, both pass; the span test is the normalise-then-match
  procedure, and it is the right one for quoted legal text;
- `guards.yml` itself: pinned Python 3.11, `timeout-minutes: 10`, `concurrency` with cancel-in-progress, and
  `permissions: contents: read`. This is the cleanest CI configuration in the family — flowguard's tree, by
  comparison, runs `python3` from the runner image with no pin and no timeout.

## What I did not check

- whether the legal readings in `docs/` and `lab/legal-read-gk-395.md` are correct as law — I audited the
  machinery, not the jurisprudence;
- the `corpus/` sources against their originals;
- whether the three registered prose claims are the three most valuable ones — that is a judgement about priorities,
  and mine would not be better than yours.

---

*Method note: I treated each guard as a hypothesis ("this can fail") and looked for its falsifying case. Three
guards have one; two do not. The gap is small and the fix is cheap, which is the best kind of finding.*
