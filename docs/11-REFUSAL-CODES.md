# Refusal codes — the closed vocabulary of "this statement did not survive"

A refusal is a finding about the **input**, not about the checker's mood. Every code below names a defect
that a human can locate and fix, or a limitation that is the point of the tool. A code is never reused for a
different defect, and never renumbered.

Report shape, per finding:

```json
{ "code": "S2_SPAN_AMBIGUOUS", "atom": "a3", "detail": "span occurs 2 times in corpus gk-rf" }
```

`atom` is `null` for statement-level findings. Order in the report is the order of the checks in the spec:
`C0 → S1 → S2 → S3 → S4 → S5 → S6 → S7`.

---

## C0 — canonicalisation

| Code | Raised when | Remedy |
|---|---|---|
| `C0_CANON` | canonical serialisation is not reproducible: floating-point number present, non-UTF-8 byte, BOM, or CRLF line endings | remove the float (ratios are computed, never stored), save as UTF-8/LF |

## S1 — is this a statement at all

| Code | Raised when | Remedy |
|---|---|---|
| `S1_SCHEMA` | a required field is missing, a type is wrong, an enum value is outside the closed set, a date is not `YYYY-MM-DD`, `jurisdiction` is empty, `corpus` is empty | fix the document |

`S1_SCHEMA` is deliberately a single code: the detail string names the field. Splitting it would create a
hundred codes that all mean "not a statement".

## S2 — anchoring

| Code | Raised when | Remedy |
|---|---|---|
| `S2_NO_CORPUS` | `anchor.corpus` names no `CorpusRef` in the statement | add the corpus, or fix the handle |
| `S2_HASH_MISMATCH` | sha256 of the corpus file ≠ declared `text_sha256` | re-pin the corpus: either the file changed or the declaration is wrong. Never fix by editing the hash alone |
| `S2_SPAN_NOT_FOUND` | `span` does not occur in the pinned text | the quote is not from this revision, or it was paraphrased, or it was copied from a rendered page and crosses a line break. Quote the raw bytes |
| `S2_SPAN_AMBIGUOUS` | `span` occurs more than once, counted **by start position with overlaps included** (spec §5 rule 4) | widen the span until it is unique, or anchor to a larger context |

**Why ambiguity is a refusal and not a warning.** Two identical occurrences of a phrase mean the citation
does not identify a provision. If one occurrence is later amended, the anchor silently follows the other one.
A citation that can re-point itself is not evidence, so the tool refuses to accept it as one.

## S3 — Hohfeld layer

| Code | Raised when | Remedy |
|---|---|---|
| `S3_UNKNOWN_RELATION` | `relation` is not one of `right, duty, privilege, no-right, power, liability, immunity, disability` | use a position from the square; if none fits, the atom is out of scope for v0.1 |
| `S3_MISSING_COUNTERPARTY` | a relative relation has `counterparty: null` | name the other party. A duty to the world is not a duty |
| `S3_OPPOSITE_CONFLICT` | two atoms assert opposite relations on the same `(bearer, verb, object, counterparty)` over overlapping time | one of the two is wrong, or the time intervals are wrong. This is the check that justifies the whole layer: it catches "A may not do X" written next to "A may do X" in the same document |

## S4 — closure and escape accounting

| Code | Raised when | Remedy |
|---|---|---|
| `S4_UNDEFINED_REF` | `bearer`, `counterparty` or `action.object` names nothing in `terms[]` | define the term, or declare it `open` and declare the escape |
| `OPEN_TERM` | an atom is not closed: a referenced term has `status: "open"`, `action.open` is `true`, or the atom failed anchoring. The detail names which | this is a *finding*, not a failure by itself: it lowers coverage. It is declared in `escapes[]`, never hidden |
| `S4_UNDECLARED_ESCAPE` | the checker computed an atom as not closed and `escapes[]` does not list it | declare it. An undeclared escape is a silent reduction of coverage in the author's favour |
| `S4_STALE_ESCAPE` | `escapes[]` lists an atom that the checker computed as closed | remove it. A stale escape makes the report look more cautious than the encoding is |

The pair `S4_UNDECLARED_ESCAPE` / `S4_STALE_ESCAPE` exists so that the declared escape list cannot drift from
reality in either direction. Without it, coverage is self-reported.

## S5 — time

| Code | Raised when | Remedy |
|---|---|---|
| `S5_EMPTY_INTERVAL` | `from > until` | fix the dates. An empty interval asserts nothing and is almost always a typo |

A date that is not a valid `YYYY-MM-DD` is `S1_SCHEMA`, not `S5_EMPTY_INTERVAL`: a malformed date is a defect
in the document's shape, and one defect is never reported under two codes.

## S6 — incompatible positions

| Code | Raised when | Remedy |
|---|---|---|
| `S6_CONFLICT` | two atoms carry *correlative* relations on the same ordered tuple `(bearer, verb, object, counterparty)` over overlapping time — i.e. the correlative was written on the wrong side — and `conflicts_policy.default` is `"report"` | either the conflict is real (fix an atom) or a resolution policy applies (declare it). **Known false positive:** two genuine mutual obligations about the same action land on one tuple and are reported; distinguish the actions or split the statement |
| `S6_UNRESOLVED_CONFLICT` | a policy is declared but the conflict is not named in `lex_specialis` with a prevailing atom | name the prevailing atom, or set the policy back to `report` |

A declared policy is the author's assertion that the corpus resolves the conflict. The checker verifies that
the assertion is **complete** — every conflict accounted for — not that it is **correct**. This distinction is
stated in the spec because conflating them is how a checker starts giving legal advice by accident.

## S7 — coverage

| Code | Raised when | Remedy |
|---|---|---|
| `THIN_COVERAGE` | coverage < `--coverage-threshold` (default 0.8) | close more atoms, or accept the weaker verdict `CHECKED`. The threshold is a flag, not a constant: a verdict quoted without its threshold is not reproducible |

`THIN_COVERAGE` does not mean the statement is wrong. It means the statement is too thin to support the
strength of verdict that its author wants. Those are different sentences and the report keeps them apart.

---

## What a refusal is not

- **Not a legal opinion.** `CHECKED_ANCHORED` does not mean the clause is lawful; `REFUSED` does not mean it
  is unlawful. Both are statements about an encoding.
- **Not a parse failure.** If a reader cannot tell what to do after a refusal, the code is wrong and should be
  split, not explained in prose.
- **Not permanent.** Codes are versioned with the spec. A statement refused under v0.1 may pass under v0.2
  if the vocabulary grows; the report always names the spec version it was checked against.
