# 17 — Round 02: eight questions aimed at the three decisions we just made

Round 01 ([`docs/07`](07-ROUND-01-QUESTIONS.md), merged in [`docs/16`](16-ROUND-01-ANSWERS.md)) answered most of
what it was asked. What it did **not** do is test the three decisions we then made on its evidence:

- [ADR-0008](../lab/decisions/ADR-0008-computational-first.md) — computational provisions first;
- [ADR-0009](../lab/decisions/ADR-0009-transition-layer.md) — a transition layer for events that change positions;
- the certificate redesign implied by Q12/Q13 (process attestation + renewal chain).

Those are fresh, and fresh decisions are the ones that need attacking. So round 02 is short, targeted, and
biased towards **witnesses and artefacts** rather than literature — round 01's failure mode was four separate
"nobody has measured that", and the fix is to ask *who has done it*, not whether it exists.

---

## §1 What changed in the protocol

Round 01 taught three things about the asking, not the answering:

1. **Signatures.** Two rounds, two sets of unsigned tables. Rule 10 of the SEARCH-01 brief exists for this;
   here it is rule 0.
2. **Witnesses, not bibliographies.** "Name the project, repository, person or dataset" produces checkable
   answers. "What does the literature say" produces categories.
3. **Attack the decision.** Every question below names our current belief so the answer can contradict it. An
   answer that agrees with us without a new source has told us nothing.

## §2 The prompt

```
Context: a project that encodes legal provisions so that software can check them, and then compiles them into
rules for an enforcement engine. Current decisions under test are listed inside each question. Today is 2026-10-28.

RULES
0. First line of your reply: your model name and the date. An unsigned answer is discarded.
1. For every question: answer -> source (a URL you opened, or "not opened") -> what it changes about the decision.
2. Name a WITNESS where you can: a project, repository, person, dataset, court case. A category is not an answer.
3. State what would OVERTURN your own answer. If nothing would, say so and why.
4. If you did not browse, say so in the first line and mark each source "unopened".
5. Never invent a DOI, title, version, repository or quotation. "I do not know" is a complete answer.
6. Output: one block per question, at most 6 lines each. No introduction, no conclusion.
```

---

## §2 The eight questions

**Q17 — Who has maintained an encoded statute for more than two years, and what did it cost?**
We have no measurement of maintenance effort per amendment ([`docs/16` §7](16-ROUND-01-ANSWERS.md)), and four
sources confirmed none is published. So: name the **witness**. OpenFisca country packages, PolicyEngine US/UK,
Catala at CNAF, the NZ/AU Rules-as-Code pilots, a tax administration's own engine. For each: how long has it been
maintained, how many amendments per year touched it, and who reported the effort.
*Belief under attack:* that maintenance is the largest ongoing cost (we assert it, we cannot show it).

**Q18 — Beyond Vernie & Grabmair, who has compared two independent formalisations of the same provision?**
That paper (arXiv 2605.25186) enumerates disagreements with a SAT solver, and found behavioural divergence
essentially uncorrelated with structural similarity. Any other work that produces **both** encodings and a
machine-checkable witness of where they differ?
*Belief under attack:* that a divergence theorem is an open contribution (our Q8 finding).

**Q19 — What is the minimal vocabulary for a legal *transition*?**
We need events that change positions: a notice that terminates (ГК 450.1), a party's bad faith that makes a
condition count as fulfilled (ГК 157(3)), exercise of a power that creates a duty. Has anyone published a small,
executable transition vocabulary for private law — events, triggers, effects, and the evidence each requires?
*Belief under attack:* ADR-0009's assumption that a transition layer is the right shape and has to be built.

**Q20 — Has anyone compiled statutory rules into a policy engine while preserving the source anchor?**
We intend to emit Cedar/OPA rules that carry `atom id` + anchor hash ([`docs/14`](14-ARCHITECTURE.md) §4). Is
there published work where a *statutory* rule survives compilation into a policy artifact with provenance intact,
and where the artifact's decision record cites the legal text?
*Belief under attack:* that this link (L4 → L6) is unbuilt territory.

**Q21 — Is there a published handover protocol for regulated decision systems?**
Our substrate-independence layer ([`docs/15`](15-SUBSTRATE-INDEPENDENCE.md)) proposes checkpoints, signed
handovers and fork detection. In regulated settings — payment systems, registries, clinical systems — has anyone
published a *continuity* protocol with legal effect, rather than a business-continuity plan?
*Belief under attack:* that substrate switching needs to be invented.

**Q22 — Is there an evidence-package standard that combines all three of our certificate requirements?**
The certificate must carry (a) a process attestation by a qualified person (FRE 902(13)), (b) a renewal chain
(RFC 4998), and (c) reproducibility (recompute the result from named inputs and versions). Candidates to check
against the combination: in-toto/SLSA attestations, BSI TR-03125 (TR-ESOR), ETSI TS 119 511, W3C Verifiable
Credentials, NIST SP 800-57. Which of them already covers all three, and where do they stop?
*Belief under attack:* that we must assemble the package ourselves.

**Q23 — Which computational provisions have an official, recomputable ground truth?**
We want to test an encoding against a number computed by someone else: a tax authority's calculator, a court-fee
formula, a benefits simulator, a statutory interest calculator. Name the **specific provision and the official
calculator or published worked example** — Russian, EU or other.
*Belief under attack:* ADR-0008's choice of ГК 395, which we have just confirmed is anchorable (see
[`docs/16` §11](16-ROUND-01-ANSWERS.md)) but not yet shown to have an official worked example to compare against.

**Q24 — What would make "computational provisions first" wrong?**
Name a class of computational provisions where encoding cost explodes or anchoring fails: values set by annex
tables, rates by delegated act, aggregations over taxpayer-specific periods, rounding rules that depend on
another act, cross-references to definitions in a different instrument. Give a concrete example.
*Belief under attack:* the whole pivot in ADR-0008.

---

## §3 How these answers will be used

- Each answer lands as a row in [`lab/sources.md`](../lab/sources.md) with a grade, and the decision it touches
  gets a dated note — never a silent edit.
- An answer of "I do not know" with a stated reason is a **result**: four of them together close a question
  rather than leave it open, which is how Q8 and Q11 were settled.
- If Q24 produces a concrete failure class, ADR-0008 is amended before any code is written, not after.

## §4 Why not more questions

Sixteen in round 01 was right for mapping a field. Eight here is right for attacking three decisions. A third
round should not exist until these eight have answers, because the next questions depend on them — and because a
question round that repeats itself produces confident paraphrases, which is the failure this project is built to
detect.
