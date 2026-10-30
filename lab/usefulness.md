# Usefulness — answered honestly, no score

These are the five questions from HackerNoon's *Proof of Usefulness* questionnaire ([`docs/34`](../docs/34-USEFULNESS-REPORTS.md) §1), answered for this repository on **2026-10-30**. No projections, no self-score: the questionnaire's own rule — *not vanity metrics or projections* — is the reason the answers below are mostly "none".

The point of the page is not to look modest. It is that a reader deciding whether to trust a verdict should be able to
see what the project has actually changed for someone, and today that answer is one sentence long.

---

## 1. What is your traction to date?

**None outside this repository.** No person or organisation has used a verdict in a decision, as far as we know. The
only external interactions are four cross-audits written by this project and four written about it
([`cross-audit/`](../cross-audit/)), plus one review that closed a defect of ours by re-running our own reproduction.

Measured inside the repository, and these are not traction: 80 tests, 12 examples, 8 guards under a catalogue check, a
twin implementation agreeing with the checker on every segment of a court's arithmetic.

## 2. Not vanity metrics or projections — what is the one data point that proves people need what you built?

**There is none, and the honest answer is that we do not know that anyone needs it.**

The nearest thing is a defect found by an outside reviewer — `flowguard` re-ran its own reproduction against our tree
and `F-3-1` stopped reproducing. That proves someone found the work worth checking. It does not prove anyone needed it.

## 3. How do you measure genuine adoption versus "tourists"?

**We cannot, because there is no adoption.** If it appears, the measure is fixed in advance and it is not a visit and
not a star: a verdict cited in a decision by someone who did not write the statement, with a link to the artefact they
produced. Anything softer is a tourist.

## 4. What is your retention story?

**None.** A user who comes once and never returns is indistinguishable from no user, and we have neither.

## 5. If you re-score in 12 months, which criterion improves most, and what are you doing now?

**Technical stability**, and the work is already the visible part of this repository: every guard has a red path,
every number has a command, every claim carries `not_claimed`. It is also the dimension the market weights least,
which is stated in [`docs/33`](../docs/33-PROOF-OF-USEFULNESS.md) §5 rather than smoothed over.

The second candidate — and the only one that would count under question 2 — is **an artefact produced outside this
repository that depends on it**. One near-miss exists (the `flowguard` reproduction). The plan does not contain a
mechanism for creating more, and pretending otherwise would be a projection.

---

## What would change these answers

A dated row, one per event, with a link:

| event | where it would be recorded |
|---|---|
| someone re-runs a verdict and reports the result | [`lab/experiments.jsonl`](experiments.jsonl) as a new row, `origin: external` |
| a verdict is cited in a published document | a row here with the URL and the sentence it supports |
| a policy is audited by an outsider with our tooling | a case-like record with Claim / Evidence / Reproduce / Verdict / Limits |

Until the first row exists, every report this checker emits carries the line *"usefulness — no person or organisation
outside this repository has used a verdict in a decision"*, and this page is the longer version of that line.
