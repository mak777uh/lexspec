# 20 — Round 02, merged: two of our claims are dead, and two things worth adopting

Six answers to [`docs/17`](17-ROUND-02-QUESTIONS.md) arrived on 2026-10-28 (Perplexity, GPT-6, o3, Qwen, and a
Claude answer that declares it did not browse — that last one is treated as grade-C leads throughout). Three of
them named things I had never seen. Two survived verification and changed our decisions.

---

## §1 The hit: CAP-RRS specifies the chain we thought was unbuilt

**Verified by reading the draft** — [`draft-sato-soos-cap-rrs-03`](https://datatracker.ietf.org/doc/draft-sato-soos-cap-rrs/),
Tom Sato (MyAuberge K.K.), IETF individual draft, 5 September 2026. Not an IETF standard (individual submission,
no standing), but public, detailed, and directly on our L4→L6→L7 chain:

| Their mechanism | What it does | What we claimed to have to invent |
|---|---|---|
| **Regulation Record** | "the human-readable, machine-compilable intermediate form between legal text and Cedar policy" | our "statement" |
| **Cedar Compilation Profile** | a normative mapping with a **determinism requirement**: two conforming compilers must produce semantically equivalent Cedar from one record | our L6 compilation with atom ids |
| **`authority_source_uri` (REQUIRED)** | a Law Reference Interface block naming "which law, which article, which statutory version, when the endorsement was made, who made it, and the endorsement's legal character" | our anchor + our provenance |
| **decision record** | PERMIT/DENY "with a structured reason code referencing the specific Regulation Record that fired", and the `authority_source_uri` must match the trace attribute emitted at evaluation time | our L7 decision record |
| **amendment detection** | poll the authority's endpoint ≤24 h; raise `CATALOG_VERSION_CONFLICT`; `INTERPRETATION_SUPERSEDED` for interpretive change without statutory change | *nothing — we had no such mechanism* |
| **suspension window** | a policy may stay SUSPENDED at most 30 days, then must become DENY | *nothing* |
| **rollback defence** | reject catalog updates whose `supersedes` or `effective_date` regress | *nothing* |
| **certification model** | who may certify a record at each tier, with signed packages and a registry | *nothing* |

**So the L4→L6 edge is not unbuilt.** It is specified, in public, by one author, with no implementation evidence
we could find. Our honest position changes from "we would be first" to "the architecture exists on paper; what is
missing is (a) span-level anchoring rather than article-level, (b) any implementation, (c) standing".

**What we adopt, explicitly:** the `authority_source_uri` idea as a first-class field; the decision record citing
the fired record and carrying the anchor at evaluation time; the amendment-detection cadence; the 30-day
suspension rule; the rollback defence. Each is a mechanism we lacked and would otherwise have hand-rolled worse.

**What remains ours, if anything:** uniqueness of the byte span (theirs identifies law/article/version, not a
unique span); Hohfeld positions as a *type discipline with correlative pairing*; coverage and escapes as reported
numbers; and the closed refusal vocabulary.

---

## §2 The second hit: the transition layer has a published vocabulary

**Verified:** **Symboleo** — *Towards a Specification Language for Legal Contracts* (RE 2020) and the SoSyM 2022
paper, with a contract ontology that includes **legal positions, obligations, powers**, events and **statecharts
for lifecycles**, plus verification support.

That is, in substance, the transition layer [ADR-0009](../lab/decisions/ADR-0009-transition-layer.md) says must be
built. ADR-0009 is therefore amended in place: the layer is still needed *for our purposes*, but its vocabulary
must be **Symboleo's**, not invented, and the thing we add is the evidence slot each event requires (which the
answers say Symboleo does not carry).

Note also that one answer cited arXiv 2511.12276 as Symboleo; it is not — that paper is the eFLINT reflection
paper (van Binsbergen et al., J. Computer Languages 2026), which is itself a serious normative language with
compliance checks before, during and after a system runs. Both are real; the citation was wrong, the lead was
right.

---

## §3 Q24 hit our flagship provision, and the answer is uncomfortable

Two independent answers said ГК 395 is a *bad* first choice, for a reason we had not considered:

- its rate is an **external value set by another body** (the Bank of Russia) — we already knew, and handled;
- but its history is **periodised by delegated acts**: the model that used regional average deposit rates ran until
  31 July 2016 and was replaced by the key-rate model from 1 August 2016; and in 2022 a government moratorium
  suspended accrual for a window (`Постановление Правительства № 497`, **`[unverified]` — not opened by us**).
- **and there is no official recomputable oracle.** The calculators the answers found are court "reference"
  services (2aas.arbitr.ru, tyva.arbitr.ru — both explicitly *справочный характер*) or commercial (Consultant,
  Garant). One answer asserted a Constitutional Court ruling (No. 61-П, 22 October 2026) touching art. 395 —
  **`[unverified]`**, and if true it is the strongest argument of all: the arithmetic is simple while the legal
  rule moves.

**Consequence:** ADR-0008's selection criteria must include, before any coding: does the provision have a
**stable** rule, **anchored** parameters, and an **authoritative oracle**? ГК 395 passes the second weakly (period
versioning), fails the third. It stays as the *anchoring* test (we proved that), but it cannot be the
**correctness** test until an oracle or a court judgment with explicit numbers is found.

---

## §4 The rest, briefly, because it held

| Q | Consensus across six | Effect |
|---|---|---|
| Q17 maintenance | no published measurement of effort per amendment, anywhere; witnesses named: OpenFisca-France, PolicyEngine UK/US, Catala at CNAF/DGFiP | stays a risk hypothesis; the "largest ongoing cost" claim is now marked as assertion, not evidence |
| Q18 divergence | nobody found a machine-checked divergence result; Vernie & Grabmair is the only comparison with a SAT witness, and Arxo/Catala parity (65 cases + 240 random) is a differential test without a theorem | divergence stays a candidate contribution, graded "not found", not "does not exist" |
| Q19 transitions | Symboleo (and eFLINT) exist; none covers the evidence each event needs; none targets ГК 450.1 or 157(3) | adopt Symboleo's vocabulary, add evidence |
| Q21 handover | no regulator-published continuity protocol; nearest: Estonia's Data Embassy (treaty-backed), eIDAS 24(2)(h) termination plans, EMIR CCP recovery, Certificate Transparency gossip for fork detection | build the cryptographic part on CT-style consistency proofs; do not invent the legal part |
| Q22 evidence package | six of six: no single standard covers all three; the assembly is the work — in-toto/SLSA payload inside an RFC 4998 / TR-ESOR evidence record, with the qualified-person certification as the human layer | certificate = three layers, assembled, and we stop looking for one standard |
| Q23 oracle | no official calculator for ГК 395; court calculators are "for reference" | see §3 |

---

## §5 What this round changes in the repository

| Document | Change |
|---|---|
[R`docs/19`](19-PORTFOLIO.md) §2 | the L4→L6 edge moves from "asked / not built" to **"specified publicly (CAP-RRS); unbuilt in practice; must be adopted, not invented"** |
| [ADR-0008](../lab/decisions/ADR-0008-computational-first.md) | addendum: selection criteria gain stability, anchored parameters, and oracle availability; ГК 395 demoted from correctness test to anchoring test |
| [ADR-0009](../lab/decisions/ADR-0009-transition-layer.md) | amended: Symboleo is prior art; our layer adopts its vocabulary and adds the evidence slot |
| [`lab/cost.md`](../lab/cost.md) | unchanged numbers, but measurement 2 is now labelled an **anchoring** measurement, not a correctness one |

---

## §6 The uncomfortable summary

Two of the three decisions from round 01 were, in part, already answered by public work that six models found and
four earlier passes did not:

- "compile statutory rules into a policy engine with provenance" → **CAP-RRS**;
- "a transition vocabulary for private law" → **Symboleo**.

The pattern from `docs/12` §6 repeats: the model's blind spot is the recent and the specialised, and our own
blind spot is believing that a mechanism we cannot find does not exist. The corrective is not more search rounds —
it is the rule already in the charter: **a claim of "unbuilt" is a claim, and it needs the same evidence as any
other.** §1 and §2 above are what it looks like when that rule fires.
