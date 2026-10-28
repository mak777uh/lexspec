# ADR-0003 — Both tracks in parallel, and two legal systems from the start

> **Amended 2026-10-28 by [ADR-0004](ADR-0004-correctness-not-novelty.md).** The "narrow track" below is framed
> as properties *nobody else claims*. That framing is withdrawn: novelty is not a criterion, and the two
> properties are kept because they are **required for a correct verdict** (a span that occurs twice does not
> identify a provision; a refusal a reader cannot act on is a defect), not because they are ours. Everything else
> in this ADR stands.

- **Date:** 2026-10-28
- **Status:** accepted (owner decision: *"оба одновременно, это как минимум параллельно две юр системы проверит"*)
- **Context:** [`docs/12` §6](../../docs/12-LANDSCAPE-REGISTER.md) found that four of our novelty claims are
  already published work (Arxo Law, LegalLean, and two 2026 papers). The choice offered was: integrate what
  exists and compete on the legal side, or narrow to the one property nobody else claims.

## Decision

**Do both, and start with two legal systems rather than one.**

1. **Integration track.** Take the architecture that now exists in public (byte-pinned sources, evaluation
   document, checked semantics) rather than reinventing it, and spend our effort where it is thin: civil-law
   jurisdictions, the Hohfeld layer as a *checkable* pairing, and the refusal vocabulary as a published
   artifact.
2. **Narrow track.** Keep the two properties that the survey could not find anywhere: **uniqueness of the
   anchored span** (not just "the quote exists", but "it identifies one place") and **the refusal as a
   first-class result with a closed code vocabulary**.
3. **Two legal systems from the start**: one civil-law (ГК РФ) and one EU act (GDPR), because a model that only
   fits one system's drafting style is a document format, not a language. This also answers round-01 Q4
   empirically instead of by argument.

## Why "both" is not indecision

The two tracks answer different questions. Integration asks *what should we stop building*; the narrow track
asks *what can we claim that nobody else has*. A project that only integrates has no reason to exist; a project
that only defends its novelty builds what already exists. Running them in parallel costs little because the
narrow track is two properties inside the same checker, not a second product.

## What this forbids

- Presenting H3, H12, H15 or H17 as contributions. They are requirements inherited from published work.
- Claiming generality from one jurisdiction. Two systems or no claim.
- Adding a third jurisdiction before the second one has a **measured** encoding cost in
  [`lab/cost.md`](../cost.md).

## First consequences

- The GDPR measurement exists: [`examples/07-gdpr-art17.lex.json`](../../examples/07-gdpr-art17.lex.json),
  cost recorded as measurement 1. It found the carve-out wall (Art. 17(3)) and an asymmetry in corpus
  availability (eCFR API returns dated revisions; EUR-Lex answered HTTP 202 with an empty body).
- The next measurement must be a ГК РФ article of comparable size, so the pair is comparable.
- A seam for `defeats` is now a **blocking** design question, not a v0.3 nicety: the first real EU article
  cannot be encoded without it.
