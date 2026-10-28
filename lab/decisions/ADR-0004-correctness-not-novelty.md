# ADR-0004 — Correctness is the objective; novelty is not a criterion

- **Date:** 2026-10-28
- **Status:** accepted (owner instruction: *"нам не нужна новизна, нам надо сделать максимально хорошо —
  установить истину"*)
- **Supersedes in part:** [ADR-0003](ADR-0003-both-tracks-two-systems.md) — the "narrow track" was framed as a
  claim to novelty; it is reframed here as a correctness requirement
- **Bears on:** charter C6, [`docs/12` §6](../../docs/12-LANDSCAPE-REGISTER.md), [`docs/07` Q0](../../docs/07-ROUND-01-QUESTIONS.md)

## Context

After the landscape work ([`docs/12`](../../docs/12-LANDSCAPE-REGISTER.md)) it became clear that four of our
hypotheses describe work already published and better engineered than our plan: Arxo Law ships byte-pinned
sources, evaluation documents and a Lean-checked certificate; LegalLean ships a defeasibility solver with six
property theorems and a `RequiresHumanDetermination` boundary; two 2026 papers measure how formalisations of one
provision diverge. The earlier documents responded by asking "what is left for us", which silently promoted
authorship to the objective.

The owner removed that objective.

## Decision

1. **The only criterion is whether the answer becomes more checkable.** Not whether it is ours, not whether it is
   publishable as a contribution, not whether it is first.
2. **Adopt by default.** For every sub-problem, take the best available mechanism, cite it by name and version,
   and write down what we changed and why. A mechanism enters the spec with a `source:` (the work it comes from)
   or a `gap:` (the concrete thing that work cannot do), and a reviewer may reject a construct that has neither.
3. **Judge prior art by fitness, not by prestige.** Arxo's four-valued support may be better for our domain than
   LegalLean's boundary type, or worse; that is decided by a test, not by the eminence of the author.
4. **Novelty language is removed from the project's self-description.** No sentence in this repository may
   present a mechanism as an advance over published work unless it also states what was tested and against what.
5. **The remaining work is defined by gaps, not by opportunities.** The gaps named so far: civil-law
   jurisdictions (Russian drafting, where Hohfeld's square may or may not survive), unanchored term definitions,
   corpus availability asymmetry between jurisdictions, and a refusal vocabulary published as a versioned
   artifact.

## What changes in practice

| Before | Now |
|---|---|
| "H3 is our formal ambition" | "H3 is a requirement; LegalLean and Arxo already meet it; our job is to meet it at least as well, or explain why not" |
| "narrow track: the two properties nobody claims" | "narrow track: the two properties the domain needs and the published work does not yet cover — judged by whether they change a verdict" |
| "what is left to contribute (Q0)" | "for each open sub-problem, what is the best available answer, and what does it fail to do (Q0 rewritten)" |
| a landscape register scoring novelty | a register of **adoptable mechanisms** with a fitness note per row |

## Consequences

- **Nothing is deleted for being unoriginal.** The disqualifier is now "unsourced and unnecessary", which is
  harder to satisfy than "not new".
- **Attribution becomes load-bearing.** Copying without citation is now the central failure mode, because copying
  is the default behaviour.
- **The comparison work is not optional.** To adopt the best, we must read Arxo's checker and LegalLean's
  theorems rather than their landing pages. That is now a prerequisite for the next design decision
  (`defeats`, see [`docs/13`](../../docs/13-DEFEASIBILITY-CHOICE.md)).
- **If someone else's system is simply better and complete**, the honest outcome is to use it and say so. This
  ADR permits the project to end as an integration rather than to continue as an imitation.
