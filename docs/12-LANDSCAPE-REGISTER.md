# 12 — Landscape register: four search passes, merged and graded

Source: four independent returns of [`lab/assignments/SEARCH-01-landscape.md`](../lab/assignments/SEARCH-01-landscape.md),
received 2026-10-28 and recorded as passes **A**, **B**, **C**, **D** in the order they arrived. Pass D is
signed ("Claude Sonnet 5.5"); A, B and C arrived unsigned, so their provenance is unknown — a protocol failure
on our side, fixed in the assignment (§2 now requires a signature line).

What this document is: the merged register with duplicates collapsed, the defects found in the returns, our
own verification of the rows that mattered, and the queue of rows still unchecked. What it is **not**: a
bibliography, or a claim that any row is true. Per charter C5, a row is `verified` only when **we** opened the
URL and found the quoted claim. Everything else says so.

---

## §1 Method, and one schema defect the merge exposed

**Dedupe key** = canonical approach name. Six models naming ODRL, four naming CUAD and four naming Cedar
collapse into one row each; the union of URLs is kept, the longest quoted guarantee is kept.

**Grading** (our grade, not the model's):

| Grade | Means |
|---|---|
| `V` | we opened the URL in this session and the quoted claim is there |
| `V*` | we opened it and found **less** than the model claimed — the row is corrected in place |
| `X` | the cited source does not support the row, or does not exist |
| `-` | not yet opened by us; the model's own grade is kept in the `rep.` column as a note only |

**The schema defect.** The column was "first year you can VERIFY", and the four passes read it four different
ways: repo creation (Cedar as 2023), paper publication (Cedar as 2024), standard revision (XACML as 2003 for
1.0 vs 2013 for 3.0), and access date (OpenFisca as "2026 (doc)"). All four are defensible readings of a bad
column. Fix for SEARCH-02: the column becomes **`year` + `year_basis ∈ {repo_created, paper_published,
spec_recommendation, first_release}`**, and a row may carry two years if two bases matter.

---

## §2 Merged register

`rep.` = how many of the four passes named it (A/B/C/D in parentheses when it is one pass only). Short claims
are quoted; the URLs live in the pass transcripts and are listed in §4 for the rows we have not yet opened.

| # | WP | approach | year (basis) | type | rep. | what it claims, or how it binds a rule to a source | grade |
|---|---|---|---|---|---|---|---|
| 1 | 01 | Input/output logic (Makinson & van der Torre) | 2000 (paper) | logic | 2/4 | norms as pairs `(a,x)`; the norm set is separate from the inference rules, so norms are not truth-apt | - |
| 2 | 01 | DAPRECO knowledge base (reified I/O logic, GDPR, LegalRuleML) | 2018 (repo) | project | 1/4 | "the biggest knowledge base in LegalRuleML and Input/Output logic freely available online"; text layer in Akoma Ntoso, logic layer in LegalRuleML | **V** (repo alive: pushed 2026-09-29, 9 stars; contents not opened) |
| 3 | 01 | SPINdle / defeasible deontic logic reasoner | 2009 (paper) | tool | 1/4 | Java reasoner for defeasible theories; superiority relation and defeaters as first-class objects | - |
| 4 | 01 | Governatori ASP encoding of Defeasible Deontic Logic | 2024 (paper) | paper | 1/4 | "efficient rule-based non-monotonic formalism", executed as an ASP meta-program | - |
| 5 | 01 | Adaptive deontic logic (Batens/Straßer) | 2010 (paper) | logic | 1/4 | tolerates deontic inconsistency by dynamically restricting inheritance instead of exploding | - |
| 6 | 01 | Prakken & Sartor dialectical model | 1996 (paper) | logic | 2/4 | conflicting arguments assessed by attack and priorities rather than by a single valuation | - |
| 7 | 01 | Horty, default logic for obligations | 2018 (paper) | paper | 1/4 | optimal goal satisfaction via Reiter defaults | - |
| 8 | 01 | Broersen, deontic STIT | 2011 (paper) | logic | 2/4 | action + obligation + knowledge in one temporal STIT logic; separates "can" from "may" | - |
| 9 | 01 | eFLINT (Haskell reference interpreter) | 2020 (paper) | language | 1/4 | executable normative specifications over transition systems, Hohfeld-based concepts; REPL, server, exploration | - |
| 10 | 02 | Catala, including the F* formalisation | 2021 (paper) | language | 2/4 | literate law→code with prose and code side by side; a *part* of the translation is proved in F*, with **one admitted lemma** and Z3 non-determinism noted in the repo | - |
| 11 | 02 | OpenFisca | 2013 (repo) | tool | 4/4 | microsimulation engine; variables with dated parameters; per-variable `reference` strings that nothing checks | **V\*** (repo 2013-12-29, AGPL-3.0, pushed 2026-10-23; the "2011" first year is unverified) |
| 12 | 02 | PolicyEngine core | 2022 (repo) | tool | 3/4 | "the simulation engine, parameter tree, variable system, and reform machinery"; README states it is **forked from OpenFisca-Core** | **V** (created 2022-10-01, AGPL-3.0, pushed 2026-10-27) |
| 13 | 02 | Better Rules for Government (NZ) | 2018 (report) | project | 2/4 | discovery programme, artefact chain "concept models, decision models, rules statements, and code"; no automated source check | - |
| 14 | 02 | Neota Logic | 2010 (vendor) | product | 1/4 | no-code expert-system builder for legal/compliance decision trees; closed | - |
| 15 | 02 | SBVR → Drools translation (financial compliance) | 2018 (paper) | tool | 2/4 | translates SBVR rule statements into DRL for a Rete engine | - |
| 16 | 02 | s(LAW) — automated legal reasoning with discretion (s(CASP)) | 2024 (paper) | project | 1/4 | goal-directed s(CASP) returns **partial stable models with a justification proof tree**; discretion appears as several admissible models, not one answer | **V** (arXiv 2401.14511, Arias et al., 2024-01-25) |
| 17 | 03 | ODRL 2.2 Information Model + Vocabulary | 2018 (W3C Rec) | standard | 4/4 | permissions/prohibitions/duties over assets; `conflict` ∈ {perm, prohibit, invalid}, **default invalid**; no normative machine semantics in the model text | - |
| 18 | 03 | ODRL formal semantics (OPAL 2025) | 2025 (paper) | paper | 1/4 | "Towards a Formal Semantics of the Open Digital Rights Language" — fills the gap row 17 leaves | - |
| 19 | 03 | ELI — European Legislation Identifier | 2012 (spec) | standard | 2/4 | structured HTTP URI + metadata ontology per legal text; identification only, no semantics | - |
| 20 | 03 | ECLI — European Case Law Identifier | 2011 (spec) | standard | 1/4 | uniform identifier for judgments (country/court/year/number) | - |
| 21 | 03 | DPV — Data Privacy Vocabulary (W3C DPVCG) | 2019 (spec) | standard | 2/4 | RDFS/SKOS taxonomy for GDPR-flavoured processing concepts; annotations, not checks | - |
| 22 | 03 | LKIF-Core | 2007 (spec) | standard | 2/4 | upper+core legal ontology, 15 modules; OWL axioms, no executable rule semantics | - |
| 23 | 04 | Catala F* proof of the default-calculus translation | 2021 (paper) | project | 1/4 | **"This mechanization contains one admitted lemma"**; Z3 non-determinism can break proof replay — a published trusted-base statement, which is exactly what we ask for | - |
| 24 | 04 | Lawlib (Lean 4, EITC twin of policyengine-us) | 2026 (claimed) | project | 1/4 | "Where sources of law diverge, the divergence is a theorem"; 10,120 printed-table cells reproduced | **X** — `github.com/than4213/lawlib` returns 404; the pass that cited it also could not open it. Unverifiable until a live source appears |
| 25 | 04 | Coq/Event-B formalisations of law | various | paper | 3/4 | three rows in this family cite Event-B smart contracts, an Event-B institution, and Event-B→JML — **all about software contracts, not legal contracts**; off-scope for WP-04 as written | - |
| 26 | 05 | Cedar | 2023 (repo) / 2024 (paper) | language | 4/4 | "a sound and complete logical encoding, which enables precise policy analysis"; Lean-modelled authorizer, SMT analysis; validator vs schema | **V** (repo created 2023-04-25, Apache-2.0, Rust, pushed 2026-10-28) |
| 27 | 05 | OPA / Rego | 2016 (repo) | tool | 3/4 | Datalog-inspired policy evaluation with a policy-test framework; **no equivalence or conflict analysis** | - |
| 28 | 05 | XACML 3.0 | 2003 (1.0) / 2013 (3.0) | standard | 3/4 | explicit combining algorithms: deny-overrides, permit-overrides, first-applicable, only-one-applicable; `Indeterminate` as a first-class outcome | - |
| 29 | 05 | Margrave | 2010 (paper) | tool | 2/4 | change-impact analysis of access-control policies; exhaustive consequences of a policy change | - |
| 30 | 05 | Zanzibar / OpenFGA (ReBAC) | 2019 (paper) / 2022 (repo) | tool | 2/4 | relation tuples + namespace configs; each decision pinned to a consistent snapshot — the reproducibility idea we want | - |
| 31 | 06 | IBSC — bounded satisfiability for legal compliance (MFOTL + Z3) | 2022 (paper) | tool | 1/4 | "sound, and complete (within a given bound)"; counterexample-guided; five case studies | **V** (arXiv 2209.04052, Feng/Marsso/Sabetzadeh/Chechik) |
| 32 | 06 | ContractCheck (SPA consistency, Z3) | 2022 (paper) | tool | 1/4 | encodes clause premises and consistency constraints in a decidable fragment; returns a model or evidence of contradictory clauses | **V** (arXiv 2212.03349, Khoja/Kölbl/Leue/Wilhelmi) |
| 33 | 06 | Neuro-symbolic compliance (LLM + SMT), financial law | 2026 (paper) | paper | 2/4 | statutes as hard constraints, facts as soft; MaxSMT gives a minimal-change repair; UNSAT = no assignment satisfies both | **V** (arXiv 2601.06181, Hsia/Yu/Jiang, 2026-01-07) |
| 34 | 06 | cvc5 / Z3 / clingo / Soufflé as compliance engines | n/a | tool | 4/4 | solvers themselves; none binds a formula to a legal source | - |
| 35 | 06 | CHR for argumentation schemes | 2017 (paper) | tool | 1/4 | constraint handling rules to instantiate argumentation schemes | - |
| 36 | 07 | CUAD | 2021 (paper) | project | 4/4 | 510 contracts, 41 clause types, 13,000+ expert span annotations | **V\*** (arXiv 2103.06268 correct; repo `The-Atticus-Project/cuad` created 2021-03-11 but **no licence file detected** — the CC-BY-4.0 claim belongs to the HF dataset, unverified) |
| 37 | 07 | CLAUDETTE (unfair clauses in ToS) | 2018 (paper) | tool | 2/4 | sentence-level unfairness detection against EU Directive 93/13 categories; "potentially unfair" as triage | - |
| 38 | 07 | LEDGAR / ContractNLI / LegalBERT / LegalBERT++ | 2020–2026 | paper/tool | 3/4 | provision classification, document-level NLI with evidence spans, domain-adapted encoders | - |
| 39 | 07 | Commercial contract review (Harvey, Luminance, Robin AI, Spellbook, LegalOn, Ironclad) | n/a | product | 1/4 | no independent evaluation with legal-accuracy metrics was found by any pass | - |
| 40 | 08 | Temporal defeasible logic (Governatori; deadlines; norm modification) | 2005–2013 | logic | 3/4 | three distinct times per norm (in force / efficacy / application); modification as meta-rules | - |
| 41 | 08 | LKIF-rules temporal dimensions | 2010 (paper) | language | 1/4 | per-sentence `timeBlock` binding text to validity intervals — the closest thing to a sentence-level temporal anchor found | - |
| 42 | 09 | C2PA Content Credentials | 2021 (org) / 2022 (spec 1.0) | standard | 4/4 | signed manifest binding assertions to an asset; the spec **explicitly refuses to judge whether provenance is "good or bad"** | - |
| 43 | 09 | in-toto / attestation framework | 2019 (paper) / 2021 (repo) | standard | 3/4 | signed link/attestation per step, bound to artefact digests; layout declares who may do which step | **V\*** (repo created 2021-04-01, active, licence GitHub reports as **NOASSERTION** — the "open-source, licence unverified" note was right) |
| 44 | 09 | SLSA / Sigstore | 2021–2022 | standard | 2/4 | build-provenance levels; keyless signing with a transparency log | - |
| 45 | 09 | RFC 3161 time-stamping | 2001 (RFC) | standard | 1/4 | a TSA token binds a message imprint to a time assertion | - |
| 46 | 09 | FRE 902(13)/(14) self-authenticating electronic records | 2017 (rule) | standard | 1/4 | certify the **process** that produced the record, plus a hash for copies — the only court-facing rule any pass found | - |
| 47 | 10 | EU AI Act Art. 11 + Annex IV | 2024 (regulation) | standard | 4/4 | "shall contain at least the following information" — a documentation list in prose, not a checkable test suite | - |
| 48 | 10 | NIST AI RMF 1.0 (+ Playbook) | 2023 (framework) | standard | 3/4 | voluntary risk-management functions GOVERN/MAP/MEASURE/MANAGE | - |
| 49 | 10 | ISO/IEC 42001 | 2023 (standard) | standard | 2/4 | certifiable AI management system | - |
| 50 | 11 | Workflow-net soundness (van der Aalst et al.) | 1997 (paper) | logic | 3/4 | eight soundness notions decidable; **undecidable for reset arcs** — the honest boundary statement we want to copy | - |
| 51 | 11 | BPMN verification (model checking, timed automata, quality analysis) | 2014–2024 | tool/paper | 3/4 | translate BPMN to a formal model and check reachability/deadlock properties | - |
| 52 | 12 | Robodebt (Australian Royal Commission) | 2023 (report) | project | 2/4 | income averaging was **inconsistent with social security legislation**; scheme unlawful; report names the institutional cause | - |
| 53 | 12 | Susskind, Leith, Bench-Capon on legal expert systems | 1986–2010 | paper | 3/4 | the 1980s–90s episode; Leith's "rise and fall" is the named post-mortem; Bench-Capon's "deep models" critique | - |

---

## §3 Defects found in the four returns

This section is why the merge is worth doing. Each item is a row that would have entered the register as true.

1. **A fabricated project (row 24).** `github.com/than4213/lawlib` returns **404**. The claim attached to it —
   "where sources of law diverge, the divergence is a theorem" — is the single most relevant sentence in all
   four returns for our H3, and it currently has no source. It stays in the register as `X`, not deleted,
   because if a real analogue exists we must find it: a Lean library proving *divergence between two
   encodings of the same law* is precisely the artifact our hypothesis register says nobody has built.
2. **A blog post used as evidence.** One row cites a Medium article as the primary source for EU AI Act
   Annex IV. The assignment forbids this in rule 6; the row is dropped from the table and kept here as the
   example of why the rule exists.
3. **A curated list used as a project.** One row cites `newca12/awesome-rust-formalized-reasoning` — a link
   list — as the source for a project called "Coq Legalis-RS". A link list cannot support a claim about a
   project's guarantee.
4. **Off-scope rows dressed as finds.** Three WP-04 rows are about Event-B/Coq for *software* contracts and
   SQL; one WP-06 row is about Z3 for *crypto* code. True statements, wrong work package: they inflate a
   count without telling us anything about legal formalisation.
5. **Year as four different things** — see §1. Not a model error; our column was bad.
6. **Licence drift.** Two licences were asserted and are wrong or narrower than claimed: CUAD's CC-BY-4.0
   belongs to the HF dataset, not the repo (no licence file detected); in-toto/attestation reports
   `NOASSERTION`. Both are minor and both matter, because a register that carries wrong licences cannot be
   used to decide what to reuse.
7. **"Alive in 2026" asserted from a live homepage.** Three rows treat a resolving page as evidence of
   activity. Where we checked, real evidence existed (openfisca-core pushed 2026-10-23, cedar 2026-10-28,
   policyengine-core 2026-10-27, daprecokb 2026-09-29) — but the models did not provide it, they inferred it.
8. **Duplication by naming.** ODRL appeared in all four passes as four "different" rows (model, vocabulary,
   conflict handling, formal semantics). It is one standard plus one 2025 paper. A count of rows is not a
   count of approaches.

**What held up.** The five arXiv identifiers checked are all real and correctly titled: 2401.14511 (s(LAW),
2024), 2103.06268 (CUAD, 2021), 2212.03349 (ContractCheck, 2022), 2209.04052 (IBSC, 2022), 2601.06181
(neuro-symbolic compliance, 2026). That is a better hit rate than the repo-level rows and worth saying plainly:
**paper identifiers are cheap to check and were mostly right; repository identifiers were where the fabrications
lived.**

---

## §4 Queue for our own re-check

Rows we have **not** opened, ordered by what they could change in our design. Nothing from this list may enter
`docs/` or a verdict until we do.

| Priority | Rows | Why |
|---|---|---|
| 1 | s(LAW) paper, IBSC paper, ContractCheck paper, neuro-symbolic paper | the four closest existing attempts to "check a legal encoding with a solver"; they define what our novelty is not |
| 2 | Catala F* formalisation README (the admitted lemma) | the only published trusted-base statement in legal formalisation that any pass found |
| 3 | ODRL formal semantics (OPAL 2025) | if a normative semantics exists, our "ODRL has no semantics" line in `docs/02` may be out of date |
| 4 | eFLINT package + GPCE paper | executable normative specifications with Hohfeld concepts — closest to our model |
| 5 | DAPRECO KB contents | a real GDPR knowledge base in LegalRuleML; we can test our anchor rule against it |
| 6 | LKIF-rules temporal dimensions | sentence-level `timeBlock` — the temporal anchor we lack |
| 7 | workflow-net soundness + reset arcs | the model of an honest decidability boundary |
| 8 | FRE 902(13)/(14) | the only admissibility rule found; bounds what a certificate must contain |

---

## §5 Coverage: what four passes actually covered

`full` = met the 6–10 row budget; `partial` = fewer rows; `none` = explicitly listed as not covered.

| WP | A | B | C | D | Note |
|---|---|---|---|---|---|
| 01 deontic logic | partial | partial | — | full | A and B returned "no new technical guarantee verified" for several seeds; D produced the densest rows |
| 02 law-as-code | partial | partial | — | full | only D reached Neota/Drools/OpenFisca-Aotearoa |
| 03 standards | partial | full | — | full | ODRL dominated every pass; ELI/ECLI appeared only twice |
| 04 proof assistants | none | partial | — | partial | weakest coverage of all twelve; the only real artifact claims were about Catala's F* |
| 05 policy languages | full | full | — | full | best-covered WP; all four passes independently found Cedar |
| 06 solvers | partial | partial | — | full | D found the three papers that matter (IBSC, ContractCheck, neuro-symbolic) |
| 07 contract NLP | partial | partial | — | full | products were named, never evaluated |
| 08 temporal | partial | partial | — | partial | the two substantive finds (TDL, LKIF `timeBlock`) each appeared once |
| 09 evidence | partial | full | — | full | FRE 902 appeared once — the most useful single row in the whole set |
| 10 regtech | partial | partial | — | partial | every pass returned the same three documents |
| 11 processes | none | partial | — | full | only D produced workflow-net detail |
| 12 failures | partial | partial | — | full | Robodebt found twice; the 1980s episode only by D |

Pass C could not open the brief and returned six unassigned rows in Russian; they are merged where they
duplicate A/B/D (Cedar, ODRL, XACML, Catala, eFLINT, s(LAW)) and its eFLINT and s(LAW) rows were the most
careful in the set — it quoted the negative build reports instead of hiding them.

**The one systematic gap:** no pass found an approach that binds a rule to an *exact byte range of a pinned
revision*. Rows 42–46 are the closest, and they bind to an asset or a process, not to a statutory span. That is
either our differentiator or evidence that the requirement is unrealistic — and we cannot tell which from
search alone. It is the first question of round 01.
