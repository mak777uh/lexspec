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

**Default mode: every model gets the whole brief.** Twelve work packages in one message, one model per pass.
The models are expected to differ, and the differences are useful in two directions: a WP one model covers and
another ignores shows a corner that only that model reached, and a summary several models repeat identically
shows where a single wrong reading would propagate furthest. Neither is evidence of anything — see §6 — but
both tell us where to point our own reading.

| Mode | When | How |
|---|---|---|
| **Full pass** (default) | any number of models | same prompt to every model, nothing removed; collect one table each |
| **Split** | the model's context cannot hold a twelve-WP output | give 3–4 WPs to a model that has already done a full pass, or to a model known to truncate |
| **Follow-up** | a pass ends mid-table | send "continue the table from WP-07; do not repeat rows already given" — do not accept a truncated answer as final |

Rules for the human handing this out:

1. **Do not vary the prompt between models.** Diversity has to come from the model, not from us, or the
   comparison stops meaning anything and we cannot tell "this model missed WP-09" from "we changed the
   question".
2. **Record the model and the date** next to every returned table. An unlabelled table is unusable, because
   the agreement column (§6) depends on knowing who said what.
3. **If the answer stops mid-table**, ask for continuation rather than accepting it. A model that stops is not
   a model that finished; the same lesson as the harness owning the stopping rule in a proof run.
4. **If the model cannot open GitHub** — some fetch any page but not `raw.`, some cannot reach github.com at
   all — paste the WP blocks from §3 after the prompt. The prompt tells it to say so when that happens, so the
   register records which answer came from the document and which from the paste.
5. Ask for the table only. A model that writes an essay has ignored the brief; re-ask with "table only".
6. If a model has no web access, it must say so and stop. Answers from memory are worse than no answers.
7. Keep every model's raw reply. The register needs its `[unverified]` rows and its dead ends — those are
   results, not noise.

---

## §2 The universal prompt (same text to every model)

```
You are collecting an evidence-graded register, not writing an essay.

TOPIC: approaches to turning legal/normative language into machine-checkable form — logics, languages,
standards, tools, proof-assistant formalisations, policy languages, and the empirical record of failures.

BRIEF (open this first):
  https://github.com/mak777uh/lexspec/blob/main/lab/assignments/SEARCH-01-landscape.md
  raw markdown, if the page does not render for you:
  https://raw.githubusercontent.com/mak777uh/lexspec/main/lab/assignments/SEARCH-01-landscape.md
Read section 3 for the twelve work packages and section 4 for the list of approaches that are ALREADY
covered — do not spend rows re-reporting those. If you cannot open links at all, say so in one line and work
from this message; you will be asked to continue without the brief.

COVER ALL TWELVE WORK PACKAGES. Do not choose a subset. Other models are answering the same brief and their
tables will be merged with yours, so a WP you skip is a WP we must notice.

OUTPUT: one markdown table with this column order, and one row per approach:
  wp | name | year + year_basis (repo_created|paper_published|spec_recommendation|first_release)
  | type (logic|language|standard|tool|product|paper|project)
  | unit of representation (clause|rule|norm|policy|obligation|computation) | claimed guarantee, QUOTED
  | explicitly NOT done, quote if the source states it | how it binds a rule to its legal source
  (provenance/anchor) or "none" | conflict semantics when two norms apply, or "none"
  | availability: open-source|spec-only|closed + licence + code link | alive in 2026: yes|no|unknown +
  evidence (release, commit, citation — a resolving homepage is not evidence) | max 2 primary URLs
  | one-line mechanism: how it actually works | what a checked-legal-language project should BORROW
  | what it should REFUSE | verification: verified|unverified|paywalled|dead-link (+ what would verify it)

BUDGETS
- 6 to 10 rows per work package. Depth beats breadth: a WP with 10 verified rows is worth more than one with
  30 unverified names.
- If you are running out of space, finish the row you are on, then stop and list the unfinished WPs under
  "not covered". Do not silently truncate a table.
- After the table, add two short lists: "could not verify" and "not covered" (WP numbers, or "none").

RULES
1. Every row needs at least one URL you actually opened in this session. No exceptions.
2. Quote technical guarantees; do not paraphrase them. "Sound and complete" is a claim, not a description.
3. Never invent a DOI, title, author, year, version, repository or licence. If you are unsure, omit it.
4. Unverifiable claim -> write unverified and say what would verify it.
5. The same idea in ten papers is ONE row, citing the two best URLs. We want distinct approaches, not a
   bibliography.
6. Prefer primary sources: specification documents, repositories, official documentation, the paper PDF.
   Blog posts, listicles and vendor marketing are leads only, never evidence.
7. If a work package yields nothing you can verify, still emit its WP number under "not covered" with one
   line why. "Nothing found" is a result; empty space is not.
8. No introduction, no conclusion, no methodology paragraph. Table, then the two lists.
9. If you have no web access, say so and stop. Do not answer from memory.
10. END WITH A SIGNATURE LINE: your model name and the date, exactly like
    "Returned by <model>, 2026-10-28; brief opened at <the URL you actually used>". An unsigned table is
    useless to us: we merge four or more passes and cannot attribute a row, a contradiction or a fabrication
    without knowing which pass said it.
11. ONLINE-OFFLINE MARK: if a URL opened only because a search engine showed you an excerpt, say so in the
    verification cell ("excerpt only"). We distinguish an opened page from a search snippet, and one fabricated
    repository in the first round came from exactly that confusion.
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

Columns, in this order (pipe-separated; keep them even if a cell is "none") — note `wp` first, so twelve
packages from one model and one package from another merge into the same table:

```
wp | name | year | type | unit | claimed guarantee | explicitly not | source binding | conflict semantics
| availability | alive 2026 | urls | mechanism | borrow | refuse | verification
```

Example — a real row from our own work, to show the target density:

```
WP-05 | Cedar | 2023 | language | policy | "a sound and complete logical encoding, which enables precise
policy analysis" | whether the policy expresses the intended business rule | none (the policy is the
artifact) | not specified by the language; deployment decides | open-source (Apache-2.0) | yes (active repo) |
https://arxiv.org/abs/2403.04651 | policies compiled to a Lean-modelled authorizer; analysis via SMT over the
encoded semantics | prove properties of the *language/analyser*, not of individual policies | treating a
policy engine as a compliance proof | verified
```

---

## §6 How results are merged

**The governing principle: this register is not a vote.** Models are instruments for seeing the field better,
not sources of authority. A row stands or falls on one thing only — whether a stranger can open the URL and
find the quoted claim. How many models named something has **no evidential weight at all**: six models can
repeat the same wrong summary, and one model can be the only one to have actually read the specification.

Two consequences, and they are the whole discipline of this step:

- **We re-open every URL ourselves before a row is used.** A model's `verified` is a claim about the model's
  session, not about the world; it becomes our `verified` only when we fetch the page and see the sentence.
  Rows we have not re-opened stay in the register marked `unverified-by-us`, whatever the model said.
- **A row with one checkable URL outranks a row with six mentions and none.** That ordering is the opposite of
  what a poll would produce, and it is the correct one.

1. **Dedupe key** = (canonical name, primary URL). The same approach from six models becomes one row, with the
   union of verified URLs and the most specific claim quoted — the longest quoted guarantee wins, because it
   is the one a stranger can check.
2. **Grade** = the weakest verification among the cited URLs *after our own re-check*. A row with one dead
   link and one live primary source is `verified`; two dead links is `dead-link`.
3. **`reported_by: n/models` is recorded, and it means only "how many models thought of it".** It is used to
   order our own re-checking — go first where several models point, because that is where a wrong summary
   would do the most damage — never to decide whether a row is true.
4. **Per-WP coverage is reported.** For each WP: how many models covered it, how many rows survived dedupe,
   and which models listed it under "not covered". A WP that every model skipped is a signal that our WP
   text is wrong — too vague, or asking for something that does not exist.
5. **Contradictions are kept, not resolved by majority.** If two models disagree on whether something is alive
   in 2026, both statements go in the register with their evidence, and the URL settles it — or it stays open
   and says so.
6. **Every merged row lands in [`lab/sources.md`](../sources.md)** or in a new
   `docs/08-LANDSCAPE-REGISTER.md`, with the date and the WP it came from.
7. **An empty WP is recorded** with the reason and the models that found nothing. That is how we know a
   corner of the field has been looked at and found empty, which is worth more than an unexamined corner.

---

## §7 Quality bar — what makes an answer usable

- A row is usable if a stranger could open the URL and find the quoted guarantee.
- A row is **not** usable if the guarantee is the model's paraphrase of a general impression.
- "Alive in 2026" needs evidence: a release, a commit, a 2026 citation. A homepage that still resolves is not
  evidence of life.
- Two URLs maximum. If an approach needs five citations, it is probably two approaches.
- The `borrow` / `refuse` columns are the point of the exercise. A row without them is a bibliography entry.
