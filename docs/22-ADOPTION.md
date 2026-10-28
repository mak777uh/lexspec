# 21 — Stage 0: adopting the field vocabulary instead of inventing it

Status: **decision document**, no code, no schema change yet. It answers one question: which of our fields survive
contact with two published schemas, which must be replaced, and which are genuinely ours.

Sources read for this document (both verified in this session):

- **CAP-RRS** — [`draft-sato-soos-cap-rrs-03`](https://datatracker.ietf.org/doc/draft-sato-soos-cap-rrs/),
  Tom Sato, IETF individual draft, 5 Sep 2026. §4 Regulation Record schema, §5 Cedar Compilation Profile,
  §9 Law Reference Interface (LRI), §11 operational requirements.
- **Symboleo** — *Towards a Specification Language for Legal Contracts* (RE 2020); *Specification and analysis of
  legal contracts with Symboleo* (SoSyM 2022). Contract ontology with legal positions, obligations, powers,
  events, lifecycle statecharts.

---

## §1 Field mapping: our anchor vs their LRI

CAP-RRS requires, for every non-resource record, an `authority_source` block with `law_id`, `article_ref`,
`version_identifier`, `retrieved_at`, `amendment_detection_endpoint`, optional `interpretation_endpoint`, and an
`endorsement` sub-block (`authority_id`, `endorsed_at`, `endorsement_scope`, `resolution_basis`,
`resolution_instrument_id`, `co_endorsement_*`, `endorsement_claim` as a signed JWT).

| Ours | Theirs | Verdict |
|---|---|---|
| `corpus[].id` | `law_id` (LRI-1: unique within a jurisdiction profile) | **adopt**: ours is a local handle with no jurisdiction discipline |
| `anchor.article` — free prose | `article_ref` — **must be resolvable against the official structure to a unique operative clause** (LRI-2) | **adopt, and this is a correction**: our prose field is uncheckable; theirs is a testable requirement |
| `anchor.span` + uniqueness | *no equivalent* | **ours**: LRI-2 stops at "unique operative clause", not at a byte range |
| `corpus[].revision` — a date we choose | `version_identifier` — **must be derivable from the amendment history** (LRI-3) | **adopt**: our date is an assertion, theirs is a derivation |
| `corpus[].text_sha256` | *no equivalent* — they carry `retrieved_at` only | **ours + adopt `retrieved_at`**: digest without a retrieval time cannot distinguish "same bytes, re-fetched" from "same bytes, cached since 2019" |
| *nothing* | `amendment_detection_endpoint` (LRI-4) | **adopt**: our certificate has no staleness signal at all — a verdict silently ages |
| *nothing* | `interpretation_endpoint`, and `INTERPRETATION_SUPERSEDED` when interpretation changes without the text changing | **adopt the concept**: this is the case our `S2_TEXT_MISMATCH` idea missed — the bytes can be identical while the operative meaning changes |
| *nothing* | `endorsement` (`authority_id`, `endorsed_at`, `resolution_basis` ∈ statute_clear / interpretive_ruling / internal_conflict_resolution / cross_statute_coordination, signed claim) | **adopt the shape**: this is what a handover "legal basis" ([ADR-0007](../lab/decisions/ADR-0007-substrate-independence.md)) needs — an endorsement with a *legal character*, not a sentence |
| `S1_…`–`S7_…` codes | CAP tiers (0-A…3) + structured DENY reason codes referencing the fired record | **both, separately**: tiers are a political classification of obligations; our codes are defects of an encoding. Neither maps onto the other |
| coverage, escapes | *no equivalent* | **ours** |

**Compilation (§5.2) — the one thing we must copy exactly:** every emitted Cedar policy carries an **annotation
block** with `record_id`, `tier`, territories, `effective_date`, `record_version`, "which enable the GEC to produce
structured DENY reason codes referencing the specific Regulation Record that fired". Plus §5.4: a conforming
compiler MUST reject a record with an invalid or expired certification signature, and MUST surface
operator-priority conflicts as **compile-time errors**.

That is our L6 in four sentences, and it is better specified than ours: our "every rule carries its atom id" is
a wish; theirs is a conformance requirement with a named annotation block and a reason-code path.

---

## §2 What this changes in our schema (planned, not applied)

1. `anchor` becomes **four** parts, not three: `law_id` (profile-scoped), `article_ref` (resolvable, unique
   operative clause), `version_identifier` (**derivable from amendment history**), `retrieved_at`, plus our
   `span` and `text_sha256` as the sixth and seventh.
2. `corpus[]` gains `amendment_detection_endpoint` and optional `interpretation_endpoint`, or the statement
   declares explicitly that it has none — with the consequence that its certificate can never claim currency.
3. A new top-level `endorsement` block: who endorsed, when, with what legal character, signed. This replaces the
   free-text `basis` we had planned.
4. `compilation` becomes a required report section: for each emitted rule, `record_id`/atom id, version, and the
   reason code path — the CAP-RRS annotation block, in our vocabulary.
5. Our refusal vocabulary gains a **staleness** dimension it never had: a verdict whose endorsement predates a
   detected amendment is not `CHECKED`, it is `SUSPENDED` — and the honest name for that state is the one CAP-RRS
   already uses.

---

## §3 What stays ours, stated so it can be attacked

| Ours | Why it is not already covered | How it can be killed |
|---|---|---|
| **Byte-level span uniqueness** | LRI-2 requires a resolvable reference to a unique operative clause; it does not require the *quoted text* to occur uniquely. Our added value is that a paraphrase cannot be smuggled in, and that a re-flowed quote fails loudly | if real corpora make byte-uniqueness impossible (line wrapping already costs us 43 % of attempts), the rule is over-strict and must be weakend to "unique within a declared context window" |
| **Hohfeld as a pairing type** | CAP-RRS classifies obligations by *tier* (who may override), not by legal position; Symboleo has positions but (per the answers) not correlative-pair checking | if Symboleo already enforces correlatives, this is adoption, not addition |
| **Coverage and escapes as numbers** | neither source reports how much of a provision was modelled | if a reader cannot act on the residue report, the number is decoration |

---

## §4 Decision

**Adopt**: the LRI field set, the endorsement block with a legal-character vocabulary, the retrieval timestamp,
the staleness endpoints, the annotation block for compiled rules, the compile-time rejection of uncertified
records, and the SUSPENDED state.

**Keep**: span uniqueness, Hohfeld pairing, coverage/escapes, the refusal catalogue.

**Do not do yet**: change the schema. Stage 0's output is this document plus the consistency guard
([`lab/check-spec.py`](../lab/check-spec.py)); the schema change lands with tests, per ADR-0001, and only after
the guard proves the current documents are mutually consistent — because extending an inconsistent spec is how a
project acquires two truths.
