# 07 — Round 01: questions we cannot answer from inside

A question pack for external models and practitioners. Every question here survived the first search round
([register](12-LANDSCAPE-REGISTER.md)) — meaning: we looked, and either found nothing, found only opinion, or
found two answers that contradict each other.

How to answer, in order of usefulness:

1. **One paragraph per ID**, in the format `ID → answer → source → what it changes`. Nothing else.
2. A source is a document a stranger can open: a specification, a paper, a repository, a statute. A blog post
   is a lead, not a source.
3. **"I don't know" is a valid and useful answer**, and so is "this question is badly posed, here is the real
   one". Both are more valuable than a confident guess.
4. If an answer is an opinion, mark it `[opinion]`. We keep opinions, but never as evidence.

---

## A0. The question that now outranks the rest

**Q0.** For each sub-problem our spec has to settle — binding a rule to its source, handling carve-outs,
representing uncertainty, certifying a result, applying editions over time, and reporting coverage — **what is
the best available answer, and what does that answer fail to do?**

This is not "what is left for us". Authorship is not a criterion in this project
([ADR-0004](../lab/decisions/ADR-0004-correctness-not-novelty.md)); the only question is which mechanism makes a
verdict more checkable, and where the best available mechanism stops working.

Answer in this shape, one block per sub-problem:

```
sub-problem → best available mechanism (name, version, link) → the property it establishes
            → the case it does NOT handle, named concretely → what we would test to confirm that
```

Do not answer "yours is fine". If a published mechanism is better, say so plainly; adopting it is the preferred
outcome and the cheaper one.

*Why we cannot answer it ourselves:* we found Arxo and LegalLean **after** writing twenty hypotheses and four
search passes, so our instinct about what is settled is exactly the instinct least likely to be right.
*What would change:* the spec. Adoption decisions are recorded in `lab/decisions/`, one per sub-problem, each
naming the source and the gap.

---

## A. Anchoring — the rule the whole design rests on

**Q1.** Does any official legal publisher expose a **stable, dereferenceable identifier for a byte range or a
numbered fragment** inside a legal text (not just for the document or the article)? Candidates to check:
ELI/`eli` subdivision identifiers, Akoma Ntoso `eId` fragments, EUR-Lex Cellar/Formex, `pravo.gov.ru`
publication formats, US `uscode.house.gov`/`govinfo` packages, UK `legislation.gov.uk` fragment IDs.
*Why we cannot answer it ourselves:* it requires reading several publishers' technical documentation, and our
one survey found only document-level identifiers.
*What would change:* if fragment-level anchors are stable somewhere, H1 stops being an invention and becomes an
integration. If nowhere, our uniqueness rule needs a different mechanism.

**Q2.** For a *consolidated* (amended) statute, what is the accepted way to pin "this exact wording was in force
between date X and date Y"? Name the format and the publisher that provides it.
*Why:* we currently assume a revision date plus a hash of a file we saved ourselves — which makes our corpus an
excerpt, not law.
*What would change:* whether v0.2 can ever claim anything about "the law" rather than "our copy of it".

**Q3.** Is there a published case where a citation system had to **retract** an anchor because the text was
amended under it? What did they do?
*Why:* this is the failure our `S2_SPAN_AMBIGUOUS` refusal is designed to prevent, and we have never seen it
observed in the wild.

## B. The model — Hohfeld and beyond

**Q4.** Is the eight-position Hohfeld square sufficient for **Russian civil-law drafting** (obligations,
supply, services), or does it systematically lose something that a Russian lawyer would consider essential?
Point at the construct that breaks it.
*Why:* our only corpus is ГК РФ art. 506/309, and our sources are common-law accounts of Hohfeld.
*What would change:* a different relational vocabulary, or an added dimension (e.g. remedies).

**Q5.** When a clause confers a **discretion** ("the buyer may require early delivery"), is that a privilege, a
power, or a third thing? What is the accepted formal treatment?
*Why:* three of our four passes on deontic logic disagreed about this, and it decides how `power` is used.

**Q6.** What is the correct formal treatment of an **exception** ("unless the contract provides otherwise")
when the goal is decidability rather than completeness? Name the formalism and its cost.
*Why:* H9 says defer defeasibility, but we have no evidence about what deferring actually costs at encoding
time.

## C. What is worth proving

**Q7.** Is a soundness theorem for a conflict detector — "if the checker reports no conflict, none exists under
the algebra" — a **publishable or useful** result, or is it trivial by construction?
*Why:* H3 is our main formal ambition, and if the theorem is a restatement of the code, we should drop it
rather than advertise it.
*What would change:* whether Lean enters v0.2 at all.

**Q8.** Has anyone published a **machine-checked proof that two independently written encodings of the same
statute diverge**? One search pass attributed this to a Lean library ("where sources of law diverge, the
divergence is a theorem") whose repository returns 404. Does the idea exist anywhere real?
*Why:* if it exists, it is the closest prior art to our whole program and we must cite it; if it does not, it is
a candidate contribution.

**Q9.** What properties of a *legal encoding* have actually been proved in a proof assistant, by anyone, with
downloadable artefacts? List them with what was assumed.
*Why:* our WP-04 coverage was the weakest of twelve — four passes found almost nothing verifiable.

## D. Cost, which decides whether any of this survives

**Q10.** Is there a **published measurement** of the cost of encoding one statutory article or one contract
clause into executable form — minutes, person-days, or lines per article? Not an estimate: a measurement, with
the corpus named.
Candidates: Catala's French family-benefits and tax code work, L4's Singapore projects, OpenFisca country
packages, PolicyEngine's US/UK models, the Rules as Code pilots.
*Why:* charter falsifier F3 says the project dies if encoding costs more than a careful human checklist, and we
have no number.
*What would change:* everything about scope — a cost of 30 minutes per article and a cost of 3 days per article
imply two different products.

**Q11.** Same question for **maintenance**: how much work per year does an encoded statute require after the
first encoding, per amendment?
*Why:* this is the number that kills such projects in practice, and no pass returned it.

## E. Evidence and admissibility

**Q12.** What must a machine-produced record contain to be **accepted by a court, auditor or regulator** as
evidence of what was checked? Point at the rule (FRE 902(13)/(14), eIDAS, 21 CFR Part 11, or a national
equivalent) and at the part of it that a hash alone does not satisfy.
*Why:* our H12 certificate is being designed from attestation practice, not from evidence law, and the two
differ.

**Q13.** How do regulated industries handle **key and algorithm ageing** for records that must remain
verifiable for 10–30 years? What is the accepted re-timestamping procedure?
*Why:* H17 gives a certificate a validity window, but not a story for what happens after it closes.

## F. The uncomfortable ones

**Q14.** If a lawyer were handed a `CHECKED_ANCHORED` verdict, what would they **mistakenly conclude**, and
what wording would stop them?
*Why:* charter falsifier F4 is exactly this, and we cannot test it on ourselves.

**Q15.** Which single part of this design would you delete first, and what evidence would make you delete it?
*Why:* we have five falsifiers and twenty hypotheses; a hostile reader's instinct is worth more than our list.

**Q16.** Is there a body of law where a checked-encoding product would be **obviously** worth its cost — narrow
vocabulary, frequent disputes, mechanical structure? Name it, and say what makes it mechanical.
*Why:* we chose contracts by default, and "default" is not a reason.

---

## What we will do with the answers

1. Each answer becomes a row in [`lab/sources.md`](../lab/sources.md) with a grade, and a hypothesis in
   [`docs/06`](06-FROM-TEXT-TO-PROOF.md) is either strengthened, weakened or killed in a dated note — never
   silently edited.
2. Answers that contradict each other are both kept; the contradiction goes into the next round.
3. An answer with no openable source is recorded as `[opinion]` and cannot move a design decision.
4. The four questions we most want answered first are **Q10, Q7, Q1, Q14** — cost, whether proving is worth it,
   whether anchoring is possible at all, and whether the verdict misleads. Everything else is downstream.
