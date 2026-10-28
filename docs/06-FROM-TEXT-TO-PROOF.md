# 06 — From legal text to a proof obligation: twelve hypotheses

Status: hypothesis register, not spec and not a plan. Authority stays with
[`00-CHARTER.md`](00-CHARTER.md) and [`10-SPEC-v0.1.md`](10-SPEC-v0.1.md). Every hypothesis here is a
candidate, with the test that would kill it. Nothing in this file is claimed to work.

Written after reading three primary sources on 2026-10-28: the PutnamBench proof run
([lessons](05-HARNESS-LESSONS.md)), the verification landscape ([survey](04-SEMANTIC-VS-FORMAL.md)), and the
`nearai/ironclaw` agent OS, whose capability model turned out to contain four structures that transfer
almost unchanged.

---

## §1 The question, and the only three honest answers

"Make legal language formally provable" has exactly one honest reading, and it is narrower than the phrase
suggests. There are three different things one could prove, and they are not interchangeable:

| Target | Statement shape | Status |
|---|---|---|
| **T1 — properties of the encoding** | "in this statement, no atom is simultaneously permitted and forbidden; every atom is anchored; coverage is k" | **decidable, cheap, buildable now** |
| **T2 — properties of the checker** | "for every statement admitted by the schema, if the checker reports no conflict then none exists under the Hohfeld algebra" | **provable in Lean/Isabelle, and this is the interesting target** |
| **T3 — properties of the world** | "this clause is enforceable / lawful / survives assignment" | **not provable, by anyone, ever** — it is a prediction about institutions |

Legal-tech products almost always advertise T3, demonstrate T1, and never mention T2. The program in this
file is the reverse: do T1 mechanically, **prove T2**, and refuse T3 in the artifact itself (the
`not_claimed` field already does this at the level of the report).

The insight that makes T2 worth the effort: T2 is provable **once** and then covers every clause encoded
forever. T1 must be re-run per clause; T2 is amortised. This is the same economics that makes CompCert worth
3 person-years — the theorem is about the compiler, not about a program.

---

## §2 Twelve hypotheses

Format: **claim → why it is plausible → what to build → the test that kills it.** Numbering is permanent;
hypotheses are never renumbered, only superseded by a dated entry.

### H1 — Anchor-first, proof-last

**Claim.** Formalisation effort spent on an unanchored atom is spent on the wrong proposition. The gate must
run *before* any proving, not after.
**Why plausible.** In the PutnamBench run two of 672 formalisations were not what they claimed: one false
(`1974_b1`, degenerate configurations satisfied the predicate), one faithful to nothing (`2013_a5`, "area"
was the Busemann–Hausdorff measure because of the sup metric on `Fin 3 → ℝ`). Both were *proved*; neither was
detectable by any proof-side check.
**Build.** The v0.1 gate already does this. The addition is a rule: no prover may be pointed at a statement
containing an atom that has not passed `S2_*`.
**Kill test.** Take ten real clauses. Encode each twice — once anchored first, once formalised from the
natural-language reading and anchored afterwards. If the two encodings differ in fewer than 10 % of atoms, the
gate is not buying enough to justify its friction.

### H2 — Shallow embedding beats deep

**Claim.** Legal statements should be encoded as *data* with a small separately specified semantics, and the
proofs should be about that semantics — not as direct Lean propositions about the world.
**Why plausible.** A deep embedding of "the supplier shall deliver" forces a model of delivery, goods,
time and non-performance, i.e. the open texture of private law, and every such model is a contested
interpretation dressed as a definition. L4 and Catala both avoid this by staying at the level of rules and
computations; neither claims proofs about law.
**Build.** `lean/LexSpec/Basic.lean`: the eight Hohfeld positions as an inductive type, the correlative and
opposite maps as functions, intervals as `Icc`/`Ico` over `Date`, and atoms as a structure. Then a relation
`Conflicts : Atom → Atom → Prop`.
**Kill test.** If encoding the algebra needs more than ~400 lines of Lean before the first theorem, the
shallow embedding is not shallow enough — the legal vocabulary is leaking into the meta-level.

### H3 — Prove the checker, not the clause (the Cedar move)

**Claim.** The provable artifact is the detector's correctness: *soundness* (if it reports no conflict, none
exists) and *completeness* (if a conflict exists on the declared fragment, it is reported).
**Why plausible.** Cedar did exactly this for a policy language: a sound and complete logical encoding,
modelled and proved in Lean, enabling automated reasoning about policies — including that refactoring does not
change the authorised permission set. That is the same shape of theorem LexSpec needs, one domain over.
**Build.** Theorem `conflict_free_sound : (findConflicts s = []) → ∀ a b ∈ s, ¬ Conflicts a b` and its
converse on the fragment the schema admits. Plus: determinism of canonicalisation, and monotonicity of
coverage under atom addition.
**Kill test.** If the completeness statement cannot be written without quantifying over "all possible
intended meanings", it means the check is only sound — which is still useful, but then the spec must say
"sound, incomplete" and the verdict wording must change.

### H4 — Closed-world citation (capability analogue)

**Claim.** A statement may reference only terms, corpora and jurisdictions declared in its own header.
Undeclared reliance is a refusal, and this — not pattern detection — is what makes smuggling a norm
impossible.
**Why plausible.** IronClaw's tools reach only hosts named in `network.allowed_hosts`; the sandbox cannot
bypass the proxy. That is a *positive* declaration enforced at a boundary, and it holds against an adversary
who writes novel text, whereas a denylist does not (see H10).
**Build.** `S4_UNDECLARED_RELIANCE`: any `bearer`, `counterparty`, `action.object`, `anchor.corpus` absent
from `terms[]`/`corpus[]` is refused — v0.1 does this for terms (`S4_UNDEFINED_REF`) but not for the concept
the term stands for.
**Kill test.** Encode ten clauses with the closed-world rule and count how often a *legitimate* citation has
to be added to the header. If the median is above ~5 additions per clause, the ontology is being rebuilt by
hand and the rule costs more than it buys.

### H5 — Authority injection at the boundary

**Claim.** The atom must never contain the text of the norm it relies on; it contains a pointer, and the
checker injects the text into the obligation. Paraphrase then becomes structurally impossible rather than
discouraged.
**Why plausible.** IronClaw's tools never see credentials: they declare `{secret_name, location,
host_patterns}` and a proxy at the network boundary injects the secret. The container cannot leak what it
never held. The analogous legal failure — an atom whose span is real but whose wording silently re-reads the
norm — is exactly what `S2_SPAN_AMBIGUOUS` catches only partially today.
**Build.** A checker mode that resolves each atom's span, substitutes the actual bytes into the report, and
refuses if the atom's `action`/`term` vocabulary cannot be matched against the span by a declared extraction
rule (even a crude one: every closed term must appear in the span, or be declared as an inferential
addition).
**Kill test.** If the "every closed term appears in the span" rule refuses more than half of a hand-encoded
corpus, then legal drafting routinely relies on text that is not co-located with the norm, and the rule must
be weakened to a declared, reviewable exception list.

### H6 — A severity ladder, not a binary

**Claim.** Refusal codes need severity and remedy, so a reader knows what to do next; the verdict ladder must
remain ordered by anchoring and closure only.
**Why plausible.** IronClaw's policy engine has Block / Warn / Review / Sanitize — four responses, because
one binary "unsafe" produces alert fatigue and gets turned off. LexSpec already has the beginning of this
(refusal vs escape vs finding) and the charter's falsifier F4 says a refusal a reader cannot act on is a bug.
**Build.** Every code row gains `severity ∈ {refuse, escape, warn}` and `remedy`. The verdict ignores
severity; severity drives the report's ordering and the human summary.
**Kill test.** Show the report to two people who did not write it; if either asks "so what do I do", the
ladder is decorative.

### H7 — Cost per closed atom is the unit of account

**Claim.** The viability question is minutes and dollars per **closed** atom, with failed attempts counted.
**Why plausible.** The PutnamBench submission is quoteable *because* it publishes `costs.tsv` — 724 attempts
for 672 problems, failures included, mean $0.17 / median $0.04 / max $11.18. A result without the failure
distribution is a press release.
**Build.** `lab/cost.md` as specified in [`20-METHOD.md`](20-METHOD.md) §6, with an added column for
attempts. A `tools/cost_report.py` that computes median/mean/max from it.
**Kill test.** If the median exceeds ~45 minutes per closed atom for ordinary contract language, the encoding
approach does not pay for itself against a careful human checklist — charter falsifier F3 — and the project
must move up the abstraction (fewer, coarser atoms) rather than pretend the number is acceptable.

### H8 — The prover seam is one-way

**Claim.** A prover may add evidence beside a verdict and may never raise it.
**Why plausible.** `REFUSED → CHECKED → CHECKED_ANCHORED` is ordered by anchoring and closure; no theorem can
close an open term or find a span. If a proof could raise a verdict, the project would be selling rung (d)
confidence for rung (a) work — the characteristic failure named in
[`04-SEMANTIC-VS-FORMAL.md`](04-SEMANTIC-VS-FORMAL.md) §5.
**Build.** Structural: `verdict` is computed by a function that never takes prover output as an argument;
prover results land in a separate `evidence` field.
**Kill test.** Code review: if any code path lets `evidence` influence `verdict`, the hypothesis is dead. This
is a five-line test, and it should be a unit test.

### H9 — Temporal algebra before defeasibility

**Claim.** Do intervals and declared conflict policies first; defer exceptions (`unless`, `subject to`),
because non-monotonicity destroys decidability and with it the value of the mechanical check.
**Why plausible.** Contrary-to-duty structures (Chisholm's paradox) are the classic reason deontic logics
stop being computable; Catala needed a prioritised default logic with static priorities from the syntax tree,
and it *errors out* on unresolvable conflicts rather than guessing.
**Build.** v0.1 already has intervals and `conflicts_policy`. The addition is an explicit `exception` field
that is **not interpreted** but *counted*: a statement with exceptions cannot exceed coverage k unless every
exception is itself encoded as an atom.
**Kill test.** Encode ten clauses that contain "unless"/"except"/"subject to". If more than half cannot be
expressed as atoms plus a declared policy, the model is missing a construct and the honest output is a new
refusal code, not a heuristic.

### H10 — Denylists do not survive legal adversaries

**Claim.** Detecting bad clauses by pattern ("unfair", "void", "may at its sole discretion") is the same
engineering mistake as regex-based prompt-injection defence: the adversary controls the input text.
**Why plausible.** IronClaw layers pattern detection *and* capability restriction *and* credential
non-exposure. The pattern layer is the weakest of the three and is kept only because it is cheap; the property
that actually holds comes from declarations enforced at boundaries.
**Build.** Nothing to build — a rule to keep: every check in LexSpec must be either a positive declaration
enforced structurally, or a decidable property of the encoding. No "suspicious phrase" lists, ever, in the
verdict path.
**Kill test.** Write a clause that is structurally identical to an egregious one but uses no flagged words; if
the tool's output changes, a denylist has crept in.

### H11 — Term identity must be content-addressed

**Claim.** Before clauses can be checked *together*, a term must be an object with a definition that has a
hash, so `поставщик` in two statements is the same term iff the definition bytes match.
**Why plausible.** v0.1 explicitly refuses cross-statement reasoning, and the reason is that string equality
of term names is not identity. Canonical hashing (spec §3) already gives the mechanism; it is simply not
applied to terms yet.
**Build.** `term_id = sha256(canonical(name, def))`, carried in the report, with a statement-level
`imports: [term_id]` field to opt in.
**Kill test.** Encode the same clause twice with a one-word change in one definition. If the tool does not
surface the divergence, the identity layer is not doing work.

### H12 — The certificate is the deliverable

**Claim.** The output that matters is a small, offline-checkable record: statement hash, encoding version,
every corpus hash, checker version, verdict, findings, `not_claimed`. Everything else is convenience.
**Why plausible.** CompCert, seL4, IronFleet and the PutnamBench entry all publish their trusted base, because
a claim whose trusted base is unstated is unauditable. IronClaw's audit log is the same instinct at a
different scale.
**Build.** `lexspec report --certificate` emitting JSON that a third party can re-check with the repo and no
network. The checker must be able to *replay* a certificate and reproduce the verdict.
**Kill test.** Hand the certificate and the repo to someone who has never seen the project. If they cannot
reproduce the verdict, the certificate is documentation, not evidence.

---

## §3 What would falsify the program as a whole

Not individual hypotheses — the whole idea:

1. **Two independent encoders of one clause disagree on more than 20 % of atoms.** Then "the encoding" is not
   an artifact, it is an opinion, and coverage numbers over it are meaningless (charter F2).
2. **Median cost per closed atom exceeds the value of the check.** Then the technique is a research toy
   (charter F3).
3. **A statement passes `CHECKED_ANCHORED` and a competent lawyer finds a defect in the span's plain
   reading.** Then the tool is producing false comfort, which is worse than producing nothing.
4. **The T2 theorems turn out to be trivial restatements** of the code (e.g. proving that the function that
   returns `[]` when there are no atoms returns `[]`). Then rung (d) was decoration and should be dropped
   rather than advertised.

Each of these is cheap. Each should be run before any claim of a v1.

## §4 What this costs, honestly

T2 is the only part of this document that requires a proof assistant, and it is the smallest part: the algebra
is eight positions with two maps, intervals over dates, and a detector that is a bounded pairwise scan. The
hard part is not the proof — it is H1, H4, H5 and H11, which are engineering on text, and H7, which is a
measurement campaign.

Stated as an ordering, because doing them out of order wastes the effort:

1. H1 + H8 (already true in v0.1) — the gate and the one-way seam.
2. H11 + H12 — term identity and the certificate; both are small and both unlock everything else.
3. H3 — prove the detector. This is the publication-grade artifact and the reason to use Lean at all.
4. H7 — measure cost per closed atom on real clauses; publish the failures.
5. H4 + H5 — the closed-world and boundary-injection rules, which are where the encoding stops being
   paraphrased and starts being cited.
6. H2, H6, H9 — refinements, in that order.
7. H10 — never; it is a standing prohibition, not a task.

## §5 The sentence this whole file has to earn

> Within a declared encoding of a pinned corpus, no clause can be satisfied by a fact pattern that violates an
> anchored norm — and the detector that says so is proved sound, so the guarantee is about the checker rather
> than about its author's care.

That is T1 + T2 in one sentence, it contains no T3, and it is achievable. Nothing here says a clause is lawful,
and the tool must continue to refuse to say it.
