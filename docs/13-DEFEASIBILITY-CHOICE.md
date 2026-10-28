# 13 — Defeat: the blocking sub-problem, and the best available answer

Status: **decision-ready, not decided.** Per [ADR-0004](../lab/decisions/ADR-0004-correctness-not-novelty.md) the
question is not whether we can invent a construct, but which published one is best and where it stops.

Why this is blocking rather than a v0.3 nicety: the first real article ever encoded in this repository —
GDPR Art. 17 — could not be represented. Art. 17(3) says "Paragraphs 1 and 2 **shall not apply** to the extent
that processing is necessary…". That is not a legal position; it is a *defeat*. Without it, coverage reported
0.750 honestly and the article's operative exceptions were simply absent
([`lab/cost.md`](../lab/cost.md), measurement 1). Every second article in the corpus will hit the same wall.

---

## §1 What must be representable, stated as tests

A construct is adequate only if it passes all five. Each is a test, not a wish:

| # | Requirement | The case that produces it |
|---|---|---|
| **D1** | A position can be **defeated** by another position, without the defeater being a position of the same kind | Art. 17(3) defeats the duty in 17(1) and is itself a permission to keep processing |
| **D2** | The defeat is **conditional**: it holds only "to the extent that" its conditions hold | the same duty revives when none of the (a)–(e) grounds applies |
| **D3** | When two defeasible grounds are **incomparable**, the result is preserved as a conflict rather than resolved by a coin flip | two of (a)–(e) can both apply, and the Article does not order them |
| **D4** | The result must **distinguish "not defeated" from "unknown"** — silence is not negation | a missing fact about consent withdrawal is not evidence that consent was not withdrawn |
| **D5** | The construct must stay **decidable and cheap** at our scale: no theorem prover in the runtime path, no exponential blow-up on a clause with a dozen atoms | a checker that takes minutes on one clause will not be used |

---

## §2 Candidates, as verified today

| Candidate | What it actually provides | Where it stops for us |
|---|---|---|
| **Arxo Law — four-valued support** (`TRUE_ONLY` / `FALSE_ONLY` / `BOTH` / `NEITHER`), "silence is not negation", with a theorem that incomparable defeasible grounds both survive | D3 and D4 in the result itself; competing norms are preserved as `BOTH` in the evaluation document | defeasibility rules exist, but the *shape* of a defeat obligation is not published in the material we read; the engine is not in the open parity repository, so only the idea is adoptable today |
| **LegalLean — applicability-aware defeat resolution** | filters applicable rules, resolves defeats by priority, returns a `FormalisationBoundary` result; **six solver-property theorems** (monotonicity, determinism, soundness) | priority must be supplied; the eight-factor IR is theirs, and moving our atoms into it is a rewrite, not an adoption |
| **Catala — prioritized default calculus** | each variable defined once, with a tree of exceptions whose priority is static from the syntax tree; two equal-priority exceptions ⇒ **error**, no value | the "conflict = runtime error" behaviour is wrong for us: a disputed clause must produce a preserved conflict, not a crash (contradicts D3) |
| **LegalRuleML — `Override` / `Defeater`** | a standard vocabulary for defeat and override, with temporal characteristics | a vocabulary, not a decision procedure; adopting it means implementing our own engine behind it, which is the work we are trying to avoid |
| **ODRL `conflict` ∈ {perm, prohibit, invalid}, default `invalid`** | three global resolution strategies, fail-closed default | far too coarse: it resolves a whole policy, while Art. 17(3) resolves one position to the extent of its conditions (fails D2) |
| **XACML combining algorithms** (deny-overrides, permit-overrides, first-applicable, only-one-applicable) | explicit, testable conflict semantics; `Indeterminate` is a first-class outcome | written for access decisions, not for positions that revive when a condition lapses; the algorithms are global to a policy set |
| **ASP / clingo defaults** (and eFLINT on clingo) | default negation with stable models; several admissible answers rather than one | D3 and D4 fit well; D5 is the risk — grounding cost, and a solver in the runtime path is exactly what our certificate story cannot carry today |

---

## §3 Proposed decision (conditional on §4)

**Adopt two ideas and build the smallest construct that carries them:**

1. **From Arxo: the four-valued *result*.** A position is `established`, `refuted`, `both`, or `neither`. This is
   a property of the *report*, not of the atom, and it costs one field.
2. **From LegalLean: defeat as an applicability relation with a declared priority**, not as a rewriting of the
   positions.

Concretely, a minimal spec addition — the shape matters more than the names:

```
atom.excepts: [atom_id]          // this position, when its conditions hold, defeats those positions
atom.priority: integer           // declared, never inferred; the source of a priority must be a citation
report.position_status: {atom_id → established | refuted | both | neither}
```

Rejected on the evidence above: Catala's error-on-conflict (violates D3), ODRL's policy-level `invalid` (violates
D2), and any design that runs an ASP solver inside the checker (violates D5 and the certificate's reproducibility).

**What this deliberately does not do:** it does not compute which exceptions apply. It records that a defeat
exists, which position it defeats, and what status each position reached given the facts that were asserted —
and it refuses when a fact needed to decide is absent (D4). Deciding *whether* "processing is necessary for the
establishment of legal claims" holds remains a human or model judgement, recorded as an asserted fact.

---

## §4 What must be read before this is committed

Per ADR-0004 the comparison work is a prerequisite, not an optional extra:

1. **LegalLean's solver**: the actual treatment of priority, and whether its six theorems state the properties we
   need (monotonicity, determinism, soundness) or their own variants. MIT-licensed, so readable.
2. **Arxo's engine**: is it open at all? If only the parity models are public, the four-valued *idea* is
   adoptable but the defeat mechanics are not, and §3's second half must be sourced elsewhere.
3. **Saka's survival certificate** (arXiv 2609.01741): not about defeat, but its willingness to publish a
   retracted claim and a failure rate is the model for how we should report the first version of this construct.

Until those three are read, §3 is a proposal with a stated basis and no authority.

---

## §5 The test that settles it

The construct is accepted if and only if it reproduces GDPR Art. 17 without hand-written exceptions:

| Scenario | Required outcome |
|---|---|
| grounds apply, no 17(3) fact asserted | erasure duty `established`; carve-out `neither` |
| grounds apply, "necessary for legal claims" asserted | duty `both` — the conflict is preserved, not resolved |
| grounds apply, carve-out asserted with a fact that is missing | duty `neither`, and the report names the missing fact |
| grounds do not apply | duty `refuted`; carve-out irrelevant |
| no grounds and no facts at all | everything `neither`; the report refuses to conclude |

If the construct cannot produce this table, it is not adequate, whatever its provenance. If it can, it is adopted
regardless of whose it is — and `docs/10` gains a section, not a claim.
