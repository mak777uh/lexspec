# ADR-0006 — The chain layer is optional, outward, and must carry an erasure policy

> **Amended 2026-10-28 by [ADR-0007](ADR-0007-substrate-independence.md).** The requirement turned out to be
> *continuity* — switching substrate when the legacy system is shaken — not publication. This ADR survives as the
> correct treatment of one substrate among several: commitments only, the erasure policy, and the one-way seam.
> The document it pointed at, `docs/15-BLOCKCHAIN-LAYER.md`, has been replaced by
> [`docs/15-SUBSTRATE-INDEPENDENCE.md`](../../docs/15-SUBSTRATE-INDEPENDENCE.md).

- **Date:** 2026-10-28
- **Status:** accepted (owner: *"слой блокчейна любых типов тоже предусмотри, возможность его построить поверх
  наших систем"*)
- **Evidence:** [`docs/15-SUBSTRATE-INDEPENDENCE.md`](../../docs/15-SUBSTRATE-INDEPENDENCE.md) §7

## Decision

1. **A chain layer is provided for, never required.** The certificate and the verdict are byte-identical with or
   without anchoring; the only difference is one field, `anchor: null | {...}`.
2. **Chain-neutral adapter, five fields** (commitment, chain family, reference, time lower bound, proof). The
   checker never names a chain; the families recognised today are UTXO, account-with-contracts, permissioned
   ordering, transparency log, qualified timestamp authority, and `none`.
3. **Commitments only, never content.** Salted where the artefact touches a natural person; batched with
   per-artefact inclusion proofs.
4. **Three uses, deliberately separate**: notarisation (this certificate existed), registry (this statement was
   published, here is its verdict — commitment first, selective disclosure under policy), settlement (the flow
   moved — emitted as an intent, never executed by us).
5. **The layer must carry an erasure policy**, chosen per artefact from exactly three: crypto-erasure with salt
   destruction, commitment only to non-personal structure, or refusal to publish. A chain layer without this is a
   compliance defect built by the tool that exists to find compliance defects.
6. **The one-way seam extends outward**: no code path may read `anchor` when computing `verdict`. Anchoring is
   publication, not evidence of correctness — the same rule as the prover (H8).

## What it does not authorise

No token, no consensus, no node, no wallet, no custody, no payment execution, and no claim that an on-chain record
is legally binding. A permissioned chain cannot be the only anchor, because the verification story is that a
stranger can re-check it and a stranger is outside the membership.

## Why this is worth a layer rather than a feature flag

Because it creates an obligation that the rest of the architecture must respect: **anything a chain may hold
forever, the law may later require to be erased.** Our own corpus contains Art. 17. A design that publishes
personal-data commitments immutably, without an erasure story, would be the exact failure this project exists to
catch — and it would be caught by our own tool, on our own artifact.

## Consequences

- `docs/14`'s chain now ends with an optional arrow: decision → commitment → ledger, with the check that no
  verdict depends on it.
- The certificate schema gains one nullable `anchor` object and one `erasure_policy` field. Planned, not made:
  [ADR-0001](ADR-0001-gather-before-build.md) still governs implementation.
- The interop channel with flowguard gains a third ask for note 2: whether their bundle can carry an external
  anchor without weakening the proof — our notarisation use is exactly that shape.
