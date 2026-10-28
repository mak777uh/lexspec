# Source intake register

Every source that arrives for this project is recorded here, with what it actually changed. The rule that
makes this file useful: **no source, no hypothesis** — a hypothesis in
[`docs/06`](../docs/06-FROM-TEXT-TO-PROOF.md) that cannot be traced to a row below is an opinion, and should be
demoted.

Status vocabulary, deliberately coarse:

| Status | Means |
|---|---|
| **skimmed** | opened, structure read, no claim extracted |
| **read** | the parts relied on were read in full; numbers taken from the page itself |
| **audited** | claim-by-claim grading against source files, with what could not be opened recorded |

---

## Received

| Date | Source | What it is | Moved | Status |
|---|---|---|---|---|
| 2026-10-28 | [`nearai/putnambench-deepseek`](https://github.com/nearai/putnambench-deepseek) | an agent that proved all 672 Lean 4 PutnamBench theorems; harness design, verifier, per-attempt costs, two defective upstream formalisations | H1, H7, H8, H18, H3 (the `pp.all` identity check) | read |
| 2026-10-28 | [`trishullab/PutnamBench`](https://github.com/trishullab/PutnamBench) + [leaderboard](https://trishullab.github.io/PutnamBench/leaderboard.html) + [`results.json`](https://github.com/trishullab/PutnamBench/blob/main/docs/results.json) | the benchmark: 672 Lean / 640 Isabelle / 412 Coq; the `lean-wsolution` vs `lean-nosolution` split; cost per solved problem across 52 methods | H1, H7 | read |
| 2026-10-28 | [`nearai/ironclaw`](https://github.com/nearai/ironclaw) | an Agent OS in Rust: WASM sandbox with capability grants, credential injection at a network boundary, closed-world host allowlists, severity ladder, audit log | H10, H12, H13, H14, H15 | audited — 19 README claims graded 7 enforced / 10 implemented-unverified / 1 documented-only / 1 contradicted, plus four internal contradictions. The full report is `IRONCLAW_2026-10-28.md` in the owner's research folder, outside this repository; the grade counts are the part that matters here |
| 2026-10-28 | [`docs.near.ai`](https://docs.near.ai/) | NEAR AI Cloud: private inference in TEEs, plus a full attestation discipline — verification policy, nonce/freshness binding, per-mechanism non-claims | H16, H17, H18, H19, H20 | read |

## A pattern worth noticing

The four sources above contributed 15 of the 20 hypotheses, and **only one of them is about law**. The
transferable structures came from a maths proof run, an agent OS, and a hardware-attestation reference. The
legal-formalisation literature (`docs/02`) contributed the vocabulary and the negative results — what has been
tried and where it stops — but no mechanism that survives contact with an adversary.

That is not an argument that law is special; it is an argument that the missing pieces here are
**evidence-handling** pieces, which other fields have already had to solve under pressure.

## Wishlist, with what would make each source useful

An item is worth fetching only if it can move a named hypothesis. "Interesting" is not a criterion.

| Want | Would move | Useful if | Dead if |
|---|---|---|---|
| A **worked deontic formalisation with machine-checked proofs** — source files, not a paper abstract (e.g. the LogiKEy/Isabelle dataset, or any normative theory encoded with proof obligations) | H3, H9 | the proof obligations are visible and small enough to compare with our eight-position algebra; we can see what they had to assume | only a paper describing the encoding; the files are not obtainable; the logic requires a semantics we would have to invent |
| A **policy language with proven meta-properties** (Cedar is the known case) | H3 | we can read the theorem statements and see how much of the work was the language design vs the proof | the proofs are informal, or the property proved is trivial (e.g. determinism of a pure function) |
| **Evidence integrity from a regulated industry** — hash-chained or WORM logs with a published retention/admissibility rationale (aviation maintenance, clinical trials under 21 CFR Part 11, financial trade reporting) | H12, H17 | the format is specified well enough to copy, and there is a stated reason why the format is that shape | it is a vendor's marketing page; or the integrity claim rests on organisational trust rather than a mechanism |
| **A concrete private-law encoding** with realistic coverage (Catala or L4 on something beyond benefits/calculator examples) | H2, H4, H7 | line counts and time-to-encode are reported, so the cost per closed atom becomes measurable | toy examples only; the encoding is not published |
| **LegalRuleML instances from a real jurisdiction** | H9 | the defeasibility constructs (`Override`, `Defeater`) are exercised on real text | specification examples only, no real corpus |
| **Anything on admissibility of algorithmic evidence in court** | T3 boundary | it states what a court requires to accept a machine-produced record, which bounds what a certificate must contain | it is commentary about "AI in law" without an evidentiary standard |
| **An existing corpus of clause-level annotations** (contracts labelled by clause type and party roles) | H7, H11 | it lets us measure encoding cost against something that already exists | paywalled, or labels are sentence-level only |

## How to add a row

1. Read enough of the source to state, in one sentence, what it claims.
2. Name the hypotheses it moved, or write `none` — `none` is a legitimate and useful result.
3. Grade it with the three-word vocabulary above, and record what you could not open.
4. If a number is quoted from it, the number comes from the page, not from memory.

A source that moved nothing is still recorded: a shelf of refused sources is the cheapest defence against
re-reading the same dead end, which is the same discipline as
[`docs/eliminations.md`](https://github.com/mak777uh/flowguard-spec/blob/main/docs/eliminations.md) in the
owner's other project.
