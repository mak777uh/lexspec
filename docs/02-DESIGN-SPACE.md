# 02 — Design space: prior art, and the one decision it forces

Status: working document (a *map*, not a constitution). Access date for every source: 2026-10-28. Companion: [99-SOURCES.md](99-SOURCES.md), where each URL carries a verification grade.

**Precedence.** [`docs/10-SPEC-v0.1.md`](10-SPEC-v0.1.md) and [`docs/11-REFUSAL-CODES.md`](11-REFUSAL-CODES.md) are canonical. Where this file and the spec disagree, the spec is right and this file is a bug. This file explains *why* the spec's choices are the ones the prior art leaves standing.

**Numbers.** No number here is a measurement. Coverage, atom counts and check counts come from `tools/lexspec_status.py` with its command, environment and commit recorded (`AGENTS.md` rule 1). Anything quoted without that provenance is an illustration, not a result.

This document exists so that LexSpec does not reinvent a wheel and does not repeat a known failure. It is written for a reader who is paid to find the error.

## 1. The problem, stated precisely

"Legal text → machine-checkable" is not one problem. It is at least four, and they fail independently.

| # | Sub-problem | Question it answers |
|---|---|---|
| (a) | **Syntactic normalization** | Where does the provision begin and end; what is a definition, a proviso, an amendment, a list item? |
| (b) | **Semantic modelling of norms** | What legal position is this — right, duty, privilege, power — held by whom, against whom, over what? |
| (c) | **Reasoning about norms** | Given these norms and these facts, what follows, and what defeats what? Deontic + temporal + defeasible at once. |
| (d) | **Anchoring to an authoritative revision** | Which exact characters, in which exact version, does this atom claim to encode? |

The four are ordered by dependency but not reducible to each other. (a) does not give you (b): a perfectly parsed section says nothing about whether it creates a duty. (b) does not give you (c): you can type a duty correctly and still not know what happens when a later section overrides it. None of them gives you (d), which is a separate, empirical, bookkeeping obligation about the real world.

Akoma Ntoso keeps content, structure, semantics and presentation as four distinct levels so the same fragment can be annotated several times without being re-marked up ([AknCore §4.5](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/akn-core-v1.0-part1-vocabulary.html)) — the right architecture, and an admission that no single artefact does all four. LexSpec v0.1 occupies (b) and (d) and explicitly refuses (a) and (c): [spec §11](10-SPEC-v0.1.md) items 1–2.

### 1.1 What the tooling world collapses

1. **"Parse and you have modelled"** — (a)→(b). Output is a tree with a `type="obligation"` attribute that no semantics constrains.
2. **"Model and you can reason"** — (b)→(c). LegalRuleML resists this by design: it "is independent from any legal ontology and logic framework" ([§2.3](https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/legalruleml-core-spec-v1.0.html)). It gives a vocabulary for norms and a *mapping* to logic; not a logic.
3. **All four into one "answer"** — the LLM collapse. One opaque step consumes text and emits an assertion, so (a)–(d) become indistinguishable and unauditable in principle.

(d) is the one usually dropped without anyone noticing, because dropping it costs the builder nothing and the reader everything: an unanchored verdict cannot be checked against the statute, so it can only be believed.

### 1.2 Why the collapse produces confident nonsense

Not because "the model is bad". Four substitutions do the work:

- **Modality becomes material implication.** "The seller must deliver within 14 days" becomes `deliver → within14`, which is true when nobody delivers anything. L4's docs state the correct shape: a regulative rule "decides nothing by itself", it is evaluated against a start time and an event stream, and its outcomes are `FULFILLED`, breach, or a residual obligation ([legalese.com](https://legalese.com/l4/concepts/legal-modeling/regulative-rules)).
- **Defeat becomes conjunction.** A proviso ("unless subsection (3) applies") is dropped or ANDed in, so the exception narrows nothing.
- **The anchor becomes a citation string.** A citation looks like an anchor and is not one: it survives the text being amended and cannot be checked.
- **The gap becomes silence.** Nothing reports what was skipped, so a pass over 4% of atoms is indistinguishable from one over 96%.

The result is fluent, cites something real-looking, and is unfalsifiable by the person best placed to falsify it. The empirical size: five leading models hallucinate on 58% (GPT-4) to 88% (Llama 2) of specific verifiable questions about random federal court cases, and they "cannot always predict, or do not always know, when they are producing legal hallucinations" ([Dahl et al. 2024](https://arxiv.org/abs/2401.01301)). A system that does not know when it is wrong cannot be made safe by asking whether it is sure — which is why LexSpec's LLM surface is a statement generator under a checker, never a verdict.

*Still unknown:* whether (b) and (c) can share one representation without (d) becoming unrepresentable. Every system below that does (b)+(c) well has no (d); the one that does (d) well has no (b)+(c).

## 2. Prior art

Per entry: what it does · what it refuses · what we borrow · what we refuse · the failure mode it is known for.

### 2.1 LegalRuleML (OASIS) and the RuleML family

OASIS Standard, 30 August 2021 ([LRML Core v1.0](https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/legalruleml-core-spec-v1.0.html)).

**Does.** Extends RuleML with `Obligation`/`Permission`/`Prohibition` and `Bearer`/`AuxiliaryParty` roles; `DefeasibleStrength`/`StrictStrength`/`Defeater`; an `Override` relation (`@over`/`@under`); `TemporalCharacteristic` pairing a `Legal Status` ("in force", "applicable", "valid") with a `Status Development` at a `Time`; `SuborderList`, whose later members hold only once earlier members are violated; and `Violation`/`Penalty`/`Reparation` for the remedial layer. Its requirement R4 is *isomorphism*: "a one-to-one correspondence between collections of rules in the formal model and the units of (controlled) natural language text".

**Refuses.** To fix a logic — conformance is against RelaxNG/XSD plus an RDFS metamodel. It also refuses to own the text: sources are identified by `LegalSource`/`Reference`/`@refIDSystemName`, which is a citation, not a span.

**Borrow.** The ontology, largely wholesale: strength on rules rather than one global priority order, `Override` as data, `Legal Status` separated from `Status Development` (being in force is not the event of coming into force), `SuborderList` as contrary-to-duty ordering rather than a reasoner special case.

**Refuse.** That isomorphism is achievable by annotation. R4 is a design requirement to "ease validation and maintenance"; nothing in the schema checks it. A schema-valid document can be a faithful encoding or a fabrication, and the artefact does not let you tell.

**Failure mode.** Cost and unfalsifiability: large XML surface, expert author, correctness asserted by that author. Precisely what (d) exists to prevent, and why `S2_*` are refusals rather than warnings.

*Still unknown:* whether `Override` is transitive, and whether `SuborderList` order is checked statically or at evaluation time — both are described operationally, neither normatively.

### 2.2 Akoma Ntoso (OASIS LegalDocML) and XML pipelines

OASIS Standard, 29 August 2018 ([AknCore v1.0 Part 1](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/akn-core-v1.0-part1-vocabulary.html)); Part 2 carries the schemas; namespace `http://docs.oasis-open.org/legaldocml/ns/akn/3.0`.

**Does.** A document model, not a norm model: FRBR identity (Work/Expression/Manifestation), identifiers for every fragment, hierarchy vocabulary, and machinery for change — §5.7 versioning, §5.10.2 `activeModifications`, §5.10.3 `passiveModifications`, §5.10.10 `TemporalData`, §5.8 cross-references.

**Refuses.** Semantics in our sense: no deontic operators, no consequence relation, no notion of a norm being satisfied or violated. "Machine readable" means structure and metadata, and the spec says so.

**Borrow.** Three things, all load-bearing for §3. (i) Anchor structurally, not by character offset into a PDF. (ii) Markup is *editorial*, not authorial — "Markup is the act of adding annotation and labels", metadata items "are editorial additions" (§4.3.2–4.3.4). (iii) Therefore an electronic version is not the law: "All conversions into electronic formats … have an authoritative status that is of lesser authoritativeness than the official form" (§4.3.1). Point (iii) is exactly why our spec pins a corpus by sha256 of the bytes: the URL is provenance, the hash is identity, and a changed corpus file voids the old verdict.

**Refuse.** Treating the XML as the corpus. It is a claim about the corpus. Production point-in-time consolidation — the Laws.Africa Content API serves "point-in-time versions, XML, HTML, PDF … lifecycle metadata" ([developer guide](https://developers.laws.africa)) — is something to consume, not reimplement.

**Failure mode.** Editorial drift: two publishers produce two valid expressions of the same Act with different `eId`s, and neither is wrong.

*Still unknown:* whether AKN fragment identifiers are stable enough to anchor across publishers. Untested against two independent publishers; until tested, our anchor stays a plain substring plus a content hash — dumber, and it survives re-publication.

### 2.3 Catala (law-as-code, prose-aligned, default logic)

Merigoux, Chataing, Protzenko, *Catala: A Programming Language for the Law*, ICFP 2021, [DOI 10.1145/3473582](https://doi.org/10.1145/3473582); full text [arXiv:2103.03198](https://arxiv.org/abs/2103.03198) (Inria, ENS Paris, Microsoft Research).

**Does.** A language for the fragment of law that is "an algorithm in disguise": tax, benefits, penalties. It is prose-aligned — designed "to follow the existing structure of legal statutes, enabling a one-to-one correspondence between a legal paragraph and its corresponding translation" — and literate: statutory prose sits immediately above its transcription. Semantics are **prioritized default logic**: each definition has an optional default case plus arbitrarily nested exceptions, and priority is static, "encoded … in the surface syntax", derived from the syntax tree rather than resolved at run time. If two definitions apply and no priority separates them, execution aborts with a fatal conflict error.

**Refuses.** Interpretation, explicitly: it targets cases "where entities are well-defined, and where human appreciation, judgement or interpretation are not generally expected". It has no deontic vocabulary — no `Obligation`, only computed values. It refuses non-termination ("not Turing-complete, purposefully") and dependency cycles. It refuses to guess: ambiguity is fatal, not a warning.

**Borrow.** The conflict discipline, the most transferable idea in the survey: *an unresolvable conflict is a fatal error, not a preference*. That is our `S6_CONFLICT` under `conflicts_policy.default = "report"` — every conflict refuses, because no norm silently overrides another ([spec §7](10-SPEC-v0.1.md)). Also prose-alignment, and the honest scoping.

**Refuse.** The claim-by-omission that a verified toolchain verifies the law. Their F⋆ proof proves *compilation is correct*; not that the program matches the statute. That gap is the whole of §3 and the reason `not_claimed` is a required field.

**Failure mode.** Encoding cost, admitted by the authors: modelling "is labor-intensive, owing to all of the implicit assumptions present in what is seemingly 'just legalese'", and is "best achieved through pair-programming, in which a Catala expert transcribes a statute with the help of a legal expert." Also: for a provision that is not an algorithm, Catala has nothing to say.

*Still unknown:* what fraction of a real Act is "an algorithm in disguise". The case studies were chosen because they are; we have no denominator, and that denominator is the one coverage needs.

### 2.4 L4 (SMU Centre for Computational Law)

Docs at [legalese.com/l4](https://legalese.com/l4); implementation [smucclaw/dsl](https://github.com/smucclaw/dsl) ("Domain Specific Languages for Computational Law", Haskell, active since 2020).

**Does.** Separates *constitutive* rules ("is the borrower a small business?") from *regulative* ones ("what must the borrower do now, given what has happened?"). A regulative rule is a value of type `DEONTIC party action`, written `PARTY … MUST/MAY/SHANT … WITHIN n HENCE … LEST …`, and it "decides nothing by itself. It is a contract that waits until it is given a start time and a sequence of events". Evaluation is `contract × (start time, events) → verdict`, with three outcomes, not two: `FULFILLED`, a breach, or a **residual obligation** — the partly-performed contract as a first-class, storable, resumable value.

**Refuses.** To resolve statutory conflict: its unit is a contract against an event stream, not provisions against each other. It also refuses temporal generality in terms the docs state plainly: "There is no syntax for counting a deadline from some other named event, and none for a deadline on a fixed date; build the timing by chaining obligations with `HENCE`." And it is not a text standard: the prose is not carried in the artefact.

**Borrow.** The trichotomy — a boolean verdict is a lie about a partly performed obligation. Our `REFUSED | CHECKED | CHECKED_ANCHORED` plays that role one level up: not true/false/unknown but three statements about how much of the claim survived. Also the explicit event triple `(party, action, time)`: facts are not free-form, and that is what makes a verdict reconstructible.

**Refuse.** The artefact-as-program framing, and the absence of an anchor from the design. L4's docs do not, in the pages read, tie a rule to an article revision — a gap we cannot inherit, and why our atoms carry `anchor` rather than provenance prose.

**Failure mode.** Residual states invite silence-as-compliance: "still waiting" is easy to read as "fine". `CHECKED` has the same hazard, which is why `THIN_COVERAGE` is its own code with its own sentence — it does not mean the statement is wrong, it means it is too thin for the verdict its author wants.

*Still unknown:* how L4's default/exception reasoning interacts with temporal evaluation. The docs list an "Exceptions and defaults" page we did not read, so we claim nothing about it.

### 2.5 Statute→logic pipelines: s(LAW), Blawx, Logical English, PROLEG

- **Text→formula pipeline (CCLAW/JURIX).** Ranta, Listenmaa, Soh, Wong, *An End-to-End Pipeline from Law Text to Logical Formulas*, JURIX 2022, [DOI 10.3233/FAIA220473](https://doi.org/10.3233/FAIA220473): parse annotated text with a Grammatical Framework grammar, interpret into an "assembly logic" intermediate representation, translate to back-end logics. Stated goal is directly relevant: "rule-based and explainable", able to deliver "useful results from day one, but allows subsequent refinements and variations" — partiality designed in.
- **Blawx** (Morris), *Web-based User-Friendly Rules as Code*, GDE 2022 ([CEUR Vol-3193 paper 4](https://ceur-ws.org/Vol-3193/)): rules-as-code authoring over goal-directed answer set programming (s(CASP)).
- **Logical English** (Sartor, Dávila, Billi, Contissa, Pisano, Kowalski), *Integration of Logical English and s(CASP)*, same volume ([paper 5](https://ceur-ws.org/Vol-3193/)): a controlled natural language compiling to a logic program, so readable and executable form are one object.
- **Defeasible reasoning in ASP** (Lim, Mahajan, Strecker, Wong), same volume ([paper 3](https://ceur-ws.org/Vol-3193/)).
- **PROLEG today.** Zin, Wehnert, Kong, Nguyen, Fungwacharakorn, Xue, Araszkiewicz, Goebel, Satoh, Nguyen, *Can Legislation Be Made Machine-Readable in PROLEG?*, [arXiv:2601.01477](https://arxiv.org/abs/2601.01477) (4 Jan 2026): one LLM prompt turns GDPR Art. 6 into if-then rules *and* a PROLEG encoding, "legal domain experts" validate and refine, output is executable and explains decisions; it closes by noting "observed limitations".

**Does and refuses, collectively.** Each produces a formal artefact from prose; none binds that artefact to a span, and none claims to.

**Borrow.** (i) The intermediate representation is where the anchor belongs: an IR node can carry a span, a solver term cannot. (ii) Logical English's convergence of readable and executable form is the right target for lawyer acceptance — the same ambition as §4 F1. (iii) PROLEG's workflow, model drafts and expert validates, is the honest description of LLM assistance today; our `AGENTS.md` rule 9 says the same: a model-proposed formalisation is a hypothesis until `lexcheck` accepts it and the anchors resolve.

**Refuse.** That the pipeline's output is a *finding*. Every one of these systems produces an encoding whose fidelity is asserted by its producer; the pipeline moves the assertion around, it does not discharge it.

**Failure mode.** The unvalidated middle: in text → IR → logic, errors at the IR are invisible in the output and unfalsifiable without redoing the work. Same failure as §2.1 in different syntax.

*Still unknown:* **ProLEAP.** We could not verify it — no repository, paper or project page we fetched corresponds to a legal-reasoning system of that name (GitHub search returns only COBOL/VB6 parsers), so we claim nothing. `[unverified]`; verification needs a citable paper or repository. The *name* "s(LAW)" for the CCLAW pipeline is likewise our shorthand and `[unverified]` — the JURIX abstract does not use it.

### 2.6 Deontic logic in computer science

**Does.** Four traditions, often conflated:

1. **Dyadic deontic logic**: `O(φ | ψ)` — obligation conditional on circumstance. Unconditional `O φ` cannot express "if you have borrowed, you must return it" without generating obligations for people who never borrowed.
2. **Contrary-to-duty.** Chisholm's 1963 paradox ([DOI 10.1093/analys/24.2.33](https://doi.org/10.1093/analys/24.2.33)) shows four sentences any lawyer would call consistent — a duty, a duty if the first is violated, and the violation — have no adequate rendering in standard deontic logic without either making the obligation vanish on violation or licensing detachment of the wrong thing. It is the formal shadow of "the obligation survives the breach", which is most of remedies.
3. **Input/output logic** (Makinson & van der Torre, 2000, [DOI 10.1023/A:1004748624537](https://doi.org/10.1023/A:1004748624537)): norms as input/output pairs rather than propositions in possible worlds, which removes "norms that are true" and ought-implies-can artefacts at the cost of needing explicit treatment of permission and norm change.
4. **Defeasible deontic logic**: strength, defeaters, a superiority relation, so a later or more specific norm defeats an earlier one without inconsistency. LegalRuleML's `DefeasibleStrength`/`Defeater`/`Override` is the markup-level form of this tradition (§2.1).

**Borrow.** From (1), obligation is conditional. From (2), violation is a *state*, not a falsification — the same insight as L4's residual obligation from the other direction. From (3), a norm is a rule, not a proposition. From (4), strength and override are data, not hard-coded precedence.

**Refuse.** Picking one. The CTD literature is a live disagreement with legal consequences (does a violated obligation still bind? can a reparation create an obligation?). A checker that silently adopts one and reports "inconsistent" is reporting on its own semantics. v0.1 sidesteps this by having no defeasibility at all (spec §11 item 3) and refusing on conflict (§7).

**Failure mode.** Paradox-driven over-engineering, and its opposite: quietly dropping CTD because it is hard, producing a reasoner correct on the easy majority and wrong exactly where remedies matter.

*Still unknown:* whether a *declared* semantics per corpus is workable, or whether it makes verdicts incomparable across corpora. Open question 6 in §5.

### 2.7 Hohfeld's jural relations as a type discipline

Hohfeld, *Fundamental Legal Conceptions as Applied in Judicial Reasoning* (1913/1917 Yale lectures; collected edition [DOI 10.4324/9781315254821](https://doi.org/10.4324/9781315254821)).

**Does.** Analyses every position into one of eight, in four correlative pairs — right↔duty, privilege↔no-right, power↔liability, immunity↔disability — with opposites that cannot both hold of one bearer for one action, and distinguishes first-order positions (what you may or must do) from second-order ones (who can change them).

**Refuses.** Truth conditions, quantification, time, and any account of how positions are created. It is analytic jurisprudence, not a logic, and its categories are contested in detail.

**Borrow.** The whole layer, as a type discipline. The spec adopts it as the eight-valued `relation` and enforces two consequences mechanically: a relative relation with no counterparty is `S3_MISSING_COUNTERPARTY` ("a duty to the world is not a duty"), and opposite relations on the same bearer/action/counterparty over overlapping time are `S3_OPPOSITE_CONFLICT` ([11-REFUSAL-CODES.md](11-REFUSAL-CODES.md)). This is the cheapest check in the system and the one that justifies a formal layer at all: it catches "A may not do X" next to "A may do X" in one document, with no prover.

**Refuse.** Hohfeld as an ontology of the world. It classifies *positions in a relation*, not facts, and mapping a sentence onto the eight cells is itself interpretive — which is why `terms[]` carries `status: "closed" | "open"` and is reported rather than asserted.

**Failure mode.** Category inflation: everything gets labelled "right" or "duty" and the discipline becomes decoration. The test is whether it ever *rejects* something.

*Still unknown:* whether the four correlatives are exhaustive for civil-law drafting as well as common-law. We have only common-law sources; the shipped corpus is a Russian civil-code fragment, which is a first test of this question rather than an answer.

### 2.8 Temporal legal reasoning: conflicts as declared policy

**Does.** Names three doctrines: *lex posterior* (later prevails), *lex specialis* (more specific prevails), non-retroactivity (a later norm does not reach backwards). In practice courts apply them as rebuttable defaults, not computable functions.

**Borrow.** Declared, not inferred, policy. LegalRuleML's `Override` is the technical form of declared priority; Akoma Ntoso's `activeModifications`/`TemporalData` of declared change. The spec takes this route: `conflicts_policy.default` is `report`, `lex_specialis` or `lex_posterior`, and a declared policy must name the prevailing atom per conflict or the verdict is `S6_UNRESOLVED_CONFLICT`.

**Refuse.** Computing specificity. `lex specialis` requires a judgement that A is "more specific" than B, and that judgement is argued, not measured; a checker that scores it by counting conditions silently encodes a preference about which provision governs. The spec draws the boundary exactly: a declared policy is the author's assertion that the corpus resolves the conflict, and the checker verifies the assertion is **complete**, not **correct** ([spec §7](10-SPEC-v0.1.md)). Retroactivity is not modelled at all (spec §6).

**Failure mode.** Treating the maxims as a total order. They conflict with each other, have exceptions, and are jurisdiction-dependent; a fixed sequence yields confident answers to questions the law leaves open.

*Still unknown, and blocking:* we could not verify a primary-text statement of these doctrines — `ohchr.org` (ICCPR) and `constitution.congress.gov` both returned HTTP 403, and we did not substitute a secondary source. `[unverified]`: needs ICCPR Art. 15 / ECHR Art. 7 text plus a conflicts-of-laws authority.

### 2.9 Proof assistants reaching law: Isabelle/HOL and Lean 4

**Does.** LogiKEy is the mature case: framework, methodology and tool support for designing normative theories by shallow semantic embedding of deontic logics in Isabelle/HOL — Benzmüller, Parent, van der Torre, Artificial Intelligence 2020 ([DOI 10.1016/j.artint.2020.103348](https://doi.org/10.1016/j.artint.2020.103348)), with a public Isabelle/HOL dataset ([DOI 10.1016/j.dib.2020.106409](https://doi.org/10.1016/j.dib.2020.106409)). Lean 4 is "an open-source programming language and proof assistant" with a minimal trusted kernel ([lean-lang.org](https://lean-lang.org/)), Mathlib holding "over a million lines of formalized mathematics". The instructive industrial case is Cedar: "AWS uses Lean and verification-guided development to formally verify Cedar, the AWS authorization policy language", including differential testing against production Rust.

**What a machine-checked norm proof establishes.** Exactly one thing: that the formal statement follows from the formal definitions, in the logic the embedding chose, under the kernel's assumptions. Nothing about whether those definitions are the law. Two consequences bind us. (i) A proof is only as meaningful as the readability of the statement: `theorem t : ∀ x, Obl x → ¬ Perm x` is checkable and useless to a lawyer unless the definitions are legible — hence §4 F1. (ii) Cedar is the right model of *ambition*: the verified artefact is the policy language's semantics, not the correspondence between statute and policy. Even a fully verified engine leaves "does this policy implement §4?" open. LexSpec's answer is not to verify harder but to refuse to answer without an anchor.

**Borrow.** The distinction as a rule: verification is about the encoding, not the text. And LogiKEy's claim that designing a normative theory is a separate formal activity from implementing it — the same separation as §1(a)–(d).

**Refuse.** Scaling a proof assistant to a corpus: mechanizing a full Act in Isabelle/HOL is not a task with a plausible budget, and the result still needs the anchor step. v0.1 has no proof object at all (spec §11 item 7).

**Failure mode.** The verification gap — extensive proof effort on the wrong statement — plus overclaiming by association: "machine-checked" reads to a lay reader as "true".

*Still unknown:* whether any Lean 4 formalization of statutory or deontic norms exists. `[unverified]` — arXiv search found only mathematical and cryptographic Lean work, which is weak negative evidence; closing it needs arXiv + DBLP + Archive of Formal Proofs + the Lean community index searched for "law/legal/deontic".

### 2.10 LLM-based legal checking

Dahl, Magesh, Suzgun, Ho, *Large Legal Fictions*, Journal of Legal Analysis 16(1):64–93 (2024), [DOI 10.1093/jla/laae003](https://doi.org/10.1093/jla/laae003) / [arXiv:2401.01301](https://arxiv.org/abs/2401.01301): hallucination on 58%–88% of specific verifiable questions; models often fail to correct a user's false legal premise; and they "cannot always predict, or do not always know, when they are producing legal hallucinations".

Magesh, Surani, Dahl, Suzgun, Manning, Ho, *Hallucination-Free?*, [arXiv:2405.20362](https://arxiv.org/abs/2405.20362): the first preregistered evaluation of AI legal research tools. Providers' claims that RAG eliminates or avoids hallucinations are "overstated"; Lexis+ AI and Westlaw's tools each hallucinate 17%–33% of the time.

**Borrow.** Self-report is not a confidence signal. Model output must be forced through a channel that can be checked mechanically — a span that occurs exactly once in a hash-pinned file, or nothing — never through a channel that trusts the model's assurance. Also the hallucination typology, as test cases.

**Refuse.** Any design where model output *is* the verdict, and any UI where a confidence score substitutes for a coverage number. RAG roughly halved the rate and did not approach zero; no published evidence supports a purely generative step for high-stakes citation.

**Failure mode.** A plausible citation to a nonexistent authority, and — subtler — to a real authority that does not say what is claimed. A span check catches the first only if the model cannot invent text appearing verbatim once; it catches the second not at all. That residual is why coverage is a number about the *encoding* and `not_claimed` names the gap.

*Still unknown:* whether model assistance materially changes encoding cost. PROLEG suggests draft-then-validate; no source read here quantifies the saving. That is falsifier F3.

### 2.11 What the survey adds up to

| System | (a) normalize | (b) model | (c) reason | (d) anchor |
|---|---|---|---|---|
| Akoma Ntoso | yes | no | no | **yes** (structural, editorial) |
| LegalRuleML | no (delegates) | yes | declares none | by citation only |
| Catala | literate paste | no (no deontic) | yes (default logic) | prose adjacency, not checked |
| L4 | no | yes (`DEONTIC`) | yes (temporal) | not addressed in docs read |
| Statute→logic pipelines | partial | partial | yes | no |
| Deontic logic literature | — | theory | theory | — |
| Proof assistants (LogiKEy) | no | yes | yes | no |
| LLM tooling | implicit | implicit | implicit | none, and claims otherwise |
| **LexSpec v0.1** | **refused** (§11.1) | **yes** (Hohfeld) | **refused** (§11.2–4) | **yes** (sha256 + unique span) |

No row before the last has (b), (c) and (d) together, and the table shows why: each community optimised the two it cared about. LexSpec's bet is that the cheapest credible product drops (c) rather than (d), because (c) without (d) cannot be audited while (d) without (c) still catches real defects.

*Still unknown:* whether that bet is economically sound — whether a checker that refuses entailment is still useful to someone with a budget. This is the v1 question behind F3.

## 3. The one design decision: anchor-or-refuse

Everything above collapses to one commitment, which the spec already implements:

> **Every normative atom carries an exact span in a pinned text revision, or the statement is refused. Every verdict is relative to an explicit encoding, carries a coverage number and an escape list, and states what it does not claim.**

### 3.1 No anchor, no verdict — and an ambiguous anchor is no anchor

The spec requires four conditions before an atom counts as anchored: the corpus handle resolves; the corpus file hashes to the declared `text_sha256`; the span occurs in that file; and it occurs **exactly once** ([spec §5](10-SPEC-v0.1.md)).

The fourth is the condition a reasonable engineer would drop, and it is the one that makes the mechanism work. A span occurring twice does not identify a provision: if one occurrence is later amended, the citation silently re-points to the other, and a citation that can re-point itself is not evidence. So `S2_SPAN_AMBIGUOUS` is a refusal, not a warning — and the remedy is mechanical (widen the span until unique), which is what makes the refusal actionable rather than merely strict. Pinning by hash rather than URL is the same argument one level up: Akoma Ntoso already concedes that electronic versions have "lesser authoritativeness than the official form", so the artefact must name the revision it read, not merely the document.

### 3.2 Verdicts are relative to an encoding

The output is never `φ`. It is `verdict(encoding E, revision R, statement S)`, and it is false, in the ordinary sense, if `E` does not encode the text. This is attribution: the tool reports what its encoding entails, and the encoding is a named, reviewable, versioned artefact with an author, a canonical byte form and a sha256 ([spec §3](10-SPEC-v0.1.md)).

| Verdict | What it asserts |
|---|---|
| `REFUSED` | the statement does not survive checking; read the codes |
| `CHECKED` | consistent and anchored where anchored, but the encoding is incomplete |
| `CHECKED_ANCHORED` | every atom closed and anchored against pinned text |

None of the three is a statement about the law. The spec is explicit that `REFUSED` does not mean unlawful and `CHECKED_ANCHORED` does not mean lawful ([11-REFUSAL-CODES.md](11-REFUSAL-CODES.md), "What a refusal is not").

### 3.3 Coverage and escapes are numbers, not adjectives

```
coverage = |closed atoms| / |atoms|          (0.0 when there are no atoms)
```

An atom is closed when its bearer and counterparty resolve to terms with `status: "closed"`, its `action.open` is `false`, and it is anchored. An atom that is not closed yields an `OPEN_TERM` escape, and the checker compares computed escapes with declared `escapes[]` in **both** directions: `S4_UNDECLARED_ESCAPE` (a silent reduction of coverage in the author's favour) and `S4_STALE_ESCAPE` (a report that looks more cautious than the encoding is) are both refusals. This pair is the most important detail in the spec, because without it coverage is self-reported and therefore worthless.

The denominator is the honest part. Coverage is a number about *the statement*, not the law: 100% coverage of a clause you mis-encoded is 100% coverage of a mis-encoding. The spec says so in §8 and attaches `not_claimed` to every report so the sentence cannot be quoted off.

### 3.4 What this buys

- **Falsifiability.** A hostile reviewer can attack the anchor, the encoding, or the atom inventory without reading the implementation. In every row of §2.11 there is one thing to attack, and it is the author's sincerity.
- **Honest degradation.** Refusal is a designed outcome, not a crash. Catala's fatal-conflict rule is the same discipline one layer down; we extend it from conflicts to anchoring.
- **Comparability.** Two encodings of one article can be compared on verdict, coverage and refusal set, which makes encoding quality an empirical question for the first time.
- **A defensible negative.** "Not checkable, and here is the reason code" is often the most valuable true sentence available.

### 3.5 What this explicitly does not buy

- Not legal advice; it never asserts a provision is valid, enforceable or correctly interpreted. `not_claimed` is part of the verdict, not a disclaimer appended to it.
- Not a discharged encoding obligation. 100% coverage of a wrong encoding is still wrong; the anchor proves *where*, not *what*.
- Not ambiguity resolution; it converts ambiguity into refusal — a loss of information by design that must stay visible as such.
- No unwritten principles (proportionality, good faith, reasonableness), and it cannot: they have no span.
- No guarantee that the pinned revision is operative law: commencement, unconsolidated amendments and savings provisions are outside the anchor (spec §6, §11).
- No inherited semantics: the deontic question stays open, and v0.1 declines to answer it by having no defeasibility rather than by picking a logic quietly.
- No proof: there is no entailment and no proof object in v0.1 (spec §11 items 2, 7).

*Still unknown:* whether the refusal rate is survivable as a product. If a competent encoding of a real Act refuses most of its atoms, the honest number is a business problem — and we do not yet know whether it is 6% or 60%. Measuring it is itself a v1 deliverable.

## 4. What would make this project wrong

Each falsifier has a cheap test that can run before v1; each result is written to `lab/` with date and boundaries (append-only; `AGENTS.md` rules 6 and 9). We should expect at least one to fail.

| # | Falsifier | Cheap test | Kill criterion |
|---|---|---|---|
| F1 | A competent lawyer cannot read a statement without a manual | 3 lawyers, 10 statements plus source articles, no documentation: what does each assert, does it match? | <8/10 correct, or <8/10 agree with the encoding |
| F2 | Coverage cannot be measured honestly | Two annotators independently inventory one short Act's atoms; measure agreement on count and set | >20% disagreement on count, or κ <0.8 on the set |
| F3 | Encoding cost exceeds the value of the check | Time one encoder from reading to `CHECKED_ANCHORED` on 5 articles; count real defects found | Median above the agreed budget **and** zero defects in 20 articles |
| F4 | Refusals are indistinguishable from "I could not parse" | 20 refused statements: a reviewer who has not read the code must name the code and the remedy | They cannot, or two codes cover one cause (needs a split, rule 7) |
| F5 | Anchors drift silently | Mutate one character of the corpus: every dependent atom must refuse. Mutate an unrelated file: nothing may refuse | Any atom still verdicts, or everything refuses |
| F6 | The checker agrees with its author, not the law | A lawyer writes expected verdicts sealed before seeing the encoding; then compare | Divergence on any non-refused atom |
| F7 | Output overclaims | Grep output surfaces for assertions of legality outside a `(verdict, encoding, revision, coverage, not_claimed)` tuple | Any such sentence |
| F8 | It is a parser with a thesaurus | Feed statements whose legal answer is contested | A verdict instead of a refusal |
| F9 | The four sub-problems have silently merged | Can a reviewer change the anchor without touching the encoding, and the encoding without touching the parser? | No |
| F10 | The escape list drifts in the author's favour | Mark one term `open` without updating `escapes[]` in a passing statement | It still passes: `S4_UNDECLARED_ESCAPE` is not firing |

Every falsifier is cheap, none needs the full system, and all test *honesty* rather than capability. That is deliberate: capability failures are recoverable, a system that confidently reports the wrong thing is not.

*Still unknown:* the thresholds. F1's "8/10" and F3's "agreed budget" are placeholders chosen to be arguable; they need calibration against a real Act, and `AGENTS.md` rule 3 means changing one later requires a `lab/decisions/` entry rather than a quiet edit.

## 5. Open questions we must answer before v1

Deliberately *not* the questions v0.1 answers. Where the spec has decided, this list defers to it; every item below is open in spec §6 or §11.

1. **What is the atom when the text is not a clean clause?** A provision creating a duty *and* a power in one sentence has no obvious atom count, and that count is the coverage denominator.
2. **One sentence, two atoms — or two sentences, one atom?** Until fixed, F2 cannot pass and coverage is not comparable across encoders.
3. **Substring anchor or structural identifier?** The substring is dumb and survives re-publication; `eId`-style identifiers are richer and publisher-dependent. v1 picks one and states what breaks.
4. **What is the coverage denominator for a real Act?** Atoms in the Act, in the declared scope, or atoms an annotator could find? Each yields a different, defensible-looking number; only one can be `N %`.
5. **How do we represent defeasibility without importing a semantics?** The biggest gap (spec §11 item 3), and the whole of §2.6 says there is no neutral choice: a declared defeat relation, an explicit `unless` atom, or refusing every atom downstream of a proviso.
6. **Is one declared semantics per corpus acceptable?** If two corpora declare different conflict policies, are verdicts still comparable, or does "checked" mean something different in each?
7. **May two encodings of one article coexist and disagree?** We think yes — it is honest — but then "the verdict" is not a function of the text alone, and every API contract must say so.
8. **What happens across statements?** v0.1 checks each statement alone; `поставщик` in two statements is two terms spelled alike (spec §11 items 4–5). A contract of twelve statements is the normal case.
9. **What is the time model beyond `from`/`until`?** Retroactivity, entry into force distinct from adoption, transitional provisions, suspension (spec §6). Each needs a decision to model or refuse — and refusing is not free, because a refused temporal question can hide a real conflict.
10. **How is refusal represented so it cannot become a silent pass?** `CHECKED` already exists as the weaker verdict; open is what an API returns when the caller asked for `CHECKED_ANCHORED` and got `CHECKED`.
11. **Who reviews an anchor, given that every anchor is an editorial act?** Akoma Ntoso is explicit that markup is editorial; we need a named reviewer role and a record of who accepted which span.
12. **What are the corpus licence and redistribution constraints?** A pinned revision we may not redistribute makes the anchor scheme unshareable, which changes the distribution model and therefore the purpose.

*Still unknown:* which of the twelve can slip past v0.1. Our position: 1, 2, 4 and 10 cannot — they determine whether any published number means anything — and 5 is the one most likely to be answered by accident, badly, by whoever writes the first parser.

## What this document is not

Not a literature review but a decision record with citations. It does not claim the systems described are bad — several are better than anything here will be. It does claim that none occupies the (b)+(c)+(d) intersection, that the omission is visible in their own documentation, and that a project occupying it must pay with refusals and with numbers it may not like.

Every source appears in [99-SOURCES.md](99-SOURCES.md) with a verification status; claims we could not verify are marked `[unverified]` above, with what would verify them.
