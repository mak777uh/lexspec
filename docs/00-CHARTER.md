# CHARTER — what LexSpec is, what it refuses to be

Revision 0.1, 2026-10-28. This file governs the repository. Where any other document disagrees with it,
this one wins until the owner amends it.

## 1. The sentence this project exists to make true

> A legal statement can be written in a form that software checks, and the result of the check can be read
> by the person who wrote the statement, by a lawyer who did not, and by a machine that trusts neither.

Everything else in this repository is in service of that sentence or is scaffolding around it.

## 2. Why it is hard, mechanically

"Legal language formalised" sounds like one problem. It is at least four, and each has its own failure mode:

| Layer | Question | Typical failure when collapsed into the others |
|---|---|---|
| **L1 Surface** | what does the sentence say, precisely? | an LLM restates the clause fluently and changes one quantifier |
| **L2 Model** | what kind of legal position is this — duty, permission, power, immunity? | everything becomes "obligation", and permissions silently become duties |
| **L3 Inference** | what follows, and what conflicts? | a general-purpose prover proves a tautology of the encoding, not a fact about law |
| **L4 Provenance** | which exact text, at which revision, says so? | the citation points at a document, not at a span; the article was amended last week |

The tooling world loves to collapse L1–L3 into "AI reads the contract" and to skip L4. That combination
produces the worst artifact in this field: a confident verdict with no traceable anchor. A reader cannot
check it, so its only remaining function is persuasion. This project is built to make that artifact
impossible to produce with our tools.

## 3. The four commitments

**C1. Anchor or refuse.** Every normative atom carries an exact span in a pinned revision of a text.
No span, no hash match, or an ambiguous span is not a warning — it is a refusal. Codes: `S2_*`.

**C2. Verdicts are relative.** The checker never returns "legal" or "valid". It returns a verdict over a
triple `(statement, encoding, corpus@revision)`. Change any element, and the previous verdict is void. The
report therefore carries the canonical hash of the statement and the revision of every corpus it used.

**C3. Coverage and escapes are first-class numbers.** Atoms whose semantics are not closed are counted and
listed, never quietly dropped. A verdict computed over half an encoded clause is reported as what it is:
`CHECKED` with coverage 0.5, not `CHECKED_ANCHORED`.

**C4. The tool must be able to say "this is beyond me".** Every refusal code names a defect in the input,
not a limitation of the checker, except where the limitation is the point (`THIN_COVERAGE`). A refusal that
cannot be distinguished from a parse error is a bug in the vocabulary.

**C5. Clarity comes from survivable rows, not from volume.** What makes the truth clearer is not how much was
read but that every statement carries its own refutation: a quote someone else can open, a code that names the
defect, a number with the command that produced it, and a list of what was not claimed. So this repository
keeps three things ordinary research throws away — **refusals, dead ends, and contradictions** — and files them
as results. A model, a paper, or a colleague who says "verified" without an openable source has said nothing,
and no amount of agreement between such statements adds up to evidence.

**C6. Correctness is the objective; authorship is not.** The project exists to make a legal statement
checkable, not to be the first to do it. Where somebody has already built a mechanism that is better than ours,
we adopt theirs, cite it, and say so; where we build something, it is because a named gap in the available work
forces it, not because it would be ours. Two rules follow, and both are enforceable in review:

1. **Every mechanism names its source or its gap.** A construct in the spec that has no source and no stated
   gap is either copied without credit or invented without need — both disqualify it.
2. **A test of adoption is the test of truth.** If adopting a published mechanism makes the answer more
   checkable, adopt it even if that leaves nothing original to report. "We did it ourselves" is not a property
   of a verdict.

The corollary is uncomfortable and intended: when prior art settles a question, the effort moves to the parts
prior art does not reach — the corpus, the terms, the jurisdiction, the refusal vocabulary — and those parts are
judged by whether the answer gets *checkable*, not by whether they are new.

## 4. Non-goals (deliberate, and reversible only by the owner)

1. **Not legal advice.** The checker has no opinion about what a court would do. It checks the internal
   structure of a declared encoding and its anchoring to a declared corpus.
2. **Not a natural-language parser for statutes.** v0.1 does not attempt to read law from prose. Human or
   model assistance may propose a formalisation; the repository's job is to make the proposal falsifiable,
   not to trust it.
3. **Not a general-purpose theorem prover.** We do not compete with Lean, Isabelle, Z3 or an SMT solver.
   v0.1 is a *typechecker for legal positions* plus an *anchoring gate*; a prover can be attached later at a
   declared seam.
4. **Not a contract generator.** No drafting, no templating, no "generate a compliant policy".
5. **Not a court-ready artifact.** Nothing here is offered as evidence of anything; it is offered as a
   check that a third party can repeat.
6. **Not a jurisdiction-neutral ontology.** v0.1 is honest about being a skeleton with a Russian-law
   example; the corpus is pinned excerpts, not the law.

## 5. Falsifiers — what would prove this project wrong

Each is cheap to test, and each has a test that does not require a working product:

| # | Falsifier | Cheap test |
|---|---|---|
| F1 | A competent lawyer cannot read a statement without a manual. | give one encoded clause to a lawyer with the spec only; if they misread a relation, the surface syntax is wrong |
| F2 | Coverage cannot be computed honestly. | take a real clause, encode it, and check whether two encoders independently agree on which atoms are "closed" — disagreement above ~20 % means the metric is decoration |
| F3 | Encoding cost per article exceeds the value of the check. | time one article from reading to a statement that passes `CHECKED_ANCHORED`; compare with the cost of a careful human checklist |
| F4 | Refusals are indistinguishable from "I could not parse". | show the report to someone who did not write it and ask what they would do next |
| F5 | The verdict tracks fluency rather than structure. | two statements, one well-formed and false-in-corpus, one malformed and true-in-corpus; the checker must disagree with a fluent reader on both |

F5 is the one that separates this from every LLM-based legal checker. If we ever pass F5 by accident, assume
a bug.

## 6. What counts as success

Not "a product". Success, in order of ambition:

1. **S0 (reached in v0.1 if the tests pass):** a statement written in the schema is refused or accepted by a
   program, every acceptance carries a hash of every corpus it used, and every refusal carries a code that
   names a defect.
2. **S1:** an outsider encodes one clause of their own law, from the spec alone, and gets a verdict they
   can interpret without asking us.
3. **S2:** two independent encoders of the same clause produce statements whose canonical hashes differ but
   whose verdicts agree, and the disagreement is explainable.
4. **S3:** a lawyer uses a refusal to find a real defect in a real document.

Anything not on this list — customers, pricing, integrations — is not a success criterion and must not be
written as one.

## 7. Relationship to the owner's other projects

| Project | What we take | What we do not |
|---|---|---|
| [flowguard-spec](https://github.com/mak777uh/flowguard-spec) | the discipline: a boundary is *declared* and then proven inside; refusal codes; claim registry | its subject matter — value flow in a database, not legal positions |
| [VecDHT](https://github.com/mak777uh/VecDHT) | canonical byte form as the contract between implementations | its network, its economics |
| [mak777uh/-](https://github.com/mak777uh/-) | the lab bench: every number has the command that produced it, and reports are generated, not typed | its subject matter |
| [cases](https://github.com/mak777uh/cases) | the habit of publishing "not confirmed" as a first-class result | — |

The transferable rule across all four: **an artifact that cannot be re-checked by a stranger is a claim, and
claims are not results.**
