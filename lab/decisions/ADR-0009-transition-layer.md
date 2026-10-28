# ADR-0009 — A transition layer is required; Hohfeld's eight positions are not a semantics

- **Date:** 2026-10-28
- **Status:** accepted (evidence: round-01 Q4 and Q5, [`docs/16` §4](../../docs/16-ROUND-01-ANSWERS.md))
- **Depends on:** [`docs/13`](../../docs/13-DEFEASIBILITY-CHOICE.md) — defeat is the same family of problem

## Context

Three independent answers to Q4 said the same thing in different words: Hohfeld gives a **vocabulary of
relational positions**, not a semantics of an obligation. What the eight cells cannot express, and what Russian
civil law visibly needs, is:

- **remedy / protective relations** — ответственность as a distinct relation, not as "a duty that was breached";
- **status of an act** — ничтожность and оспоримость are statuses of transactions, not positions of parties;
- **transitions** — ГК РФ 157(3) (a condition treated as having occurred because a party in bad faith prevented
  it) and 450.1 (a unilateral refusal notice that changes or terminates the relation) are **events that alter
  positions**, and no static classification reaches them.

Q5 sharpened it: "the buyer may require early delivery" is not one operator. If the demand creates a duty that
did not exist, it is a **power**, whose exercise triggers a **claim**; often bundled with a liberty not to
exercise it. Three of four answers converged on this, and it resolves the disagreement our own deontic passes had.

## Decision

1. **Add a transition layer** (L2b) between positions and inference: events that change positions. A transition
   has a trigger, a condition (which may itself be a legal construct, as in 157(3)), and an effect on positions
   (create, extinguish, suspend, transfer). It is *not* an atom, and it does not get a Hohfeld label.
2. **Add a status dimension** to acts: `valid` / `void` / `contestable` / `unknown`, separate from positions,
   because ничтожность is a property of a transaction and not of a party's position.
3. **Compound atoms must be verifiable**: an atom whose effect is a state change is encoded as
   `power(actor) → triggers claim(counterparty)`, and a statement that bundles permission and effect must
   declare both. A single atom labelled `power` with no declared effect is refused — it is the ambiguity that
   produced disagreement in the first place.
4. **Remedy is deferred but named.** v0.2 does not model damages or termination consequences; it must *record*
   that it does not, as an escape with the reason `REMEDY_NOT_MODELLED`, so that a clause relying on remedies
   cannot reach a strong verdict.

## What this changes in the vocabulary

| Existing | Becomes |
|---|---|
| `relation ∈ 8 Hohfeld positions` | unchanged, but the atom may carry a `triggers` (power) or `status` (act) field |
| coverage counts closed atoms | also counts transitions; a transition with an unmodelled trigger keeps the atoms it affects not-closed |
| verdict | unchanged; a statement relying on transitions in an engine that does not implement them is `CHECKED`, never `CHECKED_ANCHORED` |

## Why not just add a ninth position

Because a position is a *state*, and the cases above are *changes of state* or *properties of acts*. Adding a
ninth cell would force 157(3) and 450.1 into a static shape they do not have, and every subsequent encoding would
inherit that distortion. The right shape is a small state machine over positions, which is also what L4 and
Arxo's edition model independently arrived at.

## Consequence for the plan

The transition layer is a **schema change**, so it lands with tests or not at all (ADR-0001). It is ordered after
the quantity layer (L5) and before contract clauses (ADR-0008), because computational provisions need quantities
far more than they need transitions.

## Amendment, 2026-10-28 — the vocabulary exists, and it is Symboleo

Round 02 (docs/20 §2) found prior art that this decision did not account for: **Symboleo** — *Towards a
Specification Language for Legal Contracts* (RE 2020) and *Specification and analysis of legal contracts with
Symboleo* (SoSyM 2022) — a contract ontology with **legal positions, obligations, powers**, events, and
**statecharts for obligation lifecycles**, with verification support.

Consequences, in place of §"Why not just add a ninth position":

1. The transition layer is still needed *for this project's purpose*, but its **vocabulary must be Symboleo's**,
   not invented here. Inventing a parallel vocabulary would violate charter C6 (source or gap) — the gap we must
   name is narrower: Symboleo does not carry the **evidence** each event requires, and does not target Russian
   civil-law events (ГК 450.1, 157(3)).
2. The deliverable of this layer is therefore a **mapping** from our atoms to Symboleo concepts plus an evidence
   slot per event, not a new event language.
3. The three-case test in Q19 stands: 450.1 (notice terminating), 157(3) (bad faith deemed fulfilment), and an
   exercise-of-power-creating-duty case. If Symboleo expresses all three with the evidence slot added, the layer
   is adoption, not construction.

## Addendum 2, 2026-10-28 — Symboleo covers two of the three cases, and the third is ours

Round 03 (`docs/26`, W2) converged across three answers:

- **(a) notice-triggered termination** — covered *idiomatically*: a notice is a domain event and termination is a
  `Power` whose antecedent references it. No dedicated Notice construct exists, and that is fine.
- **(c) power creating a duty with a deadline** — the two halves exist (powers carry deadlines, obligations carry
  deadlines), but the *composition* has no published worked example anyone found. Treat as an implementation
  risk, not as covered vocabulary.
- **(b) ГК 157(3), bad faith deeming a condition fulfilled** — **not expressible.** Symboleo has no Condition
  class; conditions appear only as propositions in a trigger or antecedent, and its semantics is a deterministic
  event calculus over observed events, which has no operator for a legal fiction that deems an unobserved
  condition satisfied.

**Consequence.** The layer adopts Symboleo for (a) and (c), and (b) is an **authored rule with the statute as its
basis**, recorded as such. ADR-0009 may not claim that the vocabulary supplies all three Russian transitions.
