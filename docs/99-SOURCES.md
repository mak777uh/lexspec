# 99 — Sources

Every non-obvious factual claim in [`02-DESIGN-SPACE.md`](02-DESIGN-SPACE.md) points here.

**Access date for every row: 2026-10-28.** No row was cited from memory.

## How "verified" was decided

Three grades, kept apart on purpose:

| Grade | Meaning |
|---|---|
| **yes** | the URL was fetched in this session and the fetched text contains the claim it is attached to |
| **yes (registry)** | the DOI was resolved through the Crossref API and the returned title/year match the claim; the publisher landing page was not opened (paywall risk), so the *bibliographic* claim is verified, not the full text |
| **no** | the URL did not resolve, or resolved to something that does not support the claim; the row stays in the table because a failed verification is a result |

A `yes (registry)` row is enough to cite a title, authors and year. It is not enough to cite a quotation.

---

## A. Standards and specifications

| url | what it is | supports | access date | verified |
|---|---|---|---|---|
| https://docs.oasis-open.org/legaldocml/akn-core/v1.0/akn-core-v1.0-part1-vocabulary.html | *Akoma Ntoso Version 1.0 Part 1: XML Vocabulary*, OASIS Standard, 29 August 2018 | §1 (four levels: content/structure/semantics/presentation, §4.5); §2.2 (FRBR, §4.3.1–4.3.4 author-vs-editor, §5.7 & §5.10.2/3/10 change machinery, "lesser authoritativeness"); §2.11 | 2026-10-28 | yes |
| https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/legalruleml-core-spec-v1.0.html | *LegalRuleML Core Specification Version 1.0*, OASIS Standard, 30 August 2021 | §1.1 ("independent from any legal ontology and logic framework"); §2.1 (deontic vocabulary, Strength/Defeater, Override `@over`/`@under`, `TemporalCharacteristic`/`Legal Status`/`Status Development`, `SuborderList`, Violation/Penalty/Reparation, requirement R4 isomorphism) | 2026-10-28 | yes |

## B. Projects, repositories, documentation

| url | what it is | supports | access date | verified |
|---|---|---|---|---|
| https://legalese.com/l4/concepts/legal-modeling/regulative-rules | L4 documentation, "How obligations unfold" | §1.2 (a regulative rule "decides nothing by itself"); §2.4 (`DEONTIC`, `MUST/MAY/SHANT`, `WITHIN`, `HENCE`/`LEST`, `FULFILLED`/breach/residual obligation, the missing fixed-date and named-event deadline syntax) | 2026-10-28 | yes |
| https://github.com/smucclaw/dsl | `smucclaw/dsl` — L4 implementation repository | §2.4 (the SMU CCLAW DSL, Haskell, description "Domain Specific Languages for Computational Law") | 2026-10-28 | yes |
| https://api.github.com/repos/smucclaw/dsl | GitHub API metadata for that repository | §2.4 (created 2020-06-05, default branch `main`, primary language Haskell, last push 2025-06-29) | 2026-10-28 | yes |
| https://legalese.com/l4 | L4 documentation home | §2.4 (navigation only — the documentation entry point) | 2026-10-28 | no — linked as the docs home, not opened; no claim rests on it alone |
| https://catala-lang.org/ | Catala project site, "Law to Code" | §2.3 (project identity only) | 2026-10-28 | no — HTTP 200 but the body is JS-rendered and returned no readable content; nothing is cited from it |
| https://developers.laws.africa | Laws.Africa Legal Knowledge Platform developer guide | §2.2 (Content API serves "point-in-time versions, XML, HTML, PDF … lifecycle metadata") | 2026-10-28 | yes |
| https://laws.africa/ | Laws.Africa organisation site | §2.2 (production legislation digitisation/publishing at scale) | 2026-10-28 | yes |
| https://lean-lang.org/ | Lean 4 project site | §2.9 (Lean is "an open-source programming language and proof assistant" with a minimal trusted kernel; Mathlib "over a million lines"; the Cedar case study and its differential testing against production Rust) | 2026-10-28 | yes |

## C. Papers

| url | what it is | supports | access date | verified |
|---|---|---|---|---|
| https://arxiv.org/abs/2103.03198 | Merigoux, Chataing, Protzenko, *Catala: A Programming Language for the Law*, arXiv:2103.03198v2 (2021) | §2.3 (abstract: prose-to-executable design, F⋆-verified compilation, US §121 and French family benefits, a bug found in the official implementation) | 2026-10-28 | yes |
| https://arxiv.org/html/2103.03198v2 | Full HTML text of the same paper | §2.3 (prioritized default logic as the core; scope/`exception` syntax; static priority from the syntax tree; fatal error on unresolvable conflict; "not Turing-complete, purposefully"; one-to-one paragraph↔translation; the pair-programming admission; affiliations Inria / ENS Paris / Microsoft Research) | 2026-10-28 | yes |
| https://doi.org/10.1145/3473582 | DOI of the ICFP 2021 proceedings version of Catala | §2.3 | 2026-10-28 | yes (registry) — DOI confirmed from the arXiv record's "Related DOI"; doi.org not opened |
| https://doi.org/10.1016/j.artint.2020.103348 | Benzmüller, Parent, van der Torre, *Designing normative theories for ethical and legal reasoning: LogiKEy framework, methodology, and tool support*, Artificial Intelligence (2020) | §2.9 | 2026-10-28 | yes (registry) |
| https://doi.org/10.1016/j.dib.2020.106409 | *LogiKEy workbench: Deontic logics, logic combinations and expressive ethical and legal reasoning (Isabelle/HOL dataset)*, Data in Brief (2020) | §2.9 | 2026-10-28 | yes (registry) |
| https://doi.org/10.3233/FAIA220473 | Ranta, Listenmaa, Soh, Wong, *An End-to-End Pipeline from Law Text to Logical Formulas*, JURIX 2022, FAIA vol. 362, pp. 237–242 | §2.5 | 2026-10-28 | yes (registry) — plus the record below |
| https://research.chalmers.se/publication/534400 | Chalmers research record for that paper (abstract, authors, venue, DOI) | §2.5 (Grammatical Framework parsing; "assembly logic" intermediate representation; "rule-based and explainable"; "useful results from day one, but allows subsequent refinements and variations") | 2026-10-28 | yes |
| https://doi.org/10.1093/analys/24.2.33 | Chisholm, *Contrary-to-Duty Imperatives and Deontic Logic*, Analysis 24(2) (1963) | §2.6 (the CTD paradox) | 2026-10-28 | yes (registry) |
| https://doi.org/10.1023/A:1004748624537 | Makinson & van der Torre, *Input/Output Logics*, Journal of Philosophical Logic (2000) | §2.6 (norms as input/output pairs rather than propositions) | 2026-10-28 | yes (registry) |
| https://doi.org/10.4324/9781315254821 | Hohfeld, *Fundamental Legal Conceptions as Applied in Judicial Reasoning* (collected edition, Routledge 2016; lectures 1913/1917) | §2.7 | 2026-10-28 | yes (registry) |
| https://arxiv.org/abs/2601.01477 | Zin, Wehnert, Kong, Nguyen, Fungwacharakorn, Xue, Araszkiewicz, Goebel, Satoh, Nguyen, *Can Legislation Be Made Machine-Readable in PROLEG?*, arXiv:2601.01477v1 (4 January 2026) | §2.5 (single LLM prompt → if-then rules → PROLEG encoding; expert validation and refinement; GDPR Art. 6; "observed limitations") | 2026-10-28 | yes |
| https://arxiv.org/abs/2401.01301 | Dahl, Magesh, Suzgun, Ho, *Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models*, arXiv:2401.01301v2 (2024) | §1.2, §2.10 (58% GPT-4 to 88% Llama 2; failure to correct a user's false legal premise; models "cannot always predict, or do not always know, when they are producing legal hallucinations") | 2026-10-28 | yes |
| https://doi.org/10.1093/jla/laae003 | Journal of Legal Analysis 16(1):64–93 version of the same paper | §1.2, §2.10 | 2026-10-28 | yes (registry) — DOI and journal reference confirmed from the arXiv record |
| https://arxiv.org/abs/2405.20362 | Magesh, Surani, Dahl, Suzgun, Manning, Ho, *Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools*, arXiv:2405.20362 (2024) | §2.10 (first preregistered evaluation; providers' RAG claims "overstated"; 17%–33% hallucination for Lexis+ AI and Westlaw tools) | 2026-10-28 | yes |

## D. Conference proceedings (table of contents verified, PDFs not opened)

| url | what it is | supports | access date | verified |
|---|---|---|---|---|
| https://ceur-ws.org/Vol-3193/ | CEUR-WS Vol-3193, ICLP 2022 Workshops proceedings, table of contents | §2.5 (titles, authors and venue for the three papers below) | 2026-10-28 | yes |
| https://ceur-ws.org/Vol-3193/paper4GDE.pdf | Morris, *Blawx: Web-based User-Friendly Rules as Code* (GDE 2022) | §2.5 | 2026-10-28 | no — PDF fetch blocked by the fetcher; title/author/venue verified from the ToC above, paper content **not** read |
| https://ceur-ws.org/Vol-3193/paper5GDE.pdf | Sartor, Dávila, Billi, Contissa, Pisano, Kowalski, *Integration of Logical English and s(CASP)* (GDE 2022) | §2.5 | 2026-10-28 | no — same: ToC-verified metadata, content not read |
| https://ceur-ws.org/Vol-3193/paper3GDE.pdf | Lim, Mahajan, Strecker, Wong, *Automating Defeasible Reasoning in Law with Answer Set Programming* (GDE 2022) | §2.5 | 2026-10-28 | no — same |

## E. Attempted and failed (kept, because a failure is evidence)

| url | what it is | supports | access date | verified |
|---|---|---|---|---|
| https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights | ICCPR, OHCHR treaty page — intended for Art. 15 (non-retroactivity) | §2.8 (would support the primary text of non-retroactivity) | 2026-10-28 | no — HTTP 403 to this environment. Claim marked `[unverified]` |
| https://constitution.congress.gov/browse/article-1/section-9/ | US Constitution Art. I §9 — intended for the ex post facto clause | §2.8 | 2026-10-28 | no — HTTP 403. Not substituted with a secondary source |
| https://github.com/QuantLaw/ProLEAP | intended to be the ProLEAP legal-reasoning project | §2.5 | 2026-10-28 | no — HTTP 404 |
| https://api.github.com/search/repositories?q=ProLEAP | GitHub repository search for "ProLEAP" | §2.5 (negative evidence: 41 hits, all COBOL/VB6/ANTLR parser projects, none legal) | 2026-10-28 | yes, as negative evidence — the search ran and returned no legal-reasoning system |
| https://www.blawx.com/ | intended to be the Blawx project site | §2.5 | 2026-10-28 | no — HTTP 200 but the domain now serves unrelated gambling content. The Blawx claim therefore rests only on the CEUR ToC row |
| https://raw.githubusercontent.com/smucclaw/dsl/main/README.md | intended README for L4 | §2.4 | 2026-10-28 | no — HTTP 404 (no README at that path). Replaced by the GitHub API metadata row |
| https://raw.githubusercontent.com/CatalaLang/catala/main/README.md | intended Catala README | §2.3 | 2026-10-28 | no — HTTP 404. Replaced by the arXiv HTML full text, which carried the load |

---

## Claims marked `[unverified]` in 02-DESIGN-SPACE.md

Listed here so they can be closed rather than forgotten.

| Claim | Status | What would verify it |
|---|---|---|
| Primary text of non-retroactivity (ICCPR Art. 15 / ECHR Art. 7) | `[unverified]` — both primary hosts returned 403 | Fetch the instrument text from a reachable mirror, or cite a law-report copy with a pinpoint |
| `lex specialis` / `lex posterior` as stated doctrines | `[unverified]` as to text; described, not quoted | A conflicts-of-laws authority (e.g. a treatise or the ILC fragmentation study) with a pinpoint |
| Existence and identity of "ProLEAP" | `[unverified]` — no citable URL found; repository 404, GitHub search returns unrelated parsers | A paper or repository URL for a legal-reasoning system of that name |
| "s(LAW)" as the name of the CCLAW statute→logic pipeline | `[unverified]` — the JURIX 2022 abstract does not use the name | A CCLAW publication or repository that uses the name |
| A Lean 4 formalization of statutory or deontic norms | `[unverified]` negative — arXiv search found only mathematical/cryptographic Lean work | Systematic search of arXiv, DBLP, the Archive of Formal Proofs and the Lean community index for "law/legal/deontic" |
| Blawx's editor being graphical/block-based and aimed at non-programmers | **not claimed** — the only support was a PDF abstract that could not be opened | Open `paper4GDE.pdf` and quote it |
| L4's "Exceptions and defaults" concept page | **not claimed** — page not read | Open https://legalese.com/l4/concepts/legal-modeling/default-reasoning |
| Akoma Ntoso fragment-identifier stability across independent publishers | **open question**, not a claim | Two independently published Akoma Ntoso expressions of the same Act, compared |

---

## Internal references (not sources)

| path | role |
|---|---|
| [`AGENTS.md`](../AGENTS.md) | the repository contract: citation of numbers, anchor-or-refuse, no gate weakening, `lab/` records |
| [`docs/10-SPEC-v0.1.md`](10-SPEC-v0.1.md) | canonical: statement model, anchor conditions, verdicts, coverage, §11 limitations |
| [`docs/11-REFUSAL-CODES.md`](11-REFUSAL-CODES.md) | canonical: the closed vocabulary of refusals |
| [`docs/00-CHARTER.md`](00-CHARTER.md) | why the project exists and what it refuses to do |

---

## Counts

- Rows in A–D: **28**
- Verified **yes** in A–D: **23**, of which **8** are `yes (registry)` (bibliographic only)
- Verified **no** in A–D, retained as evidence: **5**
- Rows in E (attempted and failed): **7** — **1** yes, used as negative evidence; **6** no
- Claims still marked `[unverified]` in the survey: **5**, matching **5** inline markers
- Claims deliberately **not** made (documented so they are not quietly assumed): **3**
