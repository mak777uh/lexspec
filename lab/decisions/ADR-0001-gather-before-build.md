# ADR-0001 — Gather sources before building

- **Date:** 2026-10-28
- **Status:** accepted (owner decision)
- **Supersedes:** the implementation order proposed in conversation on 2026-10-28
- **Affects:** [`docs/06-FROM-TEXT-TO-PROOF.md`](../../docs/06-FROM-TEXT-TO-PROOF.md) §4

## Context

Twenty hypotheses are registered (`H1`–`H20`), each with a kill test, and none of them is measured. The
repository currently contains a working v0.1 checker, a schema, six examples and sixty tests — all of which
check *the encoding*, and none of which implements the three mechanisms that make the pipeline honest about
provenance.

On 2026-10-28 the following next step was proposed and is, by estimate, half a day to a day of work:

1. **H13** — `Verdict` constructible only inside the checker module; the encoder-facing API returns
   `CandidateAtom` with no conversion to `Verdict`; a build-blocking scan asserts no other module names the
   constructor.
2. **H11** — `term_id = sha256(canonical(name, def))`, carried in the report, with an `imports: [term_id]`
   header field to opt in to cross-statement identity.
3. **H12** — certificate output: statement hash, encoding version, every corpus hash, checker version,
   verdict, findings hash-chained so a single mutated row is detectable, and `not_claimed`.

Followed by **H3** — a `lean/LexSpec/` skeleton: eight Hohfeld positions, correlative and opposite maps,
intervals over dates, `findConflicts`, and the first soundness theorem — which is the artifact worth showing
to a hostile reader.

## Decision

**Do not build any of it yet.** Continue collecting sources and enlarging the hypothesis register first.

The owner's instruction on 2026-10-28 was: *"пока все записывай, будем набирать больше инфы"* — record
everything, we will gather more information. That instruction takes precedence over the estimate above: the
estimate is cheap, but building before the evidence base is wider risks building the wrong three mechanisms,
and each of them (a `Verdict` type, a term-identity scheme, a certificate format) is much more expensive to
change after it exists than before.

## What this leaves unfixed, stated plainly

These are known holes, recorded here so that no later reader mistakes the repository for something it is not:

| Hole | Consequence today |
|---|---|
| `Verdict` is an ordinary value any importer can construct | the "model proposes, checker disposes" split is a convention in prose, not a mechanism |
| term identity is string equality of `name` | `поставщик` in two statements is two terms that happen to be spelled alike; cross-statement reasoning is impossible |
| the certificate does not exist | a report is reproducible by re-running the checker on the same tree, and by nothing else |
| no hash chain over findings | a report can be edited row-by-row without detection |
| no `verification_policy` (H16), no validity window (H17) | the tool decides what counts as acceptable evidence, i.e. grades its own work |
| no per-check non-claims (H19) | `not_claimed` is one list for the whole report, too coarse to stop the specific misreadings |

None of these is a bug in v0.1 as specified: every one is named in [spec §11](../../docs/10-SPEC-v0.1.md) or
in the hypothesis register. What this ADR prevents is someone reading "the checker works" as "the pipeline is
honest".

## Revisit trigger

Reopen this decision when **any one** of the following arrives through the intake register
([`lab/sources.md`](../sources.md)):

1. At least one **worked artifact** of deontic or normative formalisation with machine-checked proofs
   available to read (source files, not a paper abstract). This is what would tell us whether H3's algebra is
   the right one before we freeze a type.
2. An **evidence-integrity pattern from a regulated industry** — a hash-chained or WORM audit log with a
   published retention and admissibility rationale. This would settle H12 and H17's format in one go, instead
   of us inventing it.
3. A **real clause** from the owner's own use, with a deadline, which makes H7's cost measurement possible.
4. An explicit owner instruction to build.

## Consequences

- `docs/06` §4 stays as a *proposed* order; this ADR is what governs.
- No Lean files, no new Python modules, no schema change until the trigger fires.
- The intake register is now the active work item: every source that arrives is recorded with what it moved,
  even if the answer is "nothing".

## Notes on the estimate, kept for honesty

The "half a day to a day" figure was not measured — it is an estimate from reading, and this repository's own
rule is that an unmeasured number is not a result ([`AGENTS.md`](../../AGENTS.md) §1). It is recorded here as
an estimate and must not be quoted as a measurement. When the work does start, the first thing to record is
the actual time.
