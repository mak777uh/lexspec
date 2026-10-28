# LexSpec v0.1 — the minimal formal core

Status: **draft, implemented by `tools/lexcheck.py`**. This document is canonical: where the code and this
document disagree, this document is right and the code is a bug.

Reading order: [`docs/00-CHARTER.md`](00-CHARTER.md) explains why these choices exist. This file explains
what a statement *is* and what a check *means*. [`docs/11-REFUSAL-CODES.md`](11-REFUSAL-CODES.md) is the
closed vocabulary of ways a statement can be wrong.

---

## §1 Vocabulary

| Term | Meaning, precisely |
|---|---|
| **statement** | one JSON document conforming to `schemas/statement-0.1.json` |
| **atom** | one legal position asserted in a statement: a relation, a bearer, an action, optional conditions, a time interval, and an anchor |
| **relation** | one of the eight Hohfeldian positions (§4) |
| **anchor** | a pointer to an exact substring (`span`) of a corpus text pinned by revision and sha256 |
| **corpus** | a set of pinned texts shipped with, or referenced by, the statement; never "the law" |
| **encoding** | the schema version plus every declared term definition: what the atoms were allowed to mean |
| **verdict** | the result of the check, one of `REFUSED`, `CHECKED`, `CHECKED_ANCHORED` (§9) |
| **coverage** | the fraction of atoms whose meaning is closed (§8) |
| **escape** | an atom whose meaning is explicitly not closed, with a reason |

A statement is *not* a program and has no evaluation semantics. It is a claim about legal positions, written
so that a machine can find defects in the claim.

## §2 Document model

One statement is one JSON object. Field by field:

```
lexspec         "0.1"                      — version of this spec the statement claims
id              string                     — stable identifier, not a hash
kind            "norm" | "clause" | "scenario"
jurisdiction    [string]                   — uppercase codes; a statement about no jurisdiction is refused
corpus          [CorpusRef]                — 1 or more; see §5
terms           [Term]                     — the declared vocabulary of this statement
atoms           [Atom]                     — 0 or more; coverage is 0.0 when empty, which is never a pass
conflicts_policy {default, lex_specialis}   — how incompatible relations are to be resolved; see §7
escapes         [Escape]                   — declared non-closure; checked against computed escapes
```

`CorpusRef`:

```
id            string      — short handle used by anchors
title         string      — human name of the source
revision      string      — YYYY-MM-DD of the text edition used
text          string      — path, relative to repository root, of the pinned text
text_sha256   string      — sha256 of the file's bytes, lowercase hex
```

`Term`:

```
name    string            — referenced by atoms as bearer / counterparty / action.object
def     string            — one sentence, in the statement's own words
status  "closed" | "open" — "open" means: this term is not defined precisely enough to be checked
```

`Atom`:

```
id            string      — unique within the statement
relation      string      — one of the eight names in §4
bearer        string      — name from terms[]
counterparty  string|null — name from terms[]; required unless the relation is absolute (§4.3)
action        {verb, object, open}
conditions    [string]    — free-text conditions; not interpreted in v0.1, listed in the report
temporal      {from, until}   — YYYY-MM-DD; until=null means "no declared end"
anchor        {corpus, article, span, note}
```

`Escape`:

```
atom    string    — atom id
reason  string    — a code from §10
detail  string    — why, in one sentence
```

Unknown fields are allowed and ignored; a checker must not fail on them. A statement containing a field this
document does not define is not thereby invalid, but the extra field carries no meaning.

## §3 Canonical form and identity

A verdict is only reproducible if the statement has a byte form that does not depend on the editor. The
canonical form is:

1. UTF-8, no BOM, LF line endings.
2. The JSON object serialised with keys sorted lexicographically at every depth, no insignificant
   whitespace (`{"a":1,"b":[2,3]}`), non-ASCII characters emitted literally (not `\uXXXX`).
3. No floating-point numbers anywhere. Dates are strings. A number that must be fractional is a bug in the
   statement; coverage and ratios are computed by the checker, never stored.
4. Arrays keep their given order; ordering of `terms`, `atoms`, `corpus`, `escapes` is not canonicalised,
   so two semantically equal statements may have different hashes. That is intended: identity is over the
   bytes an author signed, not over an equivalence class.

`statement_sha256` in the report is sha256 of the canonical bytes. `C0_CANON` asserts that computing it
twice gives the same value; it cannot assert that two authors wrote the same thing.

## §4 The Hohfeld layer

### §4.1 Eight positions, two squares

Legal positions are not "rights and duties". They are four pairs of correlatives:

| Position | Correlative | Opposite |
|---|---|---|
| `right` | `duty` | `privilege` |
| `duty` | `right` | `no-right` |
| `privilege` | `no-right` | `right` |
| `no-right` | `privilege` | `duty` |
| `power` | `liability` | `immunity` |
| `liability` | `power` | `disability` |
| `immunity` | `disability` | `power` |
| `disability` | `immunity` | `liability` |

*Correlatives* are two ways of describing one relation from its two ends: if A has a `right` that B deliver,
B has a `duty` to deliver to A. *Opposites* cannot both hold of the same bearer with respect to the same
action: A cannot be both `privileged` and under a `right`-correlative duty not to do the thing.

This is the whole reason v0.1 can check anything useful without a prover. Modalities that are informally
called "permission" and "obligation" have a precise place here, and the contradictions between them are
combinatorial, not semantic.

### §4.2 What the checker asserts

- every `relation` is one of the eight names (`S3_UNKNOWN_RELATION`);
- `counterparty` is present when the relation is relative (`S3_MISSING_COUNTERPARTY`);
- no two atoms assert *opposite* relations for the same `(bearer, action.verb, action.object,
  counterparty)` tuple over overlapping time (`S3_OPPOSITE_CONFLICT`).

### §4.3 What it does not assert

- It does not derive correlatives for you. An atom's correlative need not be written; if it is written, the
  pair is checked for agreement, and a mismatch is `S6_CONFLICT`.
- It does not model degree, conditionality of duties in any formal sense, remedies, or exceptions. `conditions`
  is prose and stays prose in v0.1; a condition that matters must be encoded as another atom or as another
  statement.
- Absolute relations (`immunity`, `disability`, `power` against the world) may omit `counterparty` and are
  then checked only for opposites.

## §5 Anchoring

An atom is anchored when all four hold:

1. `anchor.corpus` names a `CorpusRef` in the statement (`S2_NO_CORPUS` otherwise);
2. the file at `CorpusRef.text` hashes to `CorpusRef.text_sha256` (`S2_HASH_MISMATCH` otherwise);
3. `anchor.span` occurs in that file (`S2_SPAN_NOT_FOUND` otherwise);
4. it occurs **exactly once** (`S2_SPAN_AMBIGUOUS` otherwise).

Rule 4 is the load-bearing one. A span that appears twice anchors nothing: a reader cannot tell which
occurrence the author meant, so a later amendment to one of them silently re-points the citation. Ambiguity
is a defect of the anchor, so it is a refusal, not a warning.

`anchor.article` is for humans and is not checked against anything in v0.1. It exists so that a refusal report
can name the provision a lawyer would look at.

The corpus is pinned *by content*, never by URL. A URL is provenance metadata; the hash is the identity. A
statement whose corpus file changes is a different statement, and its old verdict is void.

## §6 Time

`temporal.from` is the first day the asserted position holds; `until` the last, or `null`. Two rules:

- `from <= until` and the interval is non-empty (`S5_EMPTY_INTERVAL`).
- Two atoms conflict only if their intervals **overlap**. A duty that ended before a privilege began is not
  a contradiction.

Not modelled in v0.1: retroactivity, entry into force distinct from adoption, transitional provisions,
suspension. A statement that needs them must say so in `conditions` prose and cannot reach
`CHECKED_ANCHORED` on that atom — this is a known gap, listed in §11.

## §7 Conflict policy

v0.1 detects incompatibility; it does not resolve it by default. The default is authoritative in law
(no norm silently overrides another) and honest in software (a checker that guesses is worse than one that
refuses).

**What counts as a conflict here.** Two atoms conflict when they carry relations that are *correlatives* of
each other on the same **ordered** tuple `(bearer, action.verb, action.object, counterparty)` over
overlapping time. That shape means the author wrote the correlative on the wrong side: if A holds a `right`
against B that B delivers, the correlative `duty` belongs to **B toward A**, and writing it as A's duty toward
B says something else entirely. Opposite relations on one tuple are a harder defect and are handled by S3
(`S3_OPPOSITE_CONFLICT`), which no policy can cure; one defect is never reported under two codes.

**Known false positive.** Two genuine mutual obligations about the *same* action — A owes B delivery of the
goods, B owes A delivery of the same goods — also land on one tuple and are reported. v0.1 has no vocabulary
for "these are two independent debts", so it reports and the author must distinguish the actions or split the
statement. This is a limitation of the model, not of the corpus, and it is the price of keeping the check
combinatorial.

**Policies.**

- `conflicts_policy.default = "report"` — every conflict is `S6_CONFLICT` and the verdict is `REFUSED`.
- `conflicts_policy.default = "lex_specialis"` — a conflict is permitted only when
  `conflicts_policy.lex_specialis` names the prevailing atom over the other, in either direction; otherwise
  `S6_UNRESOLVED_CONFLICT`.
- `conflicts_policy.default = "lex_posterior"` — the later start prevails; a conflict between atoms that start
  on the same day cannot be ordered and is `S6_UNRESOLVED_CONFLICT`.

Declaring a policy is an assertion by the author that the corpus supports it; the checker verifies that the
assertion is *complete* — every conflict accounted for — not that it is *correct*.

## §8 Coverage and escapes

An atom is **closed** when all of the following hold:

1. `bearer` resolves to a term with `status: "closed"`;
2. `counterparty`, when present, resolves to a term with `status: "closed"`;
3. `action.object`, when present, resolves to a term with `status: "closed"`;
4. `action.open` is `false`;
5. the atom is anchored (§5).

```
coverage = |closed atoms| / |all atoms in the statement|        (0.0 when there are no atoms)
```

The denominator is **every entry of `atoms[]` that is an object**, including atoms that `S1_SCHEMA` rejected. A
malformed atom cannot be closed, so it lowers coverage rather than disappearing from the arithmetic. This is
deliberate: a coverage number that improves when an atom is malformed would be a number worth lying with. An
entry that is not an object at all (a string, a number) is not an atom, produces `S1_SCHEMA`, and is outside
the denominator.

An atom that is not closed produces an `OPEN_TERM` finding whose detail names the specific reason — an
undefined reference, an open term, `action.open`, or a failed anchor. The checker then compares the set of
not-closed atoms against the declared `escapes[]`:

- a not-closed atom that `escapes[]` does not list → `S4_UNDECLARED_ESCAPE` (a refusal);
- an atom that `escapes[]` lists although the checker computed it as closed → `S4_STALE_ESCAPE` (a refusal).

Both are refusals, and for the same reason seen from two sides: without this pair, coverage is a number the
author reports about himself. The `reason` field inside a declared escape is written for the reader and may
name the specific cause (`S2_SPAN_NOT_FOUND`, `OPEN_TERM`, …); the checker verifies **membership**, not the
wording.

Coverage is a number about the statement, not about the law. 100 % coverage of a clause you mis-encoded is
100 % coverage of a mis-encoding. §9 exists to keep that sentence attached to every verdict.

## §9 Verdicts

Exactly three values, in ascending strength:

| Verdict | Requires | Means |
|---|---|---|
| `REFUSED` | any check failed | the statement does not survive checking; read the codes |
| `CHECKED` | no failed check, but ≥1 escape or coverage < threshold | what is encoded is consistent and anchored where anchored; the encoding is incomplete |
| `CHECKED_ANCHORED` | no failed check, no escapes, coverage ≥ threshold | every atom is closed and anchored against pinned text |

The default threshold is **0.8** and is a flag, not a constant of nature: `--coverage-threshold`. A verdict
produced with a non-default threshold must be reported with that threshold, otherwise it is not reproducible.

Every report — including `CHECKED_ANCHORED` — carries:

```
"not_claimed": ["legal validity",
                "completeness of the encoded law",
                "correctness of the corpus outside the pinned revision"]
```

This is not decoration. A reader who quotes the verdict without the `not_claimed` list is quoting a different
statement than the one the tool made.

## §10 Refusal codes

Closed vocabulary, one meaning each. The full catalogue with causes and remedies is
[`docs/11-REFUSAL-CODES.md`](11-REFUSAL-CODES.md). Groups:

- `C0_CANON` — canonicalisation is not reproducible.
- `S1_SCHEMA` — the document is not a statement.
- `S2_*` — anchoring failed.
- `S3_*` — the Hohfeld layer is malformed.
- `S4_*` — reference closure or escape accounting failed.
- `S5_*` — time is malformed.
- `S6_*` — incompatible positions, unresolved.
- `S7_COVERAGE` / `THIN_COVERAGE` — the encoding is too thin for the strength of the verdict requested.

A new code requires: a defect that no existing code names, a test that produces it, and an entry in the
catalogue. Codes are never renumbered and never reused.

## §11 What v0.1 does not have

Written down so that nobody discovers it as a surprise:

1. **No statute parser.** Statements are written by hand or proposed by a model and then checked. Nothing
   in this repository reads prose law.
2. **No entailment.** The checker does not prove that an atom follows from a provision. It proves that the
   atom points at a span which exists, and that the set of atoms is internally coherent. "The law requires
   X" is never a v0.1 output; "atom a1 is anchored at ——— in this revision" is.
3. **No defeasibility.** Exceptions, `unless` clauses, contrary-to-duty structures. `conditions` is prose.
4. **No cross-statement reasoning.** Each statement is checked alone. A contract consisting of twelve
   statements is not checked as a set.
5. **No identity of terms across statements.** `поставщик` in two statements is two terms that happen to be
   spelled the same.
6. **No jurisdiction model.** `jurisdiction` is a label, not a semantics.
7. **No proof object.** The report is a record, not a certificate a third party can re-derive without the
   repository. A signed, self-contained certificate is a v1 candidate, not a promise.

## §12 Conformance

An implementation may call itself *LexSpec v0.1 conformant* if it:

1. reads `schemas/statement-0.1.json` documents;
2. produces all codes in §10 with the meanings given in the catalogue, for the inputs that cause them;
3. emits the canonical hash of §3 and the `not_claimed` list of §9 in every report;
4. refuses rather than warns on every `S2_*` condition;
5. passes `tests/run_tests.py` unchanged, or publishes a table of the checks it fails.

Conformance is a claim about behaviour on a test corpus, not about legal knowledge. An implementation that
passes the tests and knows no law is conformant, and that is fine.
