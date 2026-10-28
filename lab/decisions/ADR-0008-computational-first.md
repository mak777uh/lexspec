# ADR-0008 — Computational provisions first, contract prose later

- **Date:** 2026-10-28
- **Status:** accepted (evidence: four independent answers to round-01 Q10 and Q16, plus the primary numbers in
  [`docs/16` §1](../../docs/16-ROUND-01-ANSWERS.md))
- **Supersedes in part:** [ADR-0003](ADR-0003-both-tracks-two-systems.md) — "two legal systems" stands, but the
  *kind* of provision we start with changes

## Context

We started with a supply-contract clause (ГК РФ art. 506) and an EU rights article (GDPR art. 17). The first
was easy and shallow; the second exposed the carve-out wall and could not be encoded past 75 %.

The measured evidence says that is not an accident of our choice:

- Catala's French family-benefits formalisation — 27 articles, ≈1,500 lines including the legal text, 6 scopes,
  63 context variables, 83 definitions — is presented by its authors as representative of a **medium-size legal
  document**;
- a single complex US tax-section excerpt (≈15 % of IRC §121, ~350 lines) took **four 2-hour pair sessions** with
  tax-law specialists;
- all four answering models, independently, named **tax, benefits, penalties, deadlines and interest** as the
  domains where checked encoding pays, and named general contract law as the domain where it does not.

The reason is structural: a computational provision is already a decision procedure over numbers, dates and
conditions. Its vocabulary is narrow, its exceptions are enumerable, its ground truth can be computed twice, and
civil servants maintain it anyway. A contract clause is written to be argued about, not executed.

## Decision

1. **The first corpus is computational provisions**, not contract prose. Concretely, the pair for the two-system
   comparison becomes: **ГК РФ art. 395** (interest on a monetary obligation, where the rate arrives by reference
   to the central bank key rate — a hard test of L5 quantity anchoring) and a **tax or benefit computation**
   (where the ground truth can be recomputed independently).
2. **Contract clauses are not abandoned, they are deferred.** They become the third corpus, once defeat, quantities
   and transitions exist. Encoded without those, they produce the GDPR outcome: an honest 75 % that describes
   nothing operative.
3. **The unit of cost is hours per computational provision**, and the report of any future measurement names:
   initial encoding, independent legal review, and maintenance, separately — because the first two have data and
   the third has none ([`docs/16` §7](../../docs/16-ROUND-01-ANSWERS.md)).
4. **Contracts may still be used as a negative test**, and should be: the fact that our model cannot encode a
   bespoke service clause without defeat and remedy is a finding about the model, not a failure of the clause.

## What this costs

The deontic/Hohfeld side of the project — our most developed part — becomes *less* exercised, because
computational provisions are mostly duty-with-quantity rather than a rich square of positions. That is
deliberate: the square stays, but it stops being the thing under test until the money layer works.

## What would overturn this

- If the numbers for ГК РФ art. 395 turn out to be hundreds of lines for a single article, the "hours per
  provision" estimate is wrong and the scope must shrink again.
- If the rate-by-reference case cannot be anchored (the key rate is published by the central bank, not in the
  statute), then quantity anchoring is impossible for exactly the provisions this ADR selects, and the pivot
  fails — which would be a major, and useful, negative result.

## Addendum, 2026-10-28 — the rate is anchorable

Tested: the Bank of Russia key rate is published as a **dated machine-readable series** through its SOAP service
(209 dated records for 2026 to date; the raw response hashes to `e394f342…1c701d`). So the "referenced number"
case works — but only in one shape, which is now the rule:

> an external quantity is a **pinned reference to an official dated series**, resolved at encoding time and
> carried as (identifier, date, value, digest); it is never a runtime call, because a live feed destroys
> reproducibility and reproducibility is the certificate.

A provision whose number cannot be pinned this way is **refused**, not evaluated against a live source. Details
in [`docs/16` §11](../../docs/16-ROUND-01-ANSWERS.md). Still missing: an official worked example to compare our
computation against — round 02, Q23.
