# ADR-0005 — The chain reaches the boundary: quantity, compilation and enforcement are layers

- **Date:** 2026-10-28
- **Status:** accepted (owner: laws regulate markets and money flows, products are built around money flows, and
  the system must go from the language of law to precisely corresponding, reliably protected resource boundaries)
- **Evidence:** [`docs/14-ARCHITECTURE.md`](../../docs/14-ARCHITECTURE.md)

## Context

The spec, the hypotheses and the first measurements all stopped at a verdict about a clause. The owner's
statement of purpose is longer: laws regulate markets, money flows through products, and the useful artifact is a
boundary that permits or refuses in accordance with the law and can prove which words it obeyed.

Two consequences follow immediately, and both are facts about our own model rather than about ambition:

1. **Market regulation is made of numbers**, and v0.1 has no arithmetic. A rate, a cap, a threshold, a period, a
   rounding rule, an aggregate over a period — none of it is representable. A language for market law without
   quantities is a language for a subset of contract prose.
2. **A verdict is not a boundary.** Between our report and a running system there are two links we never named:
   compiling a position into a rule, and recording a decision well enough to walk back to a span.

## Decision

1. **Add three layers to the model**: L5 quantity, L6 compilation, L7 enforcement. The charter's layer table is
   updated; the failure mode of each layer is now named there.
2. **Quantities are exact and anchored.** No binary floats; money is an integer in a declared scale with a unit;
   rounding is a legal decision and must be anchored, never inherited from a library; a working-day calendar is
   pinned data with a hash; **a number without an anchor does not enter the chain** and makes its atom not-closed
   (new escape reason `UNANCHORED_QUANTITY`).
3. **Flows are the bridge to flowguard.** An obligation about money is a flow (payer, payee, amount expression,
   trigger, deadline, currency) authorised by an anchored position. The joint artifact with flowguard — flow plus
   authorising position plus anchored quantity plus the boundary that must refuse — becomes the subject of
   interop note 2.
4. **We compile, we do not enforce.** A statement compiles to rules for a declared engine (Cedar where the
   boundary is an application, OPA/Rego where it is infrastructure, XACML/ODRL where the artefact must
   interoperate). Every emitted rule carries its atom id and anchor hash; a rule that cannot name its atom is not
   emitted, and the atom is reported as an escape.
5. **Decisions are evidence.** The decision record contains rule, atom, anchor hash, corpus revision, checker
   version, engine version — and, where enforcement runs remotely, is bound to attested execution under a
   declared verification policy.
6. **The non-goal is now explicit**: we do not build the runtime. Adding it would make us responsible for a
   guarantee we cannot make, and it is not needed for the chain to be honest.

## What this changes in existing documents

| Document | Change |
|---|---|
| charter §2 | seven layers; the collapse failure described per layer |
| charter §4 | non-goal 5: not an enforcement runtime |
| `docs/14` | the architecture, the five arrows and the check per arrow |
| spec §2, §8 | planned: quantity expression on `action`, units in `terms`, calendar pin in `corpus`, `UNANCHORED_QUANTITY` |
| `docs/13` | defeat matters twice — for positions and for caps |

The spec edits are **planned, not made**: [ADR-0001](ADR-0001-gather-before-build.md) still governs
implementation, and a quantity layer is a schema change that must land with tests, not before them.

## What would overturn this

- If an existing language already closes the whole chain — anchored text, quantities, compilation, decision
  evidence — then the honest move per [ADR-0004](ADR-0004-correctness-not-novelty.md) is to adopt it wholesale
  and stop. The closest candidates are Arxo (text → evaluation document, no compilation to an external engine)
  and Catala (text → value, no anchoring), and neither closes it alone.
- If anchoring a number turns out to be impossible on real texts (numbers are often set by tables in annexes, by
  reference to a central-bank rate, or by delegated act), then the quantity layer must be narrowed to "numbers the
  statement can cite", and the rest must be refused rather than guessed. That outcome is acceptable and must be
  measured before the schema change.
