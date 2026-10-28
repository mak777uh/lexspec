# 15 — The chain layer: optional, outward, and never a source of truth

Status: **architecture, not spec.** The chain is not a legal layer; it is an *outward publication* layer. It adds
one property to the artifacts of [`docs/14`](14-ARCHITECTURE.md) — "this existed, in these bytes, at this time,
and nobody can quietly rewrite it" — and it adds nothing else.

Written because a chain is easy to add badly: the naive version publishes content that must not be published,
creates an immutability obligation that collides with an erasure right, and then calls the result trust.

---

## §1 What a chain can and cannot give

| Property | A chain gives it | Honestly |
|---|---|---|
| ordering of events | yes, by construction | only for what was committed |
| immutability of a record | yes, probabilistically, and it is the whole point | immutable garbage is still garbage |
| public verifiability without a trusted server | yes, if the commitment and the verification procedure are public | the procedure can be public and wrong |
| existence at a time | yes, as a lower bound (the block's time), never as an exact timestamp | a claim of "signed at 12:00" is a claim about a block, not a clock |
| settlement of value | yes, and it is regulated activity | not our layer, see §7 |
| truth of a statement | **no** | an anchored lie remains a lie, now harder to correct |
| legality of an interpretation | **no** | the chain cannot read |
| that the committed decision was correct | **no** | it proves only that this decision was recorded |

The rule that follows, and it is the same rule as everywhere else in this repository: **a chain moves the
question from "can this be changed?" to "was this right?", and only the second question matters.**

---

## §2 Three uses, three adapters

There is no "blockchain layer"; there are three different outbound uses with different artefacts. Each is an
adapter behind one interface, so that the checker never names a chain.

### 2.1 Notarisation — "this certificate existed"

- **Committed:** the sha256 of a certificate (or a Merkle root of many).
- **Revealed:** nothing but the digest.
- **Verified:** offline against the chain's headers, or against an inclusion proof (OpenTimestamps-style,
  Sigstore/Rekor-style transparency log, or an eIDAS qualified timestamp).
- **What it buys:** a decision record that cannot be back-dated or silently replaced.

### 2.2 Registry — "this statement was published, and here is its verdict"

- **Committed:** `statement_id`, canonical statement hash, anchor hashes, checker version, verdict, issue time.
- **Revealed:** by default the commitment only; selective disclosure under a policy, because a statement's
  existence can itself be sensitive (who contracted with whom, on what terms).
- **Verified:** recompute the hashes from the published statement and compare with the commitment.
- **What it buys:** a register that no single party can rewrite — the same instinct as
  [`lab/sources.md`](../lab/sources.md) applied to verdicts, with the same limit: a register records, it does not
  validate.

### 2.3 Settlement — "the flow moved"

- **Committed:** the flow identifier (payer, payee, anchored amount expression, trigger, deadline, currency) and
  the authorising atom.
- **Revealed:** whatever the parties agree to reveal; on most chains, amounts and addresses are public.
- **Verified:** the transfer exists and its memo/commitment matches the flow id.
- **What it buys:** the money layer of [`docs/14`](14-ARCHITECTURE.md) §3 gets a settlement rail.
- **What it costs:** every chain that settles value is a regulated financial system. This is the one use we
  explicitly do **not** implement (§7); we emit the intent and the evidence, and somebody licensed executes it.

### The adapter interface (five fields, and nothing chain-specific)

```
anchor.commitment      sha256 over the artefact's canonical bytes
anchor.chain_family    utxo | account | permissioned-ordering | transparency-log | tsa | none
anchor.reference       tx id / log index / sequence number, plus the family's own locator
anchor.time_lower_bound  block or log time, as a claim with its source
anchor.proof           inclusion proof or the procedure to obtain it
```

If a chain cannot express one of these, it is not supported — and "not supported" is a valid answer that the
certificate records.

---

## §3 The commitment rule

1. **Never publish content.** Publish commitments. The corpus is tens of megabytes, may be copyrighted, and
   always contains something that should not be on a public ledger.
2. **Salt commitments that cover personal data.** A plain sha256 of a small set is a dictionary attack away from
   disclosure; a salted commitment with the salt held offline is not.
3. **Batch.** One Merkle root per day, not one transaction per verdict; the proofs stay per-artefact.
4. **Keep the verification path chain-independent where possible.** Offline hash checking must work without any
   chain; the chain adds only the time and the immutability.

---

## §4 The conflict this layer creates with the law it checks — worked, not mentioned

This is the part worth the document.

`docs/12` and the GDPR measurement put **Art. 17 (right to erasure)** in this repository's own corpus. A naive
chain layer would publish, on an immutable ledger, commitments derived from personal data. That collides
directly:

| Step | Consequence |
|---|---|
| a statement concerns a natural person (a tax decision, an insurance refusal) | the artefact is personal data |
| its canonical hash goes on an immutable ledger | the hash is a pseudonymous identifier; under Recital 26 and the EDPB's reading, hashing is pseudonymisation, not anonymisation — it remains personal data |
| the person exercises Art. 17 | the controller can delete the record and the salt, but cannot delete the ledger entry |
| the ledger entry persists | either the erasure is incomplete, or the architecture promised something it cannot deliver |

**Therefore the chain layer must carry its own erasure policy, and it must be one of these three:**

1. **Crypto-erasure.** Commit salted hashes, publish only the salted hash and the salt's *commitment*; on erasure,
   destroy the salt, and record the destruction. The ledger keeps an unresolvable digest — defensible, and it
   must be written into the certificate, not discovered later.
2. **Commit to non-personal facts only.** What goes on-chain is the statement's *structural* identity (schema
   version, atom count, anchor hashes of public official texts) and never anything derived from a data subject.
3. **Do not publish this artefact.** Withhold from the chain and record the refusal as a first-class outcome —
   exactly the discipline this project already applies to verdicts.

A chain layer without an erasure policy is a compliance defect built by the tool that exists to find compliance
defects. That sentence is the reason this section exists.

---

## §5 Chain families, and what each can honestly do

| Family | Commitment | Time lower bound | Verification | Honest limit |
|---|---|---|---|---|
| UTXO chain (Bitcoin-style) | OP_RETURN-style data or a timestamping protocol on top | block time | header chain + inclusion proof | expensive per byte; confirmations take time; the time is a block's, not a clock's |
| Account chain with contracts | contract storage / event | block time | contract state read + event proof | the contract's code becomes part of the trusted base |
| Permissioned ordering service (Hyperledger-style) | ledger entry | ordering service time | membership-scoped verification | "public verifiability" is false: a stranger cannot verify |
| Transparency log (Rekor-style) | log entry + inclusion proof | log's signed timestamp | log public key + Merkle proof | a log can be operated dishonestly if its key is compromised; gossip is the defence |
| Qualified timestamp authority (eIDAS) | RFC 3161 token | TSA's asserted time | TSA certificate chain | a legal presumption exists only where the eIDAS regime applies |
| None | nothing | nothing | — | the default, and it must remain fully supported |

**A permissioned chain cannot be the only anchor**, because our verification story is "a stranger can re-check
it", and a stranger is outside the membership.

---

## §6 The rule that keeps the layer optional

The certificate and the verdict must be **identical** whether or not anything was anchored, with one extra field
say/saying `anchor: null` or `anchor: {...}`. If anchoring changes a verdict, the chain has become a source of
truth and the architecture has failed.

Concretely: `verdict` is computed before any anchoring; `anchor` is attached afterwards; and no code path may
read `anchor` when computing `verdict`. That is the same one-way seam as the prover (H8), applied outward.

---

## §7 What we do not build

- **No token, no coin, no incentive design.** Not our problem, and pretending otherwise invites the worst kind of
  audience.
- **No consensus, no node, no wallet, no custody.** Zero private keys held by this project.
- **No payment execution.** Settlement is emitted as an intent with evidence; executing it is licensed activity.
- **No claim that on-chain equals legally binding.** A hash on a ledger is evidence a thing existed; whether it
  binds anyone is a question of law, and it is not answered by a block height.

---

## §8 What we adopt, from whom

| Mechanism | Source | We adopt |
|---|---|---|
| batched commitments with per-artefact inclusion proofs | OpenTimestamps; Sigstore/Rekor | the batching and the proof shape |
| transparency log with signed checkpoints and gossip | Sigstore/Rekor, C2PA | the signed checkpoint idea; gossip as the honest protection |
| content credentials bound to an asset by signed claims | C2PA | the manifest-plus-claim structure, which our certificate already resembles |
| qualified timestamps where a legal presumption exists | eIDAS / RFC 3161 | the option, recorded as a chain family |
| verifiable credentials for selective disclosure | W3C VC | the direction for the registry's privacy story, not an implementation |

---

## §9 Failure modes per arrow

| Arrow | Silent failure | Check |
|---|---|---|
| certificate → commitment | a commitment covers a different byte sequence than the one reported | fixed by spec §3: one canonical form, named in the certificate |
| commitment → ledger entry | the entry exists but the inclusion proof is missing or unverifiable | the adapter must return a proof, not a transaction id alone |
| ledger entry → claim of time | "the block says 12:00" becomes "it happened at 12:00" | the certificate carries `time_lower_bound` with its source, never a timestamp |
| claim of time → verdict | anchoring upgrades a verdict | §6: no code path reads `anchor` when computing `verdict` |
| ledger entry → erasure | a personal-data commitment cannot be erased | §4: one of the three policies, recorded per artefact |
