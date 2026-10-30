# 14 — Architecture: from the language of law to an enforced boundary

Status: **architecture, not spec.** It says what the chain is, which links are ours, which are adopted, and what
each link must be able to prove. Numbers here are structural, not measured; the measured ones live in
[`lab/cost.md`](../lab/cost.md).

The problem this document answers: laws regulate markets, and around money flows are built software flows. A
tool that stops at "this clause is coherent and anchored" stops one link short of the only place where the
question matters — **the boundary where a system actually permits or refuses an action**. LexSpec's job is to
make that boundary traceable back to the exact words that authorise it.

---

## §1 The chain, stated once

```
 law text (pinned)
      │  L1  surface: sentence → positions
      ▼
 positions (Hohfeld)          ← L2  model
      │
      ├─ L3  inference: conflicts, defeat, gaps, coverage
      │
      ├─ L4  provenance: every position → one span, one revision, one hash
      │
      ▼
 quantities and flows          ← L5  money: amounts, periods, rounding, payer→payee
      │
      ▼
 policy artifact for an engine ← L6  compilation: atom → rule, with the atom id carried through
      │
      ▼
 enforced decision             ← L7  runtime: the boundary permits or refuses, and logs why
      │
      ▼
 evidence: decision ↔ rule ↔ atom ↔ span ↔ revision
      │
      ▼
 optional: second substrate + handover   ← L8  continuity under shocks; never a source of truth (§6, docs/15)
```

Every arrow is a place where the chain can break silently, and each break has a different owner. §7 lists them.

**The claim this architecture makes** is narrow and checkable: for any decision the boundary made, a stranger
can walk back to the exact bytes that authorised it, and can check that each step preserved the reference. It
does **not** claim the decision is lawful (§6).

---

## §2 Why the money layer changes the model rather than decorating it

Our current spec has no arithmetic at all. That is survivable for a clause about who owes what to whom, and
fatal for the laws that actually move markets, because those laws are made of numbers:

| What the law says | What our v0.1 can represent |
|---|---|
| "the rate shall not exceed 20 per cent" | nothing — no quantities |
| "within thirty calendar days" | an interval, but not a period from an event, and no working-day rules |
| "the amount shall be rounded to the nearest whole unit" | nothing — rounding is not a construct |
| "the fee is 0.5 per cent of the contract price" | nothing — no expressions |
| "the total for the period shall not exceed the cap" | nothing — no aggregation over a period |

So the money layer is not a feature; it is the reason such a language is worth building for market
regulation. It has four parts, and each has an adoption candidate:

1. **Exact quantities.** No binary floats, ever — the same rule that already governs our canonical form
   (spec §3) now governs values inside a statement. Money is an integer in a declared scale, with the currency
   as a unit. *Adopt:* the Catala/Arxo split as described in their parity article — Catala stores money to the
   cent and rounds a money-times-decimal product; Arxo keeps money exact and **rounds only where the text says
   so**. The second is the correct default for a checker: rounding is a legal decision, so it must be anchored,
   not inherited from a library.
2. **Periods and deadlines.** An interval is not a period. "Within thirty days of the event" needs (start event,
   length, calendar, working-day rules, holiday table). *Adopt:* the working-day calendar as **pinned data**
   with a hash, which is how Arxo handles it — a case outside the calendar's coverage must be reported as
   out-of-range, never guessed.
3. **Expressions and aggregates.** A fee is a formula; a cap is an aggregate over a period. This is the only
   part where a general computation language beats a checker, and the honest answer is to *borrow* one.
   *Adopt:* a small total expression language, or Catala's scope model, rather than inventing one.
4. **Every number anchored.** The rate in the encoding must point at the span that fixes the rate. A number
   without an anchor is the most dangerous object in this whole design, because it looks authoritative and is
   unverifiable — and it is exactly what an LLM will produce fluently.

**Consequence for the spec.** `action` gains an optional quantity expression; `terms[]` gains units; the
canonical form gains a decimal representation that cannot be a float; and coverage gains a category: an atom
whose number is unanchored is *not closed*.

---

## §3 The flow layer, and why flowguard is now a substantive partner

An obligation about money is a **flow**: payer, payee, amount expression, trigger, deadline, currency, and the
position that authorises it. Once a statement is expressed as positions plus flows, it has the same shape as the
thing flowguard already reasons about — value moving between points under a declared control boundary.

That is not a metaphor. The two projects meet on one artifact:

| Question | Whose discipline answers it |
|---|---|
| may this value move from A to B at all? | LexSpec: the position that authorises the flow, anchored |
| does it pass the single control point, and is that provable? | flowguard: the closure and the control boundary |
| what happens when the amount exceeds a statutory cap? | LexSpec: the cap as an anchored quantity; flowguard: the boundary that refuses |
| can a third party re-check the decision? | both: our certificate and their bundle verifier must name the same bytes |

This is the second interop note's subject: a **joint artifact** — a flow, its authorising position, its anchored
quantity, and the boundary that must refuse when the quantity is violated. If flowguard's closure can be given a
normative constraint without weakening its proof, that seam is worth more than either project alone.

---

## §4 The enforcement boundary, and what "reliably protected" can honestly mean

The user-facing promise is a boundary that reliably enforces what the law requires. The architecture can deliver
that only by **compiling to an engine someone else has verified**, and by carrying the reference chain through:

1. **Compile, do not interpret.** A statement's atoms become rules in a declared policy engine
   (Cedar, OPA/Rego, XACML, ODRL). *Adopt:* the engine, not a rival. Cedar is the strongest case because its
   language has been modelled and proved, and its validator gives schema-level checks; OPA is the pragmatic
   choice when the enforcement point is already Rego.
2. **Carry the atom id into the rule.** Every compiled rule carries its atom id and the anchor hash. A rule that
   cannot name its atom is not compiled — it is dropped and reported as an escape.
3. **Decisions are evidence, not logs.** The boundary's decision record must contain: the rule, the atom, the
   anchor hash, the corpus revision, the checker version, and the engine version. That is the same record shape
   our certificate already requires, extended by one field.
4. **Attestation, where the enforcement runs elsewhere.** If the boundary runs on someone else's infrastructure,
   the decision record must be bound to attested execution — NEAR AI's attestation discipline gives the pattern
   (verification policy declared by the relying party, nonce freshness, per-mechanism non-claims). *Adopt:* the
   discipline; not necessarily the vendor.
5. **Capability grants, where the boundary is an agent.** If the actor is an agent, the boundary is a capability
   boundary: the tool may reach only what the grant names, and the credential is injected at the boundary rather
   than handed to the tool (IronClaw's model). *Adopt:* the pattern; it is the same "declared requirement
   enforced at a boundary" shape as our anchoring rule.

**What "reliably protected" therefore means, exactly:** the boundary enforces a rule that is traceable to an
anchored span, the enforcement is done by an engine whose semantics someone else has verified, and the decision
is recorded well enough that a stranger can re-check the chain. It does **not** mean the law was interpreted
correctly — that is the human link, and it stays visible.

---

## §5 What moves in the existing documents

| Document | Change |
|---|---|
| charter §2 | the four-layer table gains L5 money, L6 compilation, L7 enforcement; the failure mode of collapsing them is "a compliant-looking system with no traceable rule" |
| charter §4 non-goals | add: we do not build an enforcement runtime; we compile to a declared engine and certify the chain |
| spec §2 | `action` gains an optional quantity expression; `terms[]` gains units; `corpus[]` gains an optional calendar pin |
| spec §8 coverage | an atom with an unanchored number is not closed — a new escape reason `UNANCHORED_QUANTITY` |
| spec §9 verdicts | unchanged; the boundary's decision is a separate artifact and can never raise a verdict (H8 holds at every layer) |
| docs/13 | defeat now matters twice: for positions, and for caps (a cap defeated by an exception is the money version of Art. 17(3)) |

---

## §6 What this architecture does not claim

- Not that an enforced decision is lawful. Traceability is not legality, and the chain ends at a human reading.
- Not that the engine is correct. We adopt someone else's verified language; their trusted base becomes ours,
  and must be printed with every decision record.
- Not that a policy artifact is a contract. We never generate the instrument; we check the statement and compile
  the constraint.
- Not that the numbers are right. An anchored number is a number someone can check, not a number that is correct
  — and an unanchored one does not enter the chain at all.

---

## §7 The five arrows, and the failure each one hides

| Arrow | Silent failure | The check that catches it |
|---|---|---|
| text → positions | the position is a paraphrase of the sentence | L4: the span must exist, uniquely, in the pinned revision |
| positions → inference | the encoding is coherent but thin | coverage + declared escapes (existing) |
| inference → quantities | a number enters from the encoder's head | `UNANCHORED_QUANTITY` — new, and it must be a refusal |
| quantities → policy artifact | a rule loses its atom id during compilation | compilation refuses to emit a rule without an atom and an anchor hash |
| artifact → decision | the decision is right but cannot name why | the decision record carries atom + anchor + revision + versions |

---

## §8 What we adopt, from whom

| Mechanism | Source | We adopt |
|---|---|---|
| anchor to exact substring of a pinned publication | Arxo Law | the rule, plus our uniqueness condition |
| four-valued result, "silence is not negation" | Arxo Law | the result vocabulary for positions and, later, for quantities |
| defeat with declared priority, property-theorem target | LegalLean | the construct; see [`docs/13`](13-DEFEASIBILITY-CHOICE.md) |
| money exact, rounding only where the text says so | Arxo parity article (contrast with Catala) | the default for our quantity layer |
| working-day calendar as pinned data with a hash | Arxo Law | the calendar pin |
| policy compilation with schema validation | Cedar | the compilation target when the boundary is an application |
| policy evaluation as a first-class artifact | OPA/Rego | the compilation target when the boundary is infrastructure |
| declared verification policy, nonce freshness, per-mechanism non-claims | NEAR AI attestation docs | the decision-record discipline for remote enforcement |
| capability grants, credential injection at the boundary | IronClaw | the boundary model when the actor is an agent |
| value flow inside a declared closure | flowguard-spec | the flow layer's counterpart; joint artifact in interop note 2 |

Nothing in this table is claimed as ours. The contribution, if any, is the **chain**: each link exists
somewhere; the requirement that a decision be walkable back to a span, and that an unanchored number never
enters the chain, is what this architecture insists on.

---

**Decision record:** [`ADR-0005`](../lab/decisions/ADR-0005-chain-to-the-boundary.md) — why the chain stops where it does.
