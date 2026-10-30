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

Rows arrive two ways: directly (someone reads a source and records it) or through a work package of
[`lab/assignments/SEARCH-01-landscape.md`](assignments/SEARCH-01-landscape.md), which is the distributed
search brief — twelve work packages, one per model, fixed output schema, mergeable by dedupe key.

---

## Received

| Date | Source | What it is | Moved | Status |
|---|---|---|---|---|
| 2026-10-28 | [`nearai/putnambench-deepseek`](https://github.com/nearai/putnambench-deepseek) | an agent that proved all 672 Lean 4 PutnamBench theorems; harness design, verifier, per-attempt costs, two defective upstream formalisations | H1, H7, H8, H18, H3 (the `pp.all` identity check) | read |
| 2026-10-28 | [`trishullab/PutnamBench`](https://github.com/trishullab/PutnamBench) + [leaderboard](https://trishullab.github.io/PutnamBench/leaderboard.html) + [`results.json`](https://github.com/trishullab/PutnamBench/blob/main/docs/results.json) | the benchmark: 672 Lean / 640 Isabelle / 412 Coq; the `lean-wsolution` vs `lean-nosolution` split; cost per solved problem across 52 methods | H1, H7 | read |
| 2026-10-28 | [`nearai/ironclaw`](https://github.com/nearai/ironclaw) | an Agent OS in Rust: WASM sandbox with capability grants, credential injection at a network boundary, closed-world host allowlists, severity ladder, audit log | H10, H12, H13, H14, H15 | audited — 19 README claims graded 7 enforced / 10 implemented-unverified / 1 documented-only / 1 contradicted, plus four internal contradictions. The full report is `IRONCLAW_2026-10-28.md` in the owner's research folder, outside this repository; the grade counts are the part that matters here |
| 2026-10-28 | [`docs.near.ai`](https://docs.near.ai/) | NEAR AI Cloud: private inference in TEEs, plus a full attestation discipline — verification policy, nonce/freshness binding, per-mechanism non-claims | H16, H17, H18, H19, H20 | read |
| 2026-10-28 | **SEARCH-01, four independent returns** (passes A, B, C unsigned; pass D = Claude Sonnet 5.5) | the first distributed landscape pass: 53 distinct approaches after dedupe, across twelve work packages | docs/12 rows; schema fix (`year_basis`); mandatory signature in the assignment; four defects including one fabricated repository | read and merged — see [`docs/12-LANDSCAPE-REGISTER.md`](../docs/12-LANDSCAPE-REGISTER.md) |
| 2026-10-28 | [Arxo Law: law as function, law as data](https://blog.arxo.io/law-as-function-law-as-data/) + [`arxohq/arxo-catala-parity`](https://github.com/arxohq/arxo-catala-parity) (Apache-2.0) | a commercial/rules-as-code engine whose compiler rejects any quoted fragment that is not an exact substring of the pinned official publication; evaluation documents with proof graphs; four-valued support; Lean 4 checker (91 theorems); Rust engine + Python reference | **kills the novelty of H3, H12, H15, H17**; leaves H1's uniqueness clause and the Hohfeld-as-type reading as possibly ours | read — the strongest prior art in the register |
| 2026-10-28 | [`edu-ap/legal-lean`](https://github.com/edu-ap/legal-lean) (MIT, Lean 4, 87 theorems) + [project site](https://legal-lean.aguilar-pelaez.co.uk) | `RequiresHumanDetermination` with the contested boundary; typed legal IR over eight factors; generic defeasibility solver with six property theorems; factorial English→Lean equivalence testing; false-precision rate as release gate | H3 (solver-property theorems) and H15 (boundary as a type) are already published; the *false precision rate* is a metric we should adopt | read |
| 2026-10-28 | [Vernie & Grabmair, arXiv 2605.25186](https://arxiv.org/abs/2605.25186) (EMNLP 2026) | comparing formalizations of one provision by the decisions they encode: node matching, SAT enumeration of disagreement, verbalised cases; 10 EU provisions, 9 LLMs | a result that constrains us: **behavioural divergence is essentially uncorrelated with structural agreement** — so "the encodings look alike" proves nothing | read (abstract) |
| 2026-10-28 | [Saka, arXiv 2609.01741](https://arxiv.org/abs/2609.01741) | a survival certificate for machine-extracted statutory logic; two extractors diverge at FNR 0.43 on Missouri statutes; implication basis + Monte Carlo + Wilson bound; 93.2 % of held-out chapters below the informativeness floor | calibrates how much a machine-extracted encoding can be trusted, and publishes an audit trail with one retracted claim — a model for our own honesty sections | read (abstract) |

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

| 2026-10-30 | [LongTails](https://github.com/k3nfalt/longtails) — Lean 4 framework for automated research in optimisation; Setup as a formal contract, Comparator as an independent audit, novelty left to judgement | **adopted**: an independent second implementation (tools/lexcheck_twin.py), escapes must name the layer that closes them, novelty verdicts carry a search date | the contract is a type, not prose; our atom set still cannot be re-derived from the text (P7) |
