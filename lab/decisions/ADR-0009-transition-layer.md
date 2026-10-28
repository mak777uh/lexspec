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
