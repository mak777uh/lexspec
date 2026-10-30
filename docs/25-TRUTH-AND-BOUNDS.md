# 25 — What is true here, and where the truth stops

A claim registry. Every statement below is either **verified in this repository** (with the command or artifact
that verifies it), **conditionally true** (with the condition named), or **not claimed**. If a sentence is not in
this document, it is not a claim of this project.

Written because "we establish truth" is a sentence that means nothing until it is cut into pieces small enough to
fail individually.

---

## §1 The only sense of "true" used here

Three primitives, and nothing beyond them:

| Primitive | Question | What makes it true |
|---|---|---|
| **resolves** | does this reference point at one place in this pinned text? | the span occurs exactly once in the file, and the file's digest matches the declaration |
| **matches** | do these two things agree? | a digest comparison, or a reproduced figure, or a checker that recomputes |
| **reproduces** | can a stranger get the same answer? | running the command in this repository on this commit |

"True about the law" is **not** among them. It is not that we doubt the law; it is that our artifacts cannot
carry that claim, and a claim an artifact cannot carry is not made here.

---

## §2 Verified now

Each row was produced in this session and can be re-run.

| # | Claim | Verified by | Boundary — where it stops being true |
|---|---|---|---|
| 1 | The spec, the schema, the refusal catalogue and the examples do not contradict each other across eight dimensions | `python lab/check-spec.py` → clean; and `python lab/selftest-checkspec.py` → **4 of 4** injected defects caught | consistency, not completeness: two documents can agree and both be wrong about the world |
| 2 | The consistency guard actually fires | four mutations (phantom code, undocumented field, flipped correlative, float in an example) are each caught | it proves the guard works, not that the spec is *clear* — clarity has no test |
| 3 | Identity of a statement is deterministic | canonical form computed twice gives the same digest; `C0_CANON` refuses CRLF, BOM, floats | this is *our* canonical form, not RFC 8785; no interoperability claim |
| 4 | The refusal vocabulary is closed and exercised | 30 codes; `python tests/run_tests.py` → 80 tests pass; every code appears in an example or a test | codes name defects of an encoding; none of them names a defect of the law |
| 5 | Anchoring works on real provisions | GDPR Art. 17: 4 of 4 atoms anchored, coverage **0.750**; ГК 395: 6 of 6, **0.500**; ЗоЗПП 26.1(4): 4 of 4, **0.250** | "anchored" means *the span occurs once in our file* — and our files are mirrors, not official publications |
| 6 | The Bank of Russia key rate is available as a dated, machine-readable series | SOAP `KeyRate` for 2026 → **209 dated records**, current 14.00 %, response digest `e394f342…` | one year probed; no official worked example exists to compare a computation against |
| 7 | The code → law direction can produce findings | three findings on an illustrative return policy against the anchored ЗоЗПП norm: a 30-day refund against a 10-day rule, a missing 3-month branch, and a boolean standing in for a legal predicate | done by hand, on an illustrative policy, once |
| 8 | The field vocabulary is adopted, not invented | [`docs/22`](22-ADOPTION.md): seven of our fields map onto CAP-RRS's LRI; two of ours are named as *worse*; two of theirs we lacked | reading, not implementation: no code, no schema change yet |
| 9 | Maintenance cost per amendment has never been measured publicly | four independent search rounds, four negatives, witnesses named (OpenFisca-France, PolicyEngine, Catala at CNAF/DGFiP) | a negative search result is not proof of absence |
| 10 | Byte-level anchoring fails often on real wrapped text | **6 of 14** candidate quotes across two articles, because the source wraps at ~100 characters | this measures our quoting procedure as much as the rule (§4, W6) |

---

## §3 Conditionally true

True while the condition holds; the condition is a live question, not a footnote.

| Claim | Condition | If the condition fails |
|---|---|---|
| The chain text → positions → quantities → rules → decisions is specified end to end | CAP-RRS §5's determinism requirement is implementable, and our adoption of its annotation block is exact | stage 2's schema changes, and L6 becomes our own design with no external check |
| Our transition layer is adoption, not construction | Symboleo expresses ГК 450.1, 157(3) and power-with-deadline (round 03, W2) | the layer is ours again, and stage 3 costs 2–4× more |
| Exact-span uniqueness is the right anchoring rule | the field's convention supports it (round 03, W6) | the rule relaxes to a context window, and `S2_SPAN_AMBIGUOUS` changes meaning |
| A verdict can be certified | an evidence package can be assembled from three parts (attestation, renewal, reproducibility), since no single standard covers them (round 02, Q22) | the certificate stays a report, and no claim of evidence is made |
| "Computational provisions first" is the right scope | a provision exists with a stable rule, anchored parameters and an authoritative oracle (round 03, W4) | the product is anchoring + coherence + audit findings, and correctness claims are deleted |

---

## §4 Not true, and not claimed

The boundary list. Each of these would be a lie if the verdict were read quickly, which is why they are written
here and repeated in every report.

1. **Not that a clause is lawful.** No verdict says "legal", "valid", "compliant" or "enforceable".
2. **Not that the encoding is complete.** Coverage is a fraction of *the statement*, and a statement can be a
   faithful encoding of half a clause.
3. **Not that the corpus is law.** Every Russian corpus here is a commercial mirror (ConsultantPlus), labelled in
   its own file as not authoritative; the EU corpus is a mirror because EUR-Lex refused this client.
4. **Not that a term is defined correctly.** Terms are the unanchored part of the model; four of them were closed
   in the GDPR statement with paraphrases nobody anchored.
5. **Not that a verdict survives an amendment.** The certificate has no staleness signal yet; CAP-RRS's
   `SUSPENDED` state is adopted on paper only.
6. **Not that the audit findings are reproducible.** They were produced by hand, once, on an illustrative policy.
7. **Not that we are first.** Two of our three "unbuilt" claims turned out to be specified in public (CAP-RRS,
   Symboleo). A third might be.
8. **Not that the specification is clear.** It is *non-contradictory* on eight mechanical dimensions. Clarity is
   tested by a lawyer reading it, and that test has not been run (charter F1, F4).

---

## §5 Negative results, with how hard we looked

A negative result is a result only if the search is stated.

| Claim of absence | Search | Strength |
|---|---|---|
| No machine-checked proof that two independent encodings of a statute diverge | five rounds, six models, plus a direct search of arXiv and GitHub code search | moderate: strong on arXiv and GitHub, weak on paywalled law reviews |
| No published measurement of maintenance effort per amendment | four rounds, witnesses named, repositories inspected | strong for the English-language literature |
| No official recomputable oracle for ГК 395 | calculators found are court "reference" services or commercial | moderate: a published judgment with full arithmetic would overturn it |
| No regulator-published continuity protocol for switching decision substrates | three rounds; nearest are a treaty (Estonia's Data Embassy) and eIDAS termination plans | moderate |
| No single evidence standard covering attestation + renewal + reproducibility | six independent answers, all aligned | strong |

---

## §6 The boundary of our own boundaries

Things we cannot test even in principle with the current artifacts, listed so nobody assumes they were checked:

1. **Whether our reading of an article matches a lawyer's reading.** No lawyer has reviewed any encoding here.
2. **Whether our corpus copy equals the official text.** We compare digests of our own files; nobody has compared
   them to the Official Gazette.
3. **Whether the drafter's intent is captured.** That is the specification gap; no tool closes it.
4. **Whether a decision made under our compiled rule would survive a court.** That is T3, and it is not a
   property of an artifact.
5. **Whether the system is useful** — no user has used it for anything.

---

## §7 How to attack this document in ten minutes

A hostile reader should not have to trust §2. Three cheap tests, each of which should break something if the
document is wrong:

1. **Pick any span** in any corpus file, run `grep -c`, and check it occurs exactly once. If it occurs twice, row 5
   of §2 is false for that statement.
2. **Delete one code** from `docs/11-REFUSAL-CODES.md` and run `python lab/check-spec.py`. It must fail. If it
   passes, row 1 is decoration.
3. **Open the illustrative policy** in [`lab/audit-2026-10-28-return-policy.md`](../lab/audit-2026-10-28-return-policy.md)
   and check that finding 1 is real: the code says 30 days, the anchored ЗоЗПП norm says ten. If the norm does not
   say ten, row 7 is false.

If all three hold, this document has earned the right to be read as the project's account of what it knows — and
nothing more.


---

## §8 Correction block, 2026-10-28 (round 03)

Appended rather than edited, per the repository's rule that a published statement keeps its wrong sentence next
to the one that fixed it.

**Two verified facts added:**

| Fact | Verified how |
|---|---|
| W3C's `TextQuoteSelector` requires the quote to be **normalized** before recording, and treats multiple matches after prefix/suffix as matching **all** of them | fetched `w3.org/TR/annotation-model`, located the clause by search, quoted verbatim in [`docs/26`](26-ROUND-03-MERGED.md) |
| `publication.pravo.gov.ru/robots.txt` excludes `/Search` and `/File`, and publishes a sitemap of daily, weekly and monthly listings per issuing body | fetched `robots.txt` (286 bytes) and `sitemap.xml` (116 KB) in this session |

**One claim corrected — row 10 was wrong about the cause.** The 6-of-14 span failures were reported as
"byte-level anchoring fails often on real wrapped text". The standard says the text must be normalized before
recording, so those failures are a **normalization gap in our procedure**, not evidence that the rule is
over-strict. The rule *is* over-strict, but for the opposite reason: exact-span uniqueness is not the field's
convention at all (W3C permits multiple matches and selects all of them), so our `S2_SPAN_AMBIGUOUS` is a product
requirement we are entitled to impose — provided we say so, and provided we stop mislabelling line wraps as
ambiguity.

**One claim strengthened.** Row 5's boundary said our corpora are "mirrors". They are official *expressions*
published on pravo.gov.ru, retrieved through a **non-official manifestation**; the defect is transport and
licensing, not authority. The corpus headers now say exactly that.


---

## §9 Verified addition, 2026-10-29

| Claim | Verified by | Boundary |
|---|---|---|
| The anchoring procedure can recover every quote that failed in our real measurements | `tools/span_hint.py` run against the six previously failed quotes — 6 of 6 recovered, each with the raw span including its line break; `python tests/run_span_tests.py` passes 6 of 6 | it recovers quotes that are *present after normalisation*; it cannot recover a quote from a different revision, and it does not decide whether the recovered span says what the atom claims |

This moves the blame for the earlier 6-of-14 failures from the anchoring rule to our procedure — which is where
the standard said it belonged ([`docs/26`](26-ROUND-03-MERGED.md) §W6).


---

## §10 Verified addition, 2026-10-29 — the 395 arithmetic, read from the act itself

| Claim | Verified by | Boundary |
|---|---|---|
| The day count for post-2016 interest is actual/actual, switching at the calendar year | judgment А09-14/2020 (10.08.2020), fetched and saved; wording quoted in [`docs/27`](27-QUANTITY-LAYER.md); the table uses 365 for 16.12.2019–31.12.2019 and **366 at the same rate** for 01.01.2020–09.02.2020 | one first-instance act; not a binding clarification |
| Rounding is per row, half-up, to kopecks | 20 of the 22 rows my extractor produced recompute to the printed figure in `Decimal` with `ROUND_HALF_UP` | two rows were unusable because the PDF text glued adjacent numbers; the **total** is therefore not independently reproduced |
| The rate series' authority is named by the Plenum | Пленум № 7 п. 39, read at source earlier the same day | names the Bank of Russia site and the Vestnik; does not pin a format |

Two incidental facts worth keeping: the Bryansk court's **TLS certificate has expired** (which is why every earlier
attempt died with `UNEXPECTED_EOF`), and **keyless search is available** through `api.anysearch.com`, so discovery
works again without any credential.

---

## §7 Usefulness is not claimed, and now it is said in every report

[`docs/33`](33-PROOF-OF-USEFULNESS.md) measures this repository against a public rubric for "proof of usefulness"
(four dimensions: adoption, revenue, technical stability, problem-solving). Result: three of the four are empty, one is
our strongest evidence, and the asymmetry is stated rather than smoothed — the dimension we can prove is the one that
market weights least.

`not_claimed` in every report now carries a sixth line: **usefulness — no person or organisation outside this
repository has used a verdict in a decision.** A limitation that travels with the artefact is worth more than a
paragraph in a design note.

The longer form of that line is [`lab/usefulness.md`](../lab/usefulness.md): the five questions of a public usefulness
questionnaire, answered with "none" where the answer is none, and the exact rows that would change each answer.
