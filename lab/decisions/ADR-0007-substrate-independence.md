# ADR-0007 — Substrate independence is a resilience requirement; a chain is one substrate

- **Date:** 2026-10-28
- **Status:** accepted (owner: *"блокчейн я имею ввиду как софтверную возможность, чтобы если будут потрясения в
  легаси — система могла переключиться на альтернативу"*)
- **Amends:** [ADR-0006](ADR-0006-chain-layer.md) — that ADR framed the chain as a publication layer. Publication
  is one use, not the requirement.
- **Evidence:** [`docs/15-SUBSTRATE-INDEPENDENCE.md`](../../docs/15-SUBSTRATE-INDEPENDENCE.md)

## Context

ADR-0006 answered "how do we publish a verdict immutably". The actual requirement is different: **continuity**.
If the legacy rail, the provider, the registry or the network is shaken, the operation must be able to move to
another substrate without losing either the ability to decide or the ability to prove what was decided.

That reframing changes what must be designed. Immutability is replaced by portability; notarisation by handover;
and the chain becomes one backend among several, subject to the same constraints as any other.

## Decision

1. **No single substrate may be a point of failure for the legal-operational layer.** For every decision there
   must be at least two substrates able to produce and record it from the same rule set, plus a provable
   continuity between them.
2. **The rule model must be substrate-neutral**: no wall clock, no randomness, no iteration-order dependence, no
   implicit external lookups, no substrate-specific identity, no provider policy syntax as the source of truth,
   no mutable global state. A construct needing any of them is not admitted and becomes an escape.
3. **Handover is a protocol with proof**: checkpoint (rule set hash, corpus revision, term table hash, last
   decision hash, state root), signed handover naming the actor, and a resume that references the last decision.
   Two decisions after the same checkpoint is a **fork** and is reported as a conflict.
4. **The switch carries a legal basis, and finding it is this project's job.** `basis` is an anchored position,
   not a sentence: force majeure, alternative performance, or a regulation permitting electronic or alternative
   records. No basis is a finding, and a serious one — the handover is then continuity without legal effect, and
   the system says so before anyone relies on it.
5. **Degraded modes are first-class** (full, degraded-evidence, degraded-manual, minimal), and every certificate
   names the mode it was produced in.
6. **A drill is mandatory.** A real handover on a real clause, checkpointed on one substrate and resumed on
   another, with a recorded pass or fail. An untested fallback is a belief, and this repository does not ship
   beliefs.
7. **A chain, if used, is one substrate**: commitments and checkpoints, not the corpus; subject to the erasure
   policy (crypto-erasure, non-personal structure only, or refusal); its bridges are part of the trusted base;
   a permissioned chain can never be the only substrate.

## What this changes

| Document | Change |
|---|---|
| charter §2 | L8 is now "publication and substrate continuity", not "publication" |
| `docs/14` | the optional arrow is a second substrate with a handover, not just a ledger entry |
| `docs/15` | rewritten from publication to continuity; the chain material survives as one section |
| certificate schema (planned) | `substrate`, `mode`, `handover`, `anchor`, `erasure_policy` — all nullable, none able to affect `verdict` |

## What would overturn it

- If a second substrate cannot be made to agree byte-for-byte on a fixed corpus, then portability is a fiction
  and the honest architecture is a single substrate with a *recorded* single point of failure — stated in the
  certificate, not hidden.
- If no jurisdiction provides a legal basis for switching rails for the target obligations, then handovers are
  operations-only, and the architecture must say that the continuity is technical, not legal.
