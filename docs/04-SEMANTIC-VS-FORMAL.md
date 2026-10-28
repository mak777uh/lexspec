# 04 — Semantic vs formal verification: where each applies, and where each lies

Status: research brief, not spec. Authority stays with [`00-CHARTER.md`](00-CHARTER.md) and [`10-SPEC-v0.1.md`](10-SPEC-v0.1.md); this file supplies only the external evidence behind their choices. Access date **2026-10-28**. Every number was read out of a fetched primary document in this session, except where marked `[unverified]`; grades follow [`99-SOURCES.md`](99-SOURCES.md).

An agent has just machine-checked all 672 Lean 4 PutnamBench theorems. LexSpec is not that kind of verification, and the difference is not weaker-versus-stronger — it is *which link in the chain the machine holds*. This file is about that link.

---

## §1 Two techniques, stated precisely

### 1.1 What a machine-checked proof guarantees

A proof assistant is a small trusted kernel plus a large body of derived machinery. A kernel-accepted proof term establishes

> **⊢ P** — the proposition `P`, as written in the prover's logic, holds in every model of that logic, assuming the kernel, the logic's axioms, and any declared axioms or free dependencies.

Total in one dimension (every case `P` quantifies over; no sampling, no test data), empty in another (nothing about whether `P` is the sentence a human wanted). Hence "`P` is proved", never "the system is correct". A proof is **sound** with respect to the statement — nothing false-in-the-logic passes the kernel — and **complete** only up to proof search, where incompleteness is an engineering fact (the agent gives up, the tactic times out), not a soundness defect. Vendor prose routinely swaps these two words.

### 1.2 What it does not guarantee

| Gap | In one line | Kernel catches it? |
|---|---|---|
| **Statement fidelity** | the formal `P` is not the informal claim | No — `P` is an input |
| **Model fidelity** | the formal objects do not denote the real ones | No |
| **Environment** | hardware, compiler, network, adversary, humans do not behave as assumed | No — or only by modelling, which inherits the gap |
| **Trusted base** | kernel, axioms, parser, assembler, linker, an assumed spec | Partly: `#print axioms` catches axioms; nothing catches the linker |

The first two are the **specification gap**, and no tooling retires them. Hence the split between **verification** ("did we build it right?", relative to a statement) and **validation** ("did we build the right thing?", relative to intent). A proof is a verification instrument only; using it as validation is **verification of the wrong specification**. A proof obliges you to name what must be true for the conclusion to matter, and each such thing is proved, assumed-and-read-by-a-human, or unexamined; CompCert and IronFleet publish that list (§3), the strongest available signal that a proof project was done honestly.

### 1.3 What semantic / model-based checking guarantees

A *declared model* (schema, policy language, state machine, typed relations) plus a checker that decides consistency, or conformance on sampled behaviour, or that stated properties hold on generated inputs. Three attainable results: **coherence** (parses, types, violates no declared internal constraint — disjointness, totality, acyclicity, coverage arithmetic); **conformance on a sample** (for inputs actually generated or observed, behaviour matched); **agreement with an oracle** (where an independent decision procedure exists, answers matched). Each is a claim about a finite set of observations plus a structural argument, and each is only as good as the model.

### 1.4 What semantic checking does not guarantee

- **Not the ungenerated case.** "No counterexample found" is not "no counterexample"; input-space coverage is an empirical property of a generator.
- **It inherits the oracle problem.** Where output correctness is not independently decidable, the check needs a human or a second implementation to say what was right — itself unverified. PBT is valuable here precisely because it often discovers that the oracle was unclear (§4).
- **Not the right model.** It checks conformance to the declared model exactly as a prover checks a proof against a statement: same gap, one level down.
- **Completeness is a design choice.** A checker that refuses on ambiguity is sound-but-incomplete — it never passes a bad artifact and refuses some good ones. Usually right for legal artifacts, but it must appear in the verdict, not be hidden.

### 1.5 Vocabulary, pinned

| Term | Precisely | Misused as |
|---|---|---|
| soundness | nothing that fails the check is accepted | "the system is correct" |
| completeness | everything that should pass does | "found all the bugs" |
| verification | artifact conforms to a *given* statement | "the software is right" |
| validation | the statement conforms to *intent* | "we proved it" |
| spec gap | formal statement ≠ informal intent | "a minor formalization issue" |
| oracle problem | no independent ground truth for the answer | "the tests pass" |
| trusted base | what must be believed for the result to hold | "it's fully verified" |
| wrong-spec verification | a true theorem about the wrong proposition | "672/672 solved" |

---

## §2 The empirical case: 672/672, and two defective statements

### 2.1 What was claimed

`nearai/putnambench-deepseek` claims **672 problems solved and machine-validated — "all 670 solvable upstream problems it attempted, plus corrected variants of the two problems whose upstream formalizations turned out to be defective"**. The arithmetic is the point: 670 + 2 *corrected* ≠ 672 upstream theorems. The repository fixed two statements, then claimed the full count.

- The agent gets the Lean file with a `sorry` and one tool (bash). `completed()` runs a verifier requiring no `sorry`/`axiom`/`native_decide`, a theorem statement **byte-identical** to a frozen copy, a clean `#print axioms`, and successful elaboration.
- A second, semantic check: the solved theorem's fully-elaborated type (`pp.all`) must be **character-identical** to the pristine statement's, which the README says "defeats statement-rewriting exploits that textual diffs miss".
- `disproved()` exists for a false statement: the agent must derive `False` in Lean, human-reviewed.
- Three passes: 639, then +22, then 11 left — 2 defective statements and 9 agents that quit. A fourth run with V4 Pro finished the tail. The stopping rule belongs to the harness: one agent attempted to quit **3,423 times out of 5,106 turns** (`putnam_2022_b6`) and was refused until it succeeded.

### 2.2 The two defects

1. **`putnam_1974_b1`** (5 points on a circle maximizing pairwise distances). The upstream solution predicate — "some ordering has equal consecutive distances" — is satisfied by degenerate configurations with repeated points (an equilateral triangle listed as `[A,B,C,A,B]`), which are not maximizers, so **the theorem as stated is false**. A machine-checked proof of `statement → False` was produced (clean axioms), matching upstream issue #347. Fixed by adding `Function.Injective p`; the corrected theorem was then proved twice independently.
2. **`putnam_2013_a5`** (area-definite lists, R² → R³). The statement pins 3D area to `μH[2]` on `Fin 3 → ℝ`, whose Pi instance carries the **sup metric** — making "area" the plane-dependent Busemann–Hausdorff measure rather than Euclidean area. The statement *appears true* but is **not the informal problem**, and needs convex geometry absent from Mathlib. Fixed by moving to `EuclideanSpace ℝ (Fin 3)`; the corrected version was proved twice within ~5 hours each, while the original resisted multi-day attempts.

### 2.3 What this proves, stated narrowly

The two are different failure modes, and the README does not merge them. `1974_b1` was caught **mechanically**: failure-to-prove was converted into a *proof of falsity*. `2013_a5` was caught **by a human reading trajectories** — the agent failed for days, that failure was only a *signal*, and the diagnosis ("the Pi instance carries the sup metric") came from manual inspection in the third pass, when only 11 problems remained and "manual inspection of trajectories was possible". No machine flagged it.

So the generalisation is not "proofs find bad specifications". It is: **a failed proof attempt is evidence that something is wrong and carries no information about what**; turning that evidence into a verdict required either a disproof (rare; only when false) or an expert with time.

The deeper point: `2013_a5` was a *true* theorem about the *wrong object*. Elaboration, `#print axioms` and the `pp.all` identity check all compare the proof to the statement; nothing compares the statement to the informal problem. The benchmark's own defence against the nearest attack (an agent rewriting the statement) was **anchoring** — freeze the statement, compare the elaborated type character-for-character. A provenance mechanism, not a proof mechanism, and the only reason "672/672" means anything.

### 2.4 PutnamBench's own statistics

Current README: **1724 formalizations** — Lean 4 **672**, Isabelle **640**, Coq **412**. The paper (arXiv:2407.11214v2, NeurIPS 2024 D&B) instead states **1692 formalizations of 640 theorems**, with "640 formalizations in Lean 4 and Isabelle, and 412 in Coq": at paper time Lean 4 was also 640, and has since grown to 672. So "672/672" is a claim about a *snapshot*, and it equals the current Lean 4 count exactly — both numbers must be quoted with a date or the claim silently becomes about a moving target.

The figure **346 of 672** is absent from both the README and the paper, but it is stated on the benchmark's own leaderboard page: "346 of the 672 problems contain an answer placeholder that the prover must infer." The same page exposes a split the README does not, and it changes what "672/672" means: `lean-wsolution` is labelled "Lean with answer — answer placeholders pre-filled (out of 672)", `lean-nosolution` is "no answer — answer placeholders not provided". The NEAR AI entry is filed under `lean-wsolution`; the only entry reporting 672 on `lean-nosolution` is Midas Prover (added 2026-09-12, mean $6.17 and 31 min per problem, total $4,144.29). So the harness solved the *factored* form — answer written into the statement — which is strictly easier than producing the answer, and a 672/672 headline that omits the track is not comparable to one that names it.

---

## §3 Where rigid verification is deployed and pays

| Case | What was proved | Cost | Explicitly out of scope / trusted |
|---|---|---|---|
| **CompCert** | semantic preservation: compiled assembly behaves as the C semantics prescribes, for all programs, in Coq | **42,000 lines of Coq, ~3 person-years**; 14 % algorithms, 10 % semantics, **76 % proof** | upstream "a parser, type-checker and simplifier … based on the CIL library"; downstream the PPC printer plus "the system's assembler and linker" |
| **seL4** | functional correctness, binary correctness, integrity, confidentiality (no unauthorised information flow) | **1.3 M lines of proofs**, maintained since 2009 | assembly, boot code, machine interface, hardware, DMA — a first-class published page, "where manual validation and scrutiny can focus" |
| **Cedar (AWS)** | the *design*: "a sound and complete logical encoding, which enables precise policy analysis, e.g., to ensure that when refactoring a set of policies, the authorized permissions do not change"; modelled and proved in Lean | not quantified in the abstract | the Rust implementation's conformance; whether a policy expresses the intended business rule |
| **IronFleet** | safety **and** liveness of two full implementations (IronRSL Paxos RSM, IronKV sharded store), "all the way down to the bytes of the UDP packets", tolerating drop/reorder/duplication | not quantified in the fetched text | "the spec for each system is trusted", the main event loop, **Dafny**, the .NET compiler and runtime, and message integrity (no tampering with packets/headers) |
| **WireGuard** | key-exchange security properties in **Tamarin**: "unbounded verification of security protocols modulo an equational theory", against a Dolev–Yao adversary | not quantified | the implementation, timing, memory safety, and computational soundness of the symbolic abstraction |
| **KEVM** | "an executable formal specification of the EVM's bytecode stack-based language built with the K Framework", evaluated against the official Ethereum test suite | not quantified | whether a contract implements the intended instrument — the paper itself cites "a series of costly bugs and exploits" in a market it puts at ~$100bn and 500k daily transactions |

Two deployment facts worth keeping. CompCert was **qualified for the ATR 42/72 (MFC_NG) in March 2026**, with DO-178C / DO-333 / DO-330 credits claimed for the first time from compiler usage, and a July 2023 release fixed "minor issues in the **unverified** C front-end" — the trusted base is real, not theoretical. seL4's fact sheet claims **"0 violations of verified properties since proof completed in 2009"**: a project claim, not an independent audit.

**Common shape.** Every case proves a property of an artifact against a statement its own authors wrote, in a domain where the statement is short, stable, and owned by the people writing the code; every case publishes its trusted base; none claims to have validated that statement.

---

## §4 Where semantic / model-based checking is deployed and pays

| Technique | Catches | Cannot catch | Published evidence |
|---|---|---|---|
| **PBT / MBT** | violations of properties you could state, including inputs no example-based test reaches | properties you did not write; unreachable inputs; outputs needing an oracle | Quviq QuickCheck on an industrial **Megaco** stack: "detected faults that had not been detected by other testing techniques", and "**we found unclarities in the specifications**" — qualitative, no control group, yet enough for Ericsson to fund a larger study |
| **TLA+ / PlusCal** | design-level concurrency and fault-tolerance bugs | anything unstated; code-level defects; spec fidelity | AWS since 2011: **10 systems, 7 teams** — S3 804 lines → 2 bugs; S3 redistribution 645 → 1 bug then another in the first fix; DynamoDB 939 → 3 bugs needing traces up to **35 steps**; EBS 102 → 3 bugs; lock-free structure 223 → "improved confidence **though failed to find a liveness bug, as liveness not checked**"; replication 318 → 1 bug plus a verified optimization |
| **Alloy / Event-B** | inconsistency and missing cases in a design, cheaply and early | that the abstraction is the right one | **no quantitative claim made here** — not fetched this session |
| **Dafny / Why3** | contract violations, index and termination obligations; forces the contract into writing where it can be criticised | the parenthetical in "provably correct code **(w.r.t. specifications)**" | Dafny's own description; IronFleet's assumption list shows the real trusted base — tool, .NET, runtime, spec |
| **Policy engines (OPA/Rego, Cedar)** | inconsistency, permission regressions across refactors, type/attribute errors, dead rules; whether one policy set is more permissive than another | whether the policy is the rule the organisation meant | **no measurement found**; adoption evidence is circumstantial — say so rather than dressing it up |
| **Runtime verification** | violations on *observed* traces, in production, without a whole-system model | unobserved traces; any guarantee of absence; alarm fatigue when the property encodes the wrong abstraction | descriptive only; no effectiveness measurement cited |
| **LLM spec mining** | candidate postconditions that do discriminate wrong code | whether the postcondition is *true* — it is checked against a test suite | Endres et al.: best variant **77 % test-set correct**, a test-set-correct postcondition for **96 % of problems (158/164)**, catching **64 real Defects4J bugs** |

Three honest notes. First, the TLA+ row is the strongest evidence in this column: quantitative, published by practitioners, and including the authors' own negative result. Second, the LLM row is this brief's argument in miniature — *test-set correct* is correctness against an oracle, and the authors claim only that it "largely corresponds to true correctness", an empirical claim about their dataset. A postcondition that is test-set correct and subtly wrong passes the check and then rejects correct code forever; that is the spec gap arriving through the door marked "automation". Third, the Megaco result is the cleanest demonstration that writing properties performs **validation**: the specification was ambiguous, and formalising it found the ambiguity.

---

## §5 The hybrid pattern that works

Ordered by cost per unit of confidence. No organisation in §3–§4 runs one rung only.

**(a) Anchor to an artifact.** Fix what is claimed: byte range in a pinned document, hash of the statement, revision of the corpus. Cheapest, the only rung that survives the artifact changing, and the rung that would have caught §2.2 — `2013_a5` was anchored to nothing, so nothing could notice it had drifted. Catches drift, revision mismatch, unverifiable paraphrase. Cost ≈ 0.

**(b) Check internal coherence mechanically.** Parse, type, resolve references, disjointness, totality, coverage arithmetic, unresolved conflicts. Decidable, fast, exhaustive over the artifact; catches malformed artifacts and undeclared gaps; says nothing about the world.

**(c) Check correspondence to a declared model by sampling or property tests.** Generate scenarios, compare against an independent decision procedure or second implementation, shrink failures. Where conformance is actually established, and where the oracle problem bites hardest.

**(d) Prove narrowly, where the property is genuinely formalisable.** High and superlinear cost; covers the whole quantified domain; worth it only when (b) and (c) cannot reach the property at all.

| Property shape | Rung | Why |
|---|---|---|
| "this span exists, uniquely, in this pinned revision" | (a) | decidable, no model needed |
| "these two positions cannot both hold"; coverage arithmetic; "no undeclared escape" | (b) | internal, finite, exhaustive |
| "on these 200 scenarios the encoding agrees with the decision procedure" | (c) | needs an oracle, but a cheap one exists |
| "for all runs, under an adversary with capabilities C, X is preserved" | (d) | infinite domain, short stable statement, high cost of error |
| "the parties' obligation survives assignment" | (c) at best, against a declared model | the predicate is contested natural language; no oracle |
| "this clause is lawful" | none | not a property of an artifact |

**A proof is justified** when all five hold: the property is closed (no free variables pointing at the world); the domain is infinite or combinatorially vast; the statement is short and rarely revised, since proofs amortise over their lifetime; one escaped defect costs more than the proof; and the trusted base is small enough to be read.

**A proof is money wasted** when any holds: the statement is the thing in dispute (you would prove a contested reading); the predicate is natural-language-laden ("reasonable", "material", "good faith"); the spec changes faster than the proof; a property test over a decidable model catches the same class; or the property is about the artifact's *honesty* rather than its behaviour — those are rung (a) problems in a proof's clothes. The characteristic failure of the ladder is climbing too high: rung (d) on a rung (a) problem yields a true theorem about a statement nobody can trace to a text, which is the most expensive way to be wrong.

---

## §6 What LLMs change, and what they do not

**Production cost, by orders of magnitude.** At submission prices: **$111.85 total** for **724 attempts across 672 problems**; per problem **mean $0.17, median $0.04, max $11.18** (`putnam_2021_a6`, 4 attempts, solved on step 5,411 of a 78-hour run). At current official DeepSeek off-peak prices, **$331** (mean $0.49, median $0.10, max $42.19). The same trajectories on other models: **GPT-5.5 $11,000** (mean $16.50, max $891.33), **Sol $8,257** (mean $12.29, max $687), **Fable $20,644** (mean $30.72, max $1,718). Solved-set model split: V4 flash 653, V4 pro 19. What got cheap is the *tail* — the longest run took over three days and still cost about $11. Note what the harness had to add to make cheap generation usable: a verifier the agent could not talk its way past, and a stopping rule it did not own (3,423 refused quit attempts). The generator was not the hard part.

**Not the validation problem.** A model that writes a wrong statement gets a true proof of the wrong statement, for $0.17. Both PutnamBench defects are exactly that — one statement false, one faithful to nothing — and both were found by failure, not by generation. Cheaper proof production raises the value of the artifact that says *what* was proved, which is rung (a).

The legal evidence agrees, from this repository's own collection: legal hallucinations occur "between 58 % of the time with ChatGPT 4 and 88 % with Llama 2" on specific verifiable questions about random federal court cases; models "often fail to correct a user's incorrect legal assumptions" and "cannot always predict, or do not always know, when they are producing legal hallucinations" (arXiv:2401.01301). RAG-equipped legal tools reduce this without removing it — Lexis+ AI and Westlaw's tools "each hallucinate between 17 % and 33 %", and the providers' "hallucination-free"/"eliminating" claims are "overstated" (arXiv:2405.20362). The operative clause is the last: a system that cannot reliably report its own uncertainty cannot decide when to refuse, so refusal must be a property of the checker, not of the model. The deliverable is the check; the model is a candidate generator whose output is a hypothesis until something mechanical accepts it — already this repository's rule (`AGENTS.md` §9).

---

## §7 Consequences for LexSpec

Layer names are [`00-CHARTER.md`](00-CHARTER.md) §2 (L1 surface, L2 model, L3 inference, L4 provenance).

1. **L4 provenance is fully mechanisable now, and is the only layer where LexSpec can be exhaustive.** Span existence, uniqueness (`S2_SPAN_AMBIGUOUS`), revision pinning and `text_sha256` agreement are decidable properties of finite byte strings — rungs (a)+(b), and where the differentiation actually lives. The PutnamBench harness reached the same conclusion from the opposite direction: its defence against statement-rewriting was not a proof but a character-identical comparison of the elaborated type against a frozen statement. `S2_*` is that mechanism with a stronger target — anchoring to a corpus span rather than to a previous copy of itself.

2. **L1 surface is mechanisable only as a schema/parse check.** Field well-formedness, `bearer` resolution, `action.open` as a boolean: yes. That the sentence was understood: no, and no tooling makes it so — this is validation and stays with the human encoder. An unclosed term yields `OPEN_TERM` plus a coverage debit, never a pass.

3. **L2 model is mechanisable as a typecheck, not as a judgement.** That an atom names one of the eight Hohfeldian positions, that a counterparty-requiring relation has one, that an absolute relation does not: checkable. That a permission was correctly classified instead of silently becoming a duty — the charter's named failure for this layer — is not checkable from inside the encoding. The type discipline raises the cost of the error and makes it visible; it does not remove it.

4. **L3 inference is mechanisable only relative to the declared encoding.** Conflict detection and `conflicts_policy` completeness are rung (b): the checker verifies that every conflict is accounted for, "**not that it is correct**" ([`10-SPEC-v0.1.md`](10-SPEC-v0.1.md) §7) — the completeness/soundness split of §1.5 applied to conflict resolution, and it should stay in the spec verbatim.

5. **What the incident implies for "anchor or refuse", specifically.** Both defects were *unanchored statements*: `1974_b1` was anchored to a predicate that admitted degenerate configurations; `2013_a5` was anchored to nothing, so a true theorem about Busemann–Hausdorff measure could be reported as a theorem about Euclidean area. Neither was detectable by any proof-side check, and both would be **refused** by a rule requiring an unambiguous span in a pinned text plus a closed term for every symbol in the predicate. The rule is therefore not a bureaucratic precondition on proving; it is the only defence that operates on the failure mode that actually occurred at the frontier. Two consequences: coverage must never be computable in a way a malformed atom improves (the current denominator — every object in `atoms[]`, §8 — is right for this reason); and a failed *proof* attempt must produce a refusal code, not a warning, since "we could not close this" is the same class of event as the agent that could not prove `1974_b1`.

6. **May LexSpec ever attach a proof assistant? It may, under a narrow stated condition, and never as a verdict upgrade.** The charter does not promise one and does not forbid one — non-goal 3 defers it to "a declared seam", and this paragraph is what that seam must satisfy if it is ever used. The condition: the prover attaches **only to L3**, over **only** properties internal to the encoding, with the obligation's statement **derived from** the anchored atoms rather than supplied beside them. Qualifying: no atom is simultaneously permitted and forbidden under one interpretation; delegation and authority chains are acyclic; temporal intervals are consistent; coverage arithmetic is monotone under atom addition. Not qualifying, ever: "this clause is lawful", "this obligation survives assignment", "the parties intended this" — no closed statement exists, and a proof of a closed approximation is the `2013_a5` error with extra steps. Nothing in v0.2 depends on this paragraph becoming true.

7. **A proof must never raise a verdict.** `REFUSED` → `CHECKED` → `CHECKED_ANCHORED` is ordered by anchoring and closure, and no theorem proving can close an open term or find a span. A prover's output belongs beside the verdict with its own trusted base listed, and its absence must not lower the verdict. The moment a proof can raise a verdict, the project sells rung (d) confidence for rung (a) work.

8. **Publish the trusted base, CompCert/IronFleet style.** LexSpec's list is short and should print with every verdict: the JSON parser, the sha256 implementation, the corpus files as pinned, and the human's reading of the span. Everything else is checked.

---

## Appendix A — claims I could not verify

| Claim | Status | What would close it |
|---|---|---|
| 346 of 672 Lean problems contain an answer placeholder | **verified 2026-10-28** on the benchmark's leaderboard page (not in README or paper) | closed — the leaderboard also supplies the `lean-wsolution` / `lean-nosolution` split used in §2.4 |
| PBT reduces field defect rates measurably | `[unverified]` — no controlled study found; the Quviq case study is qualitative | a controlled industrial study with defect-escape rates |
| Policy engines reduce defects in deployment | `[unverified]` — adoption evidence only | published pre/post incident or audit data |
| Event-B / Alloy deployment numbers | **not claimed** | the specific project's own publication, with the property proved |
| IronFleet proof-to-code line ratio | `[unverified]` — no "lines of proof" match in the paper text | a §-level quote from the SOSP evaluation section |
| Verdi (PLDI 2015) specifics | **not claimed** — sibling of IronFleet, not fetched | fetch the paper and quote its guarantees |
| seL4 "0 violations since 2009" | project's own claim, not independently audited | an independent incident review |
| PutnamBench 1724 vs paper 1692 | **resolved 2026-10-28**: the arithmetic closes — paper 640 Lean + 640 Isabelle + 412 Coq = 1692; README 672 + 640 + 412 = 1724, and the difference is exactly 32 Lean 4 problems added after publication (the leaderboard notes that "some new problems have been added since original release") | closed; what remains open is *which commit* a given result was evaluated against, which every entry must state |

## Appendix B — sources

| url | what it is | verified |
|---|---|---|
| https://raw.githubusercontent.com/nearai/putnambench-deepseek/main/README.md | the run's README: 672 claim, both defective formalizations, verifier design, all cost figures | yes |
| https://raw.githubusercontent.com/trishullab/PutnamBench/main/README.md | benchmark README: Lean 4 672 / Isabelle 640 / Coq 412, 1724 total | yes |
| https://arxiv.org/abs/2407.11214 | PutnamBench paper v2 (NeurIPS 2024 D&B): 1692 formalizations of 640 theorems | yes |
| https://arxiv.org/html/2407.11214v2 | full text; source of the "factor the solution out of the theorem statement" wording | yes |
| https://compcert.org/ | project site: 2026 ATR 42/72 qualification (DO-178C/DO-333/DO-330); 2023 unverified-front-end fix | yes |
| http://gallium.inria.fr/~xleroy/publi/compcert-CACM.pdf | Leroy, *Formal verification of a realistic compiler*, CACM 2009: 42,000 lines Coq, ~3 person-years, 14/10/76 %, unverified parser and printer | yes |
| https://sel4.systems/Verification/ | properties proved, and the assumptions list (assembly, boot, machine interface, hardware, DMA) | yes |
| https://sel4.systems/About/fact-sheet.html | 1.3 M lines of proofs; "0 violations … since 2009" (project claim) | yes |
| https://arxiv.org/abs/2403.04651 | Cutler et al., *Cedar*: Lean model, sound-and-complete encoding, validator | yes |
| https://web.eecs.umich.edu/~manosk/assets/papers/ironfleet-sosp15.pdf | Hawblitzel et al., *IronFleet*, SOSP 2015: safety and liveness, IronRSL/IronKV, §2.5 assumptions | yes |
| https://wireguard.com/papers/wireguard-formal-verification.pdf | Donenfeld & Milner: Tamarin, Dolev–Yao, unbounded modulo equational theory | yes |
| https://fsl.cs.illinois.edu/publications/hildenbrandt-saxena-zhu-rodrigues-daian-guth-moore-zhang-park-rosu-2018-csf.pdf | Hildenbrandt et al., *KEVM*, CSF 2018 | yes |
| https://www.amazon.science/publications/how-amazon-web-services-uses-formal-methods | Newcombe et al., CACM 2015 — landing page | yes |
| https://cdn.amazon.science/67/f9/92733d574c11ba1a11bd08bfb8ae/how-amazon-web-services-uses-formal-methods.pdf | same paper, full PDF: 10 systems, 7 teams, per-system table, liveness caveat | yes |
| https://research.chalmers.se/en/publication/115891 | Arts/Hughes/Johansson/Wiger, Quviq QuickCheck on Megaco (Erlang Workshop 2006) | yes |
| https://dafny.org/ | "provably correct code (w.r.t. specifications)"; targets C#/Java/JS/Go/Python | yes |
| https://www.openpolicyagent.org/docs/policy-language | OPA docs: Rego as Datalog-inspired declarative queries over structured data | yes |
| https://arxiv.org/abs/2310.01831 | Endres et al.: 77 % / 96 % (158/164), 64 Defects4J bugs | yes (PDF v2) |
| https://arxiv.org/abs/2401.01301 | Dahl et al., *Large Legal Fictions*: 58 % (GPT-4) to 88 % (Llama 2); false-premise correction failure | yes |
| https://arxiv.org/abs/2405.20362 | Magesh et al., *Hallucination-Free?*: 17–33 % for Lexis+ AI / Westlaw; provider claims "overstated" | yes |
| https://trishullab.github.io/PutnamBench/leaderboard.html | benchmark leaderboard: the `lean-wsolution` / `lean-nosolution` split, "346 of the 672 problems contain an answer placeholder", featured "all 672 solved" ranking | yes |
| https://github.com/trishullab/PutnamBench/blob/main/docs/results.json | leaderboard data as JSON: 52 entries, per-method solved counts, dates, cost budgets, notes (NEAR AI 672 at mean $0.17; Humanfia 672 at $44.5; Forall 672 at $3.52; Midas Prover 672 no-answer at $6.17) | yes |
| https://github.com/nearai/putnambench-deepseek | the run's repository (canonical link; the README clone URL points at `SkidanovAlex/putnambench-deepseek`) | yes |
| https://www.wireguard.com/formal-verification | WireGuard's own verification page — **not opened**, cited only as the project's pointer | no |
| https://dl.acm.org/doi/10.1145/1159789.1159792 | ACM DL record of the QuickCheck paper — consulted for existence; abstract taken from the Chalmers record | no (paywalled) |

**Counts.** Rows 25: verified **yes** 23 (one of those qualified as PDF-only), **no** 2 (retained as evidence). Claims carrying an `[unverified]` marker: **3** (PBT's field effect, policy-engine effect, IronFleet's proof ratio), each with the action that would close it; two further rows are marked "not claimed". Two items that were open when this brief was drafted were closed on the same day and are marked resolved in place: the answer-placeholder count, and the 1724-vs-1692 discrepancy.
