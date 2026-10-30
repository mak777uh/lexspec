# 32 — Portfolio insights: five repositories, one problem class

The owner asked for a careful pass over the pinned repositories, looking for mechanisms rather than summaries. Five
were read in parallel (four by delegated readers, `cases` by me), and the useful finding is that **this family has
already solved three of the problems `lexspec` is still failing at** — and one of those solutions was built *in
response to our own review*, which makes it a round trip rather than a borrowing.

Everything below names a file and a line, and the three marked **verified** I opened myself.

---

## §1 What was found, and what it is worth

| # | mechanism | where | what it solves | state |
|---|---|---|---|---|
| 1 | **Meta-guard over the guard catalogue** — every `lab/check-*` must ship a planted-defect mode *and* be called by a persistent contour; the list is discovered from the directory, not written in the guard | `VecDHT/lab/check-guard-selftests.py` | "a guard whose zero is indistinguishable from *did not look*" — the exact class of our volume-vs-passing defect | **verified** (ran it: 22 guards, 0 without selftest) |
| 2 | **Two silences are not equality** — flags comparisons where both operands can carry the "no fact" sentinel, because `[ "$a" = "$b" ]` is true when neither fact exists | `VecDHT/lab/check-none-compare.py` | a gate that greens out of two absences | **verified** (read the docstring and logic) |
| 3 | **Digest as write-admission** — a result cannot be journalled unless its artifact is re-hashed at read time | `harness/core/journal.py` | our *"digests in `experiments.jsonl` that nothing re-checks"* | reported, unverified by me |
| 4 | **Exemptions must be re-earned** — a waiver is keyed to (id, class, referents) with a reason, and a waiver whose referent reappeared is itself a finding | `flowguard-spec/lab/check-artifact-refs.py:90` | stale whitelists, stale escapes, stale allowances | reported, unverified |
| 5 | **Generated status, build fails when stale** — the status page is produced by the measuring commands; a hand-edited number cannot exist | `flowguard-spec/tools/fg_status.py:186-199` | tables in prose that drift from the run | reported, unverified |
| 6 | **Evidence liveness** — every link a case rests on is fetched in CI; 403 = alive but closed, only 4xx/5xx/0 are dead | `cases/tools/check_evidence.py` | provenance that rots silently | **verified** (copied into `lab/check-citations.py`) |
| 7 | **Case record shape** — Claim / Evidence / Reproduce / Verdict / Limits, one plain sentence first | `cases/README.md`, `cases/*/README.md` | our experiment rows have no limits and no one-line verdict | **verified** (read 601, 602, 604) |
| 8 | **Cross-repository canonical differential** — flowguard loads *our* `lexcheck.py` and diffs its canonicaliser against ours byte for byte | `flowguard-spec/lab/xrepo-canonical.py:19,39` | nobody else checks our canonical form | **verified** (imports `lexcheck`, uses `canonical_text`) |

## §2 What this says about us, plainly

1. **Every mechanism above is about a guard that cannot fail quietly.** Our three external audits said the same thing
   in different words: volume measured where the claim was about passing; a self-test that names its own cases; a
   documented exit code that did not exist. The family has a vocabulary and a toolkit for this, and we were writing
   our own from scratch.
2. **One of our findings came back as a mechanism.** `VecDHT`'s number contract (`check-ci-numbers.py`) was created in
   response to our V-1 review, and its design is better than our `check-prose-numbers.py`: it requires the **counting
   definition itself** to be written in the header, and it treats an unknown command as a finding. That is the
   round-trip the exchange was for.
3. **`cases` solves our provenance problem by a route we did not consider**: not "pin the bytes" (we do that) but
   "prove the address still answers". Both are needed and only one of them was in our CI.
4. **`harness`'s registry is closer to what we called `not_claimed`** than our own document is: each claim carries an
   evidence type that caps the words it may use. Their gate for it has a defect (substring matching, so any digit
   anywhere passes) — which is a warning about the shape, not a reason to skip the idea.

## §3 What was adopted in this pass

- **`lab/check-citations.py`** — external sources are fetched; 403 is alive-but-closed, only 4xx/5xx/0 are dead, and
  the binary is resolved with `shutil.which` because a hardcoded `curl.exe` once made the source repository's CI call
  every link dead. First run on us: **18 addresses, 2 dead** — both `consultant.ru` deep links from the two Russian
  corpus headers. That is exactly the argument for pinning: the provenance address is unstable, the bytes are not.
- **`lab/check-guard-catalog.py`** — the meta-guard. Enumerates every guard by directory prefix, requires a
  planted-defect mode and a CI call, keeps a **baseline** of accepted exceptions with reasons, and — the important
  half — treats a baseline entry that no longer applies as a finding. Our own debt list is in the file.
- **A weekly citation job** rather than a per-push one: the network is not the repository's business, and a check that
  fails for a proxy reason teaches people to ignore it.

## §4 What was not adopted, and why

- **`assert`-based invariant registries** (`morphogenesis/config.py`): `python -O` deletes every one of them silently.
  A guard that vanishes under a flag is worse than no guard, because the CI still says green.
- **Free-text claim tables with a regex column** (`harness/CLAIMS.md`): their own reader reports five rows with
  non-runnable commands and a gate that passes single digits by substring. The idea (claim = command + expectation)
  is right; the implementation shows how it decays.
- **A status page generated on every run** (`flowguard`): worth doing, but our numbers already come from
  `lexspec_status.py` and the prose guard; adding a third generator before the first two are trusted would be
  decoration.
- **Importing another repository's canonicaliser as the second implementation**: differential, not independent — and
  their own note says so. Our twin (`tools/lexcheck_twin.py`) was written from the spec, not from the checker, which
  is the property that makes agreement worth something.

## §5 The one thing this pass changed about how we work

Two of the five repositories keep a **baseline of accepted debt** — a list of exceptions with reasons, checked in
both directions: an exception that stops applying is a finding. We had no such thing; our whitelists in
`check-prose-numbers` were write-only. That is now the pattern for every exemption in this repository, and it is
written into the guard's own docstring so the next exemption inherits it.


---

## §6 What the adopted rules found in this repository on their first run

Two of the three adoptions produced findings immediately, which is the only evidence that matters for a guard.

**Exemptions that expire** (`flowguard`'s rule, applied to our own whitelist): four entries in
`lab/check-prose-numbers.py` excused numbers `60 tests`, `61 tests`, `17 codes`, `22 codes` — all four had been
rewritten out of the documents days earlier, and the entries had been silently excusing nothing. Deleted. The rule is
now part of the guard, with the incident in its comment, and doc §3 records it as the pattern for every exemption in
this repository.

**The catalogue guard** (from `VecDHT`), on its first run over our own guards, reported that five of eight had no
planted-defect mode and that the new guard itself was not wired. Every one of those was true. The excused set is now
five entries with reasons, and its red path was proved by planting a guard with neither property — two findings, then
green after deletion. Writing it also reproduced the family's own warning twice in ten minutes: my first version
counted the *word* `--selftest` inside a docstring as a selftest mode, and the very patch that fixed it was mangled by
shell quoting. Both are the defect the guard exists to catch, committed while writing the guard.

**Citation liveness** (`cases`): 18 addresses, **2 dead** — both `consultant.ru` deep links in the two Russian corpus
headers. That is not a defect to fix by deleting the link: it is the argument for pinning. The address is unstable;
the bytes are not, and the report names the digest, not the URL.
