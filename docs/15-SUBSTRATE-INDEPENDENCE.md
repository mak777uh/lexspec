# 15 — Substrate independence: surviving a shock in the legacy system

Status: **architecture, not spec.**

> **Correction, 2026-10-28.** An earlier version of this document treated a chain as a *publication* layer —
> notarisation, immutability, public verifiability. That was the wrong requirement. The owner's point is
> resilience: **if the legacy system is shaken, the operation must be able to switch to an alternative.** A chain
> is one possible alternative substrate, not the subject. This document replaces that framing; the erasure
> finding from the earlier version survives in §7 because it is still true and still expensive.

---

## §1 The requirement, stated as a property

> For every decision this system produces, there must exist **at least two substrates** able to produce and
> record it from the same rule set, and a **provable continuity** between them, so that losing one substrate does
> not lose the ability to decide or to prove what was decided.

"Substrate" means whatever actually executes and records: a bank's payment rail, an internal enterprise engine,
a state registry, a cloud provider's policy service, a chain, or paper with a hash on it. The design requirement
is not that a chain is present; it is that **no single substrate is a point of failure for the legal-operational
layer**.

Three consequences, and each is a constraint on the rule model rather than on the deployment:

1. **Rules must be substrate-neutral.** If a rule can only run on one engine, the second substrate does not exist.
2. **State must be checkpointable.** A switch mid-history must resume without a gap and without re-deciding what
   was already decided.
3. **The switch itself must be legally grounded.** Moving an obligation from a bank rail to a chain is not a
   technical act — it discharges a debt only if a norm says so. This is the part only this project can check,
   and §5 is the reason the layer belongs in *our* architecture rather than in an ops handbook.

---

## §2 The shock model

A substrate is lost in specific ways, and the fallback differs per way. The table is the threat model, and it is
deliberately short — these are the shocks that have actually happened to systems of this kind.

| Shock | What it takes away | What must survive | Mechanism |
|---|---|---|---|
| payment rail cut (sanctions, correspondent bank, SWIFT) | ability to move money | the obligation, its amount, its authorising norm, the record of what was paid | substrate-neutral flow objects (§3) + settlement intents (§7) |
| provider shutdown or policy change | the engine, the API, the keys held there | the rules and the ability to evaluate them elsewhere | rules as data, not as provider configuration |
| registry outage or refusal | the authoritative record | a verifiable copy and a way to prove it matches | signed checkpoints + independent anchoring |
| key loss or compromise | authorship of anything signed | the ability to re-establish and to mark what is suspect | key rotation recorded as an event; decisions carry the key that signed them |
| currency or rate discontinuity | the meaning of an amount | the rule that pins the rate, and the revision that applied | anchored quantities (L5) with a rate reference, never a literal |
| loss of network entirely | everything online | the ability to decide and to record offline | degraded mode (§6) with offline-verifiable certificates |

**The test of the architecture is the drill, not the diagram.** A fallback that has never been exercised is a
belief. §6 makes the drill a required artefact.

---

## §3 What substrate neutrality forbids in the rule model

A rule that is portable must not depend on anything the substrate provides implicitly. Each prohibition is a
checkable property of a compiled rule, not a style preference:

| Forbidden dependency | Why | The check |
|---|---|---|
| wall clock | two substrates will disagree, and the disagreement is undetectable | every time value is an input or an anchored reference, never `now()` |
| randomness, iteration order of a map | same inputs must give byte-identical decisions | decision record carries the canonical bytes; a twin run must match |
| implicit external calls (rate lookups, FX, oracles) | unavailable exactly when the shock happens | every external value is an input with a source and a revision (L5) |
| substrate-specific identity | an account id is not a party | parties are terms (L2), mapped to substrate identifiers by a declared table |
| provider-specific policy syntax as the source of truth | it is the compiled artefact, not the rule | the statement is the source; the engine artefact is generated and carries its atom ids (L6) |
| mutable global state | a switch cannot reconstruct it | state is an explicit checkpoint (§4) |

If a construct cannot be evaluated without one of these, it is not admitted into a compiled rule — it becomes an
escape, which is the vocabulary this project already has for "we cannot check this".

---

## §4 The continuity protocol

Switching substrates is not a redeploy; it is a **handover with proof**. Three commitments make it checkable:

```
checkpoint = { rule_set_hash, corpus_revision, term_table_hash,
               last_decision_seq, last_decision_hash, state_root, issued_at_source }

handover  = { from_substrate, to_substrate, checkpoint, basis, actor, signatures }

resume    = first decision on the new substrate, carrying handover.id and proving
            that it follows last_decision_hash
```

Rules:

1. **No gap, no fork.** The first decision on the new substrate must reference the last decision hash of the old
   one. Two substrates producing decisions after the same checkpoint is a fork and must be reported as a
   conflict, not silently reconciled.
2. **Same rule set.** `rule_set_hash` and `corpus_revision` must match on both sides; a switch that also changes
   the rules is a rule change and needs its own record.
3. **State is explicit.** Whatever the next decision needs must be inside `state_root`; anything not reconstructible
   from it is a defect discovered at the drill, which is the right time.
4. **The handover is signed by a named actor**, and the actor's authority is itself a position in a statement
   (L2) — not an assumption about who runs the servers.

---

## §5 The switch needs a legal basis, and finding it is our job

This is the section that makes the layer belong here.

Whether a technical handover *discharges an obligation* is a question of law. Paying on a chain is not payment
unless the applicable norm allows it; a registry entry is not a registration unless the regime recognises it; an
electronic record is not evidence unless the evidentiary rule admits it.

So a handover carries a `basis` field, and that field is **a position, not a sentence**: an anchored atom in a
statement, pointing at the span that authorises the switch. Practically, that span is usually one of:

- a **force-majeure or business-continuity clause** in the contract (who may switch, on what trigger, with what
  notice);
- an **alternative-performance clause** (payment in another form or rail counts as performance);
- a **regulation permitting electronic or alternative records** (e-evidence regimes, electronic-signature and
  e-identification rules, sectoral continuity requirements);
- **no basis at all** — which is a finding, and a serious one: the switch is then a business continuity measure
  with no legal effect, and the system must say so before anyone relies on it.

**What this means in practice:** the same checker that validates a clause validates a handover, because a
handover is a statement with a corpus, anchors and positions. That is why the resilience requirement lands in
*this* architecture: the fallback is only real if the right to use it is checkable.

---

## §6 Degraded modes, and the drill

Four levels, each with what it can still prove:

| Mode | Available | What is proven | What is lost |
|---|---|---|---|
| **full** | rules + engine + substrate + anchoring | decision, enforcement, publication | — |
| **degraded-evidence** | rules + engine, no substrate writes | decision + certificate, offline-verifiable | ordering by an external clock; publication |
| **degraded-manual** | rules + paper procedure | a human decision recorded with hashes and signatures | automatic enforcement |
| **minimal** | signed statements only | what was asserted, by whom, when | everything computed |

A certificate states the mode it was produced in. A decision made in `minimal` mode is not wrong; it is weaker,
and the weakness is visible — which is the same discipline as coverage and escapes.

**The drill** is a scheduled exercise that performs a real handover on a real clause: checkpoint on substrate A,
resume on B, produce a decision, verify the chain end to end. It is the equivalent of restoring a backup, and it
has the same property: untested, it is a story. The drill's output is a row in [`lab/cost.md`](../lab/cost.md)
and a pass/fail in the certificate template.

---

## §7 A chain as one substrate among several

If a chain is used, it is used for what it is actually good at, and it is subject to §7's constraints:

| Use | Good for | Not good for |
|---|---|---|
| commitments and checkpoints | small, public, append-only facts; a handover record anyone can verify | the corpus (tens of MB, may be copyrighted), personal data |
| settlement | value movement that a norm authorises | being "payment" by itself — see §5 |
| availability | distributed copies of commitments | serving the rules or the state; chains are poor databases |
| dispute | a shared, non-repudiable timeline | deciding the dispute |

**The erasure conflict, kept from the earlier version because it is still true.** Our own corpus contains GDPR
Art. 17. Hashing a statement about a natural person and publishing it immutably is a collision: hashing is
pseudonymisation, not anonymisation (Recital 26), so the digest remains personal data, while the ledger entry
cannot be erased. A chain-bearing artefact must therefore choose one of three policies and record it:
**crypto-erasure** (salt destroyed, the commitment becomes unresolvable), **commit only to non-personal
structure**, or **refuse to publish**. A chain layer without this choice is a compliance defect manufactured by
the tool that exists to find compliance defects.

**Two more limits of this substrate specifically:** a bridge between two chains is a trusted component and
becomes part of the trusted base; and a permissioned chain cannot be the *only* substrate, because our
verification story is that a stranger can re-check it and a stranger is outside the membership.

---

## §8 What this layer never claims

- A decision recorded on a substrate is not therefore lawful, and a handover is not therefore valid — §5 decides
  that, and only if a norm is found and anchored.
- Redundancy does not equal correctness: two substrates running the same wrong rule produce the same wrong
  decision twice, deterministically. That is a property worth having and it is not the one being advertised.
- No token, no consensus, no custody, no payment execution, no wallet, no private keys held by this project.
- Availability of a substrate is never assumed at the time of the shock; that is the definition of the shock.

---

## §9 Failure modes per arrow

| Arrow | Silent failure | Check |
|---|---|---|
| rule set → second engine | the second engine interprets an unstated construct differently | twin evaluation on a fixed corpus; any divergence is a defect, not a nuance |
| checkpoint → resume | state needed by the next decision was never in the checkpoint | the drill: resume on B from A's checkpoint and produce a decision |
| handover → legal effect | the switch works technically and discharges nothing | `basis` must be an anchored position; "none" is reported as a finding |
| decision → certificate | the certificate omits the mode and the substrate | mode and substrate are mandatory fields |
| commitment → erasure | a personal-data commitment cannot be erased | one of the three policies in §7, recorded per artefact |
| anchoring → verdict | publication or redundancy upgrades a verdict | no code path reads `anchor` or `substrate` when computing `verdict` ([ADR-0006](../lab/decisions/ADR-0006-chain-layer.md), H8 one-way seam) |
