# 16 — Round 01 answers: what four returns changed, and what they did not

Four independent answers to [`docs/07`](07-ROUND-01-QUESTIONS.md) arrived on 2026-10-28 (two in English, two
mixed; none signed, so provenance is unknown — the same protocol failure as SEARCH-01). They agree with each
other more than they disagree, and three of the agreements are decisive. Verified numbers below were re-read
from the primary source in this session; everything else is marked.

---

## §1 The decisive measurement (Q10)

All four answers circled the same source; one gave the numbers, and I checked them in the paper text.

**[Catala: A Programming Language for the Law](https://arxiv.org/abs/2103.03198), §6.3 and §4.5 — verified by
reading the HTML:** 

| Artifact | Size | Effort |
|---|---|---|
| French family benefits (27 articles of the Social Security Code + executive orders) | ≈ **1,500 lines** including the legal text; 6 scopes, 63 context variables, 83 definitions and rules | not stated; the authors call these numbers "fairly representative of the authoring effort required for a **medium-size legal document**" |
| US IRC §121, formalised up to paragraph (b)(4) — ≈ **15 %** of the section, ~**350 lines** including the law text | 15 % of one complex section | **four 2-hour pair-programming sessions** with US tax-law specialists ≈ 8 pair-hours ≈ 16 person-hours |
| F\* mechanisation of the compiler core (type safety + translation correctness) | ≈ 3,500 lines | **1 person-month** |
| The compiler itself | — | ≈ 5 person-months |

**What this does to falsifier F3.** "Minutes per article" is the wrong unit — an article is not a unit of work.
The defensible units are **hours per computational provision** and **lines per medium document**. On this
evidence, a *structurally ordinary* provision costs hours, not minutes, and a medium document costs about 1,500
lines. Our GDPR Art. 17 measurement (4 atoms, 75 % coverage, ~9 minutes, exceptions unrepresentable) is
consistent with that: we were fast because we encoded almost nothing — no quantities, no deadlines, no defeat.

The honest conclusion for scope: **encoding is affordable for computationally dense provisions and not for
general contract prose**, which is also what all four answers said in Q16. That is a strategy change, recorded in
[ADR-0008](../lab/decisions/ADR-0008-computational-first.md).

---

## §2 Q1 and Q2 — anchoring is an integration, and identity is not fixity

Consensus across all four:

- **Numbered-fragment identifiers exist and are official**: ELI subdivision URIs (`…/art_2/par_2`), Akoma Ntoso
  `eId` (required to be stable across versions and renumbering), UK legislation.gov.uk provision URIs down to
  paragraphs, USLM element paths. `[partially verified: legislation.gov.uk URI documentation and the ELI
  subdivisions specification were named by three answers; I opened neither in this session]`
- **Byte-range identifiers do not exist** from any publisher. W3C Web Annotation selectors (TextQuote/
  TextPosition) are client-side, not publisher-guaranteed.
- **A stable identifier does not identify immutable wording.** UK documentation separates identifier URIs,
  version-specific document URIs and representation URIs. Point-in-time text is a *different* artefact with its
  own URI (`/data/YYYY-MM-DD`).
- **EUR-Lex consolidated texts are documentation, not law**; only the Official Journal act is authoritative. In
  Russia the official source is the publication of amending acts; consolidated texts are commercial.

**Change to H1 and to spec §5** (made below): an anchor is no longer one span. It is a triple —
**structural path + quote selector + digest of the retrieved representation** — and each part can fail
separately. Byte-range uniqueness survives only as a property of our own copy, never as a claim about the
publisher.

**Change to the claim we are allowed to make**: "this is our anchored copy of the *expression* identified by X at
date Y", never "this is the law". That sentence goes into the charter's non-claims.

---

## §3 Q3 — the failure we design for is not documented anywhere

All four searched; none found a case of a citation system retracting an anchor because the text was amended
underneath it. What they found instead: point-in-time publishing treats amendment as *expected behaviour*, and
tooling discussions treat "preserve the cited version across document updates" as an open problem.

**Decision:** `S2_SPAN_AMBIGUOUS` stays as a *designed-for* refusal, and it must stop being described as
protecting against an observed failure. Three proposed sibling codes are recorded here but **not** added to the
catalogue, because a code enters only with a test (AGENTS §7):

| Proposed code | Distinguishes |
|---|---|
| `S2_VERSION_UNPINNED` | the anchor names an identifier whose text is version-dependent and no revision was pinned |
| `S2_TEXT_MISMATCH` | the identifier resolves, but the retrieved representation's digest is not the pinned one |
| `S2_SPAN_AMBIGUOUS` (existing) | the pinned text is correct, and the quote identifies more than one place |

---

## §4 Q4 and Q5 — Hohfeld is a vocabulary, and "may" is not one operator

Consensus: the eight positions are a starting vocabulary; they are not a complete semantics, and the loss is in
**remedy, status and transition**, not in the eight cells. The concrete stress cases named for Russian law:
ГК РФ **157(3)** (bad-faith prevention or facilitation of a condition is treated as its occurrence or
non-occurrence), **450.1** (a unilateral refusal notice changes or terminates the relation), **секундарные
(преобразовательные) права**, ответственность as a distinct protective relation, ничтожность/оспоримость as
*statuses of acts* rather than positions.

Q5 is answered identically by three of four: "may require" is **a power whose exercise triggers a claim**, often
bundled with a liberty not to exercise it — never a single primitive.

**Change:** the model needs a **transition layer** (events that change positions) and a **status dimension**
(valid/void/contestable), not a ninth Hohfeld position. Recorded in
[ADR-0009](../lab/decisions/ADR-0009-transition-layer.md) as a required v0.2 layer, with the rule that a
compound atom must be representable as power + triggered claim, or refused.

---

## §5 Q7 and Q15 — the soundness theorem, restated or dropped

Four of four agree: a soundness theorem is trivial when the algebra *is* the implementation, and useful only as
**relative soundness against an independently axiomatised algebra** — "if the checker reports no conflict, none
exists in the algebra", where the algebra is stated separately (model-theoretic, or a proved translation to
SMT). Three of four would delete H3 first; one would delete the `CHECKED_ANCHORED` label first.

**Change to H3 (second amendment, below):** the theorem is restated as relative soundness, Lean is out of v0.2
unless an independent algebra exists, and the formal ambition is replaced by the metrics we can actually produce:
determinism of refusals, stability of verdicts under irrelevant edits, and coverage.

---

## §6 Q12 and Q13 — the certificate needs a person and a renewal chain

**Q12, verified against the rule text as quoted:** FRE 902(13) requires certification by a qualified person that
the *process or system* produces an accurate result; 902(14) authenticates a *copy* by digital identification
(hash). A hash proves identity of bytes, never accuracy of the process. 21 CFR 11.10 additionally requires
validation, access control and secure time-stamped audit trails.

**Q13:** the established preservation mechanism is **RFC 4998 Evidence Record Syntax** — timestamp renewal plus
hash-tree renewal, performed *while the old evidence is still trusted*, and ETSI TS 119 511 for preservation
services.

**Changes:** the certificate gains a **process attestation with a named responsible person** and a **renewal
chain**, and stops calling itself evidence of accuracy. H12 and H17 are amended accordingly.

---

## §7 Q8, Q9, Q11 — the three unknowns that stay unknown

- **Q8:** nobody found a machine-checked proof that two independent encodings diverge. Four searches, four
  negatives. It remains a **candidate contribution**, and the phantom Lean library stays `X`.
- **Q9:** the only downloadable proof artefacts anyone could name are Catala's F\* mechanisation (≈3,500 lines,
  1 person-month, type safety + core translation) and the **LogiKEy** Isabelle/HOL theories (value-oriented legal
  reasoning). Neither proves a property of an executable statute article. WP-04 stays thin, and the register
  now separates five different proof obligations: source integrity, semantic correspondence, compiler
  correctness, detector soundness, adequacy of the human encoding.
- **Q11:** there is **still no measurement of maintenance per amendment** in any source any model could name.
  Amendment *frequency* is measurable (legislation.gov.uk publishes "changes to legislation"); effort is not.
  This remains the most dangerous unquantified number, and it is now flagged as **blocking** for any claim about
  long-term viability.

---

## §8 Q14 — the verdict wording is the one change that needs no research

Four of four independently said the same thing: `CHECKED_ANCHORED` will be read as legal approval. The fixes
they propose are compatible:

> **"No conflict found in the encoded subset (N of M atoms closed; source copy dated X, digest Y). Source
> linkage verified. Legal interpretation, completeness, current applicability, and unencoded provisions were not
> verified."**

**Planned change (not made in code):** keep the enum (an API), change the **human-facing line** so that coverage
appears on the same line as the outcome, and make the scoped sentence mandatory in the report under a new field
`statement_of_scope`. The wording above is the candidate; it must be tested with two lawyers who have not seen
the system, and the test is falsifier F4.

---

## §9 What four returns did *not* change

- `S2_SPAN_AMBIGUOUS` stays — as a designed refusal, not an observed one.
- The canonical-bytes rule stays; nobody challenged byte-level identity, and one answer reinforced it (identity
  and fixity are different properties, both needed).
- The refusal vocabulary stays closed; the three proposed siblings wait for tests.
- The certificate as a *reproducible record* stays; what changes is the claim attached to it.

---

## §10 Scoreboard

| Question | Consensus | Verified by us | Effect |
|---|---|---|---|
| Q1 | numbered fragments yes, byte ranges no | partially | H1 split into three parts; spec §5 rewritten |
| Q2 | point-in-time exists per publisher; claim must shrink to "our copy of the expression" | partially | charter non-claim added |
| Q3 | no documented retraction case | yes (four negatives) | `S2_SPAN_AMBIGUOUS` reframed as designed-for |
| Q4 | Hohfeld insufficient for remedy/status/transition | no | ADR-0009 transition layer |
| Q5 | "may require" = power + triggered claim | partial | compound atoms must be representable or refused |
| Q6 | defeasible logic, linear for the propositional case; deferral cost is guard growth and lost source link | partial | matches `docs/13`; cost must be measured |
| Q7 | relative soundness only | yes (agreement) | H3 second amendment; Lean out of v0.2 |
| Q8 | no prior art found | yes (four negatives) | stays a candidate contribution |
| Q9 | Catala F\* and LogiKEy; no statute-level property | yes for Catala | five proof obligations separated |
| Q10 | hours per computational provision, ~1,500 lines per medium document | **yes, from the paper** | F3 narrowed; ADR-0008 computational-first |
| Q11 | no measurement at all | yes (four negatives) | blocking unknown |
| Q12 | hash ≠ process accuracy; a qualified person must certify | yes (rule text) | H12 amended |
| Q13 | RFC 4998 renewal chain | yes (named standard) | H17 amended |
| Q14 | the label misleads; scope must be on the same line | yes (four agree) | planned verdict-wording change |
| Q15 | delete H3 first, or the composite label | — | both recorded |
| Q16 | computational provisions before contracts | **yes (paper + all four)** | ADR-0008 |
