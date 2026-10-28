# SEARCH-01 — Landscape assignment: every approach to machine-checkable legal language

Purpose: produce a single evidence-graded register of approaches — logics, languages, standards, tools,
proof-assistant formalisations, policy languages, and the empirical record of failures — that a project
building a *checked legal statement language* can actually use.

The assignment is split into **twelve work packages (WP)**. One model, one WP. The output format is fixed so
that twelve independent answers merge into one table without an editor.

Written 2026-10-28. Companion files: [`docs/02-DESIGN-SPACE.md`](../../docs/02-DESIGN-SPACE.md) (what we already
surveyed), [`lab/sources.md`](../sources.md) (the register these results feed).

---

## §1 How to run this

| Mode | When | How |
|---|---|---|
| **One WP per model** (preferred) | 8+ models available | paste the universal prompt + one WP block; collect twelve tables |
| **Grouped** | 3–4 models | give each model 3–4 WPs, in one message, one table per WP |
| **Single pass** | 1 model | all twelve WPs at once; expect lower depth, and say so in the register |

Rules for the human handing this out:

1. One WP per message. If a model gets two WPs in one message it will merge them and lose rows.
2. Ask for the table only. A model that writes an essay has ignored the brief; re-ask with "table only".
3. If a model has no web access, it must say so and stop. Answers from memory are worse than no answers.
4. Keep every model's raw reply. The register needs its `[unverified]` rows and its dead ends — those are
   results, not noise.

---

## §2 The universal prompt (paste this before every WP block)

```
You are collecting an evidence-graded register, not writing an essay.

TOPIC: approaches to turning legal/normative language into machine-checkable form — logics, languages,
standards, tools, proof-assistant formalisations, policy languages, and the empirical record of failures.

Your scope is the WORK PACKAGE at the end of this message and nothing else. Do not summarise the whole field.

For every approach you report, fill exactly one row with these fields:
  name | first year you can VERIFY | type (logic|language|standard|tool|product|paper|project)
  | unit of representation (clause|rule|norm|policy|obligation|computation) | claimed guarantee, QUOTED
  | explicitly NOT done, quote if the source states it | how it binds a rule to its legal source
  (provenance/anchor) or "none" | conflict semantics when two norms apply, or "none"
  | availability: open-source|spec-only|closed + licence + code link | alive in 2026: yes|no|unknown +
  evidence | max 2 primary URLs | one-line mechanism: how it actually works
  | what a checked-legal-language project should BORROW | what it should REFUSE
  | verification: verified|unverified|paywalled|dead-link (+ what would verify it)

RULES
1. Every row needs at least one URL you actually opened in this session. No exceptions.
2. Quote technical guarantees; do not paraphrase them. "Sound and complete" is a claim, not a description.
3. Never invent a DOI, title, author, year, version, repository or licence. If you are unsure, omit it.
4. Unverifiable claim -> write unverified and say what would verify it.
5. The same idea in ten papers is ONE row, citing the two best URLs. We want distinct approaches, not a
   bibliography.
6. Prefer primary sources: specification documents, repositories, official documentation, the paper PDF.
   Blog posts, listicles and vendor marketing are leads only, never evidence.
7. If your work package yields nothing you can verify, answer "no new entries" and one line why.
   That is a valid, useful answer. Do not fill space.
8. OUTPUT: one markdown table, then a short list "could not verify". No introduction, no conclusion.
9. If you have no web access, say so and stop. Do not answer from memory.

WORK PACKAGE:
<insert WP block>
```

---

## §3 The twelve work packages

Each block is self-contained: scope, seed names to check, the questions that matter, and the dead ends to
avoid. Seed names are starting points, not a closed list.

### WP-01 — Deontic and normative logic (science)

**Scope.** Logics that model obligation, permission, prohibition and their conflicts. Dyadic deontic logic;
standard deontic logic and why it fails; contrary-to-duty (Chisholm); input/output logic; defeasible and
adaptive deontic logic; preferential and ranked semantics; normative systems; deontic STIT.
**Seeds.** von Wright, Chisholm 1963, Makinson & van der Torre (input/output), Nute (defeasible deontic),
Batens/Straßer (adaptive), Prakken & Sartor, Governatori, Horty, LogiKEy.
**Questions that matter.** Which of these has an *implementation* that runs on a statute-sized input (not a
toy example)? Which gives a decision procedure, and what is its complexity? How does each handle a conflict
between two applicable norms — report, prioritise, or both? What is the published criticism from legal
practice (not from logic)?
**Dead ends.** Surveys that list logics without any implementation or evaluation. Philosophy-only treatments
with no computable semantics.

### WP-02 — Law-as-code languages and rules-as-code programmes

**Scope.** Languages and national programmes that write law or regulation as executable code. Catala, L4,
Blawx, s(LAW), Oracle Policy Automation, Neota, Bryter, OpenFisca, PolicyEngine, Drools-for-law; government
"Rules as Code" work (New Zealand Better Rules, Australia, Canada, France); tax and benefit engines.
**Seeds.** Catala (Inria), L4 (SMU CCLAW), Blawx, OpenFisca, PolicyEngine, Better Rules NZ, OPA (Oracle
Policy Automation), LegalRuleML.
**Questions.** What is the unit — a rule, a computation, a clause? Does the language keep the *paragraph
structure* of the source (Catala claims this)? How are exceptions handled — priority, ordering, or error?
Is there any mechanism binding a rule to the article it came from? What is the published coverage (how much
of a real statute was actually encoded) and the cost?
**Dead ends.** Marketing pages. Demos on calculator-sized examples presented as statute coverage.

### WP-03 — Legal document standards, metadata and ontologies

**Scope.** Standards for representing legal *documents* and legal *concepts*: Akoma Ntoso / LegalDocML,
European Legislation Identifier (ELI), ECLI, LegalRuleML, LKIF-Core, LOIS/LRI-Core, EuroVoc, DPV/DPVCG
(data-protection vocabulary), ODRL (rights expression), COEL, W3C Verifiable Credentials where relevant to
rights.
**Seeds.** OASIS LegalDocML, OASIS LegalRuleML, ELI (EU), ECLI, ODRL 2.2 (W3C), LKIF, DPV.
**Questions.** Which of these has a *machine checkable semantics* versus being a markup vocabulary? Does any
standard specify how to point from an assertion to an exact byte range of an authoritative text revision?
What does ODRL model as a permission, and how does it handle conflicting permissions? Who actually
implements these — name the publishers and jurisdictions, with evidence.
**Dead ends.** Ontology papers with no instances. Standards pages without a normative semantics.

### WP-04 — Proof assistants and formal methods reaching law

**Scope.** Machine-checked formalisation of norms, statutes, contracts or legal reasoning in Isabelle/HOL,
Coq/Rocq, Lean 4, TLA+, Event-B, K Framework, plus deontic theorem provers and modal provers.
**Seeds.** LogiKEy (Isabelle/HOL dataset), Lean legal formalisations, Event-B for statutes, TLA+ for legal
processes, KAT/PDL for legal relations, deontic theorem provers.
**Questions.** What exactly is proved — a theorem about a logic, about a model of a statute, or about a
program? How large is the artefact (lines of proof)? What had to be assumed (axioms, semantics, trusted
base)? Is the artefact downloadable? Has anyone proved anything about a *detector* or *checker* rather than
about a clause?
**Dead ends.** Position papers "we could use a proof assistant". Anything that will not show the proof files.

### WP-05 — Policy languages with analysable semantics

**Scope.** Machine-readable policy/permission languages designed so that policy sets can be *analysed*:
Cedar (AWS), OPA/Rego, XACML, Google Zanzibar / OpenFGA relationship-based access control, Margrave,
Alloy-based policy analysis, SMT-based policy comparison.
**Seeds.** Cedar (Lean model, arXiv 2403.04651), OPA, XACML 3.0, Margrave, OpenFGA/Zanzibar.
**Questions.** Which properties are actually analysed (equivalence, subsumption, reachability, conflict,
refactoring safety) and with what guarantee? Which of these proved something *about the language* rather
than about a policy? How is a permission bound to its justification/authority? How is a conflict between
two permits/denies resolved — by the language or by the deployment?
**Dead ends.** RBAC product pages. "Policy as code" blog posts with no analysis result.

### WP-06 — Solvers and rule engines applied to compliance

**Scope.** Encoding regulation or compliance rules for a solver: SMT (Z3, cvc5), ASP (clingo), Datalog
(Soufflé), Prolog (PROLEG), Constraint Handling Rules, production rule engines (Drools), and regulatory
reporting engines in finance/tax.
**Seeds.** Z3/cvc5 for regulation, Soufflé Datalog compliance, clingo norms, CHR legal, PROLEG, Drools
compliance, Basel/IFRS rule engines.
**Questions.** What is the encoding cost per article, if reported? What fragment of the regulation had to be
dropped to fit the solver? What does the solver guarantee (decidability, completeness) and what is the
timeout behaviour? Any published case where the solver found a real defect in the rules?
**Dead ends.** "We used an SMT solver" with no reduction from text to formula shown.

### WP-07 — Contract analysis: clause classification, NLP, LLM review

**Scope.** Systems that read contracts and classify or extract: CLAUDETTE (unfair terms), LegalBERT,
CUAD, LEDGAR, ContractNLI, Atticus, LexNLP, and commercial contract-review products (Harvey, Luminance,
Robin AI, Spellbook, LegalOn, Ironclad, LegalSifter).
**Seeds.** CLAUDETTE (unfair terms detection), CUAD, LEDGAR, ContractNLI, LegalBERT, and the products above.
**Questions.** What is measured, on what data, with what inter-annotator agreement? Is there any published
evaluation of legal accuracy by an independent party? Which of these produce a *checkable* output (a rule, a
citation, a constraint) versus a score or a summary? What do the failure analyses report?
**Dead ends.** Vendor accuracy claims without a dataset. Benchmark wins on sentence classification presented
as contract understanding.

### WP-08 — Temporal legal reasoning and conflict resolution

**Scope.** Lex specialis, lex posterior, non-retroactivity, repeal, amendment, entry into force,
transitional provisions — formalised. Legal dynamics and norm change (AGM-style revision for law), temporal
deontic logic, versioned legal texts.
**Seeds.** Prakken & Sartor on legal dynamics, Governatori on defeasibility, LegalRuleML Override/Defeater,
Akoma Ntoso temporal data (`activeModifications`), Catala priorities, ELI versioning.
**Questions.** Is conflict resolution *computed* or *declared*? Which systems model amendments as data rather
than as edits? Is there a published formal account that handles "article 5 as amended on date X applies to
facts occurring between Y and Z"?
**Dead ends.** Papers that only state the maxims. Systems where "lex specialis" is a flag with no semantics.

### WP-09 — Evidence, certificates, provenance and audit integrity

**Scope.** How other fields make a machine-produced record acceptable to a third party: C2PA content
provenance, in-toto/Sigstore/SLSA supply-chain attestations, RFC 3161 timestamping, OpenTimestamps, eIDAS
qualified signatures, 21 CFR Part 11 (clinical), WORM storage, hash-chained audit logs, US FRE 902(13)/(14)
self-authenticating electronic records.
**Seeds.** C2PA, in-toto, Sigstore, SLSA, RFC 3161, eIDAS, 21 CFR Part 11, FRE 902(13)-(14), WORM.
**Questions.** What must a record contain to be *re-checkable offline* by a stranger? What is the accepted
retention and re-verification story when the signing key or the algorithm ages out? What has a court or a
regulator actually accepted? Where does each scheme deliberately stop (what does it explicitly not prove)?
**Dead ends.** Blockchain-notarisation marketing. Schemes that require trusting the same party that produced
the record.

### WP-10 — RegTech, compliance automation and AI-governance tooling

**Scope.** Industrial systems and regulatory frameworks that claim automated compliance: Ascent, 4CRisk,
Thomson Reuters, Wolters Kluwer, IBM OpenPages; EU AI Act Annex IV technical documentation, ISO/IEC 42001,
NIST AI RMF, model cards, conformity assessment automation.
**Seeds.** EU AI Act Annex IV, ISO/IEC 42001, NIST AI RMF, model cards model reporting, the vendors above.
**Questions.** What is the *artefact* the regime requires — a document, a log, a test suite? Is any of it
machine-checkable, or is it prose that a human audits? Which obligations are expressed as testable
requirements and which as narratives? Is there a published mapping from a requirement to a check?
**Dead ends.** Vendor brochures. Interpretations of the AI Act by non-authoritative blogs.

### WP-11 — Verification of business processes, workflows and rules

**Scope.** Formal verification applied to the operational layer: BPMN + model checking, workflow-net
soundness, temporal-logic specification of business processes, Alloy/TLA+ in industry, verification of
KYC/AML rule sets, RBAC/ABAC analysis.
**Seeds.** van der Aalst workflow nets, BPMN verification, TLA+ industrial case studies, Alloy RBAC,
business-rule consistency checking.
**Questions.** Which properties are actually checked in practice (soundness, deadlock, reachability,
separation of duty)? What is the cost per model? Is there a published case where a check found a real defect
in an operating process? How is the model kept in sync with the process it models?
**Dead ends.** Tool comparisons without a checked property. Academic examples on 5-node graphs.

### WP-12 — The empirical record of failure

**Scope.** Published evidence about what did **not** work: government evaluations of Rules as Code, the
expert-systems-in-law episode of the 1980s–90s, critiques of deontic logic in legal practice, legal-AI
hallucination studies, adoption studies, post-mortems.
**Seeds.** Susskind's accounts of legal expert systems, NZ/AU Better Rules evaluations, legal hallucination
studies (arXiv 2401.01301, 2405.20362), critiques of "computational law", failed legal-tech products.
**Questions.** For each failure: what was the stated cause, and is it a *technical* cause or an
*institutional* one? Which failures are cited repeatedly without a primary source? What would have had to be
true for the approach to work?
**Dead ends.** Opinion pieces without a named case. "AI will replace lawyers" genre.

---

## §4 What we already have (tell the models, to avoid re-finding)

These are covered by [`docs/02-DESIGN-SPACE.md`](../../docs/02-DESIGN-SPACE.md) with verified sources. A model
that returns them again is not wrong, but it is not adding rows:

LegalRuleML, Akoma Ntoso, Catala, L4, Blawx, s(LAW)/Logical English, PROLEG, Hohfeld's jural relations,
standard/dyadic/input-output/deontic logic basics, Chisholm's paradox, Isobelle-LogiKEy at the level of
existence, Lean and the Cedar case study, legal hallucination studies (both arXiv papers), CompCert, seL4,
IronFleet, TLA+ at AWS, PBT/QuickCheck.

What is **not** covered and is the reason for this assignment: WP-02's commercial and government programmes,
WP-03's ODRL/ELI/ECLI/DPV specifics, WP-05's analysable policy languages in depth, WP-06's solver
encodings, WP-07 entirely, WP-09 entirely, WP-10 entirely, WP-11 entirely, WP-12 partially.

---

## §5 Output schema, and an example row

Columns, in this order (pipe-separated; keep them even if a cell is "none"):

```
name | year | type | unit | claimed guarantee | explicitly not | source binding | conflict semantics
| availability | alive 2026 | urls | mechanism | borrow | refuse | verification
```

Example — a real row from our own work, to show the target density:

```
Cedar | 2023 | language | policy | "a sound and complete logical encoding, which enables precise policy
analysis" | whether the policy expresses the intended business rule | none (the policy is the artifact) |
not specified by the language; deployment decides | open-source (Apache-2.0) | yes (active repo) |
https://arxiv.org/abs/2403.04651 | policies compiled to a Lean-modelled authorizer; analysis via SMT over the
encoded semantics | prove properties of the *language/analyser*, not of individual policies | treating a
policy engine as a compliance proof | verified
```

---

## §6 How results are merged (so the models know what happens next)

1. **Dedupe key** = (canonical name, primary URL). The same approach from three models becomes one row, with
   the union of verified URLs and the most specific claim quoted.
2. **Grade** = the weakest verification among the cited URLs. A row with one dead link and one live primary
   source is `verified`; two dead links is `dead-link`.
3. **Contradictions are kept, not resolved.** If two models disagree on whether something is alive in 2026,
   both statements go in the register with their evidence, and the disagreement is the finding.
4. **Every merged row lands in [`lab/sources.md`](../sources.md)** or in a new
   `docs/08-LANDSCAPE-REGISTER.md`, with the date and the WP it came from.
5. **A WP that returns nothing** is recorded as an empty WP with the reason. That is how we know a corner of
   the field has been looked at and found empty, which is worth more than an unexamined corner.

---

## §7 Quality bar — what makes an answer usable

- A row is usable if a stranger could open the URL and find the quoted guarantee.
- A row is **not** usable if the guarantee is the model's paraphrase of a general impression.
- "Alive in 2026" needs evidence: a release, a commit, a 2026 citation. A homepage that still resolves is not
  evidence of life.
- Two URLs maximum. If an approach needs five citations, it is probably two approaches.
- The `borrow` / `refuse` columns are the point of the exercise. A row without them is a bibliography entry.
