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
| `S2_CORPUS_NOT_FOUND` | no file exists at `corpus[].text`, searched from the repository root and upward from the statement | the path is wrong, or the tree was moved without the corpus. The declared sha256 was never compared — this is **not** a hash mismatch. Deliberately separate: blaming the corpus for a resolution problem was finding F-3-1 in flowguard's review |
| `S2_REVISION_MISMATCH` | the statement's `corpus[].revision` does not appear in the file's `# REVISION:` header | correct one of the two. The report claims a verdict is about `corpus@revision`, so this is the difference between a claim and a decoration |
| `S2_REVISION_UNCHECKED` | the corpus file carries no `# REVISION:` header, so the declared revision cannot be compared | add the header; until then the revision is a declaration, which the report now says out loud |
| `S2_CONTEXT_MISMATCH` | the declared `anchor.prefix`/`suffix` do not surround the span in the pinned text | recompute them with `python tools/span_hint.py --corpus … --quote …`, which prints the raw context. Context that is never checked is decoration |
| `S2_CONTEXT_MISSING` | the normalised span is shorter than 40 characters and no context is declared | add 32 characters of prefix and suffix. Measured: 11 of 604 short random quotes were ambiguous, 0 of 585 long ones ([docs/29](../docs/29-PRINCIPLES-AND-DATA.md) P4) |
| `S2_CORPUS_UNREADABLE` | the file exists but cannot be read or is not valid UTF-8 — in the second case the declared sha256 **matched** | re-export the text as UTF-8; **do not re-pin**, the bytes are the right bytes. Separate from `S2_HASH_MISMATCH` because the remedy is different and because telling an author to re-pin a correct corpus is the misdiagnosis this code exists to prevent |
| `S2_HASH_MISMATCH` | sha256 of the corpus file ≠ declared `text_sha256` | re-pin the corpus: either the file changed or the declaration is wrong. Never fix by editing the hash alone |
| `S2_SPAN_NOT_FOUND` | `span` does not occur in the pinned text **after normalization** (spec §5) | the quote is not from this revision, or it was paraphrased, or it was copied from a rendered page so a line break or a character entity sits inside it. The detail must say whether the span occurs in the *raw* text: if it does, the defect is normalization, not absence |
| `S2_SPAN_AMBIGUOUS` | `span` **with its context** (`prefix`/`suffix`) still selects more than one region, counted by start position with overlaps included (spec §5 rule 4) | widen the context window until one region remains, or anchor to a structural identifier. Note: the W3C convention permits multiple matches and selects all of them; our single-target requirement is stricter **by declaration**, not by standard |

**Two corrections from round 03** ([`docs/26`](../docs/26-ROUND-03-MERGED.md) W6), verified against
[w3.org/TR/annotation-model](https://www.w3.org/TR/annotation-model/) §4.2.4:

1. The standard requires the text to be **normalized before recording** (markup removed, entities decoded).
   Therefore a quote that fails because it crosses a line break is a **normalization defect in our procedure**,
   not a repeated quote. Mislabelling it as ambiguity was our error, and it was the cause of 6 of 14 failures in
   two real measurements.
2. Exact-span uniqueness is **not** the field's rule. `TextQuoteSelector` uses `exact` plus `prefix`/`suffix`, and
   when several matches remain the specification says the selection "SHOULD be treated as matching all of the
   matches". We still refuse, because a citation that selects three places is not a citation — but the refusal is
   our product requirement and is now declared as such.

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

## S8 — quantities

The layer that lets an atom carry a number ([`docs/27`](../docs/27-QUANTITY-LAYER.md)). Two rules shape the whole
group: a number must be traceable, and an arithmetic convention must be declared rather than assumed.

| Code | Raised when | Remedy |
|---|---|---|
| `S8_UNANCHORED_BASIS` | a series provides no checkable `basis` (`corpus` + `span`), so the numbers that rest on it have no provenance | state the basis, or do not use the series. **An absent basis is not a weaker basis**: the atom that cites the series stays open. Found by an external audit on 2026-10-31, which deleted the field and watched the quantified atom stay closed |
| `S8_SERIES_NOT_PINNED` | a quantity references a series with no `path`, no `digest`, a missing file, a digest mismatch, or a file that is not a usable series | pin the artifact: save the retrieved values, hash the file, declare both |
| `S8_UNANCHORED_QUANTITY` | a quantity is malformed, or a literal has no integer `value` | a number nobody can trace is not a number here |
| `S8_SEGMENT_GAP` | the series has no value for part of the declared period | the period is outside the pin's coverage; narrow it or pin a wider series |
| `S8_UNDECLARED_ARITHMETIC` | `period.day_count` or `rounding.mode` is `undeclared` | a **caution, not a refusal**: it caps the verdict at `CHECKED` and lifts by itself once both are declared with a basis |

`S8_UNDECLARED_ARITHMETIC` is the only code in the catalogue that is deliberately a ceiling rather than a stoppage:
the encoding can be right while the arithmetic convention rests on nothing, and the verdict should say so instead of
pretending either certainty or failure.

## S9 — defeat

The layer that lets one position defeat another ([`docs/13`](../docs/13-DEFEASIBILITY-CHOICE.md) §3). It records the
relation and the declared applicability; it never computes which exception *should* apply, because that is a legal
judgement and this project does not make those.

| Code | Raised when | Remedy |
|---|---|---|
| `S9_DEFEAT_UNDEFINED` | `atom.excepts` names something that is not an atom in this statement | fix the id, or encode the defeater as an atom |
| `S9_DEFEAT_CYCLE` | an atom excepts itself, or two atoms except each other | a cycle is not a priority question; break it in the encoding |
| `S9_APPLICABILITY_UNSTATED` | a position is defeated by an atom whose `applies` is not asserted | set `applies: true` or `false` **with a citation**. Silence is not negation (D4): the report says `neither`, and the refusal says why |
