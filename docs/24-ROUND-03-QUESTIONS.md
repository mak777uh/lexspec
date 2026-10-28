# 24 — Round 03: six walls, one question each

Round 03 exists because six advances are blocked by facts that are not in this repository and cannot be derived
from it ([`docs/23`](23-METHOD-LOOP.md) §2). Each question below carries the five required lines: what is
blocked, what was tried, the ask, what settles it, and what would make it moot.

**Nothing here repeats rounds 01–02.** Where an earlier round covered the neighbourhood, the question is narrowed
to the point that is still open, and the narrowing is stated.

**Protocol.** First line of a reply: your model name and the date — an unsigned answer is discarded. Per question:
one paragraph, plus a source you actually opened or the words "not opened". "I do not know" is a complete answer
and, if the reason is stated, a useful one. Name a witness — a judgment, an endpoint, a spec section, a dataset —
not a category of literature.

---

## W1 — Day-count and rounding for statutory interest when the rate changes

**WALL.** The quantity layer ([`docs/21`](21-IMPACT-PLAN.md) stage 2) cannot be specified without a convention:
ГК 395 art. 1 fixes the rate as "the key rate in force in the relevant periods", and our encoding must decide (a)
365 or actual days in the year, (b) whether an interval is cut at each rate change, (c) how the final figure is
rounded. Without it the layer encodes a choice, and the choice is the law.

**TRIED.** Read art. 395 п. 1–6 in full; confirmed the Bank of Russia publishes the key rate as a dated series
(209 records for 2026 over its SOAP service); read how Catala and Arxo treat money (Arxo keeps money exact and
rounds only where the text says so). The statute itself states no convention.

**ASK.** In Russian judicial practice after 1 August 2016, when a delay period spans one or more key-rate changes:
is the day count 365 or the actual number of days, are the intervals segmented at each change, and how is the
result rounded? Cite a judgment or a Supreme Court clarification that shows the arithmetic, not only the result.

**SETTLES.** A judgment (or a Пленум ВС clarification) with principal, start and end dates, the rate periods
applied, and the computed figure — enough for a stranger to reproduce the number and compare conventions.

**MOOT.** If the statute or a binding clarification states the convention in words, the question becomes
verification rather than research.

---

## W2 — Does Symboleo express the three Russian transition cases?

**WALL.** [`ADR-0009`](../lab/decisions/ADR-0009-transition-layer.md) now says our transition layer adopts
Symboleo's vocabulary rather than inventing one. That is only true if Symboleo actually covers the cases that put
us here — otherwise the layer is construction again, and the plan's stage 3 changes.

**TRIED.** Read the RE 2020 and SoSyM 2022 papers' descriptions: contract ontology with legal positions,
obligations, powers, events and lifecycle statecharts. Did not find a construct for notice-triggered termination,
for a condition deemed fulfilled because of bad faith, or for a power whose exercise creates a duty with a
deadline.

**ASK.** In Symboleo's published semantics, is there a construct (or an idiomatic pattern) for each of: (a) a
unilateral notice that terminates or changes the contract (ГК 450.1); (b) a condition treated as fulfilled because
a party in bad faith prevented it (ГК 157(3)); (c) exercise of a power that creates a duty in the counterparty
subject to a deadline. Name the construct and its section, or say plainly that it does not exist.

**SETTLES.** A page or section reference per case, or an explicit negative with the closest construct named.

**MOOT.** If we drop the transition layer from scope — which would also drop contract clauses as a target domain.

---

## W3 — What replaces an authority endorsement where nobody will sign

**WALL.** CAP-RRS binds every record to an `endorsement` signed by an `authority_id` with a legal character
(`statute_clear`, `interpretive_ruling`, …). In our setting no regulator issues signed machine-readable records, so
either the certificate has no legitimacy anchor, or something else takes its place. Stage 5 cannot be specified
until we know which.

**TRIED.** Read CAP-RRS §9 (LRI, endorsement, co-endorsement, signed JWT) and §10 (statute-primacy, interpretation
supersession). Checked RFC 4998 / TR-ESOR (evidence preservation, no authority condition) and FRE 902(13)/(14)
(certification by a qualified person about the process).

**ASK.** In settings where no authority signs machine-readable records, what is accepted in practice as the
equivalent evidence of authoritative interpretation — a published judgment, official Q&A, supervisory guidance, a
consolidated text from an official publisher? Name a jurisdiction, the artifact, and what verification it
supports.

**SETTLES.** A named artifact type with one concrete example, plus a statement of what it proves and what it does
not.

**MOOT.** If we restrict the product to deployments where a signing authority exists (regulated entities, certified
publishers).

---

## W4 — A provision with fully published arithmetic

**WALL.** [`ADR-0008`](../lab/decisions/ADR-0008-computational-first.md) requires an authoritative oracle before a
provision can be used as a *correctness* test. We have none, so every measurement so far is an anchoring
measurement. Without an oracle the correctness half of the product has no ground truth.

**TRIED.** Searched for official calculators for ГК 395: the court calculators found are explicitly "for
reference", and the commercial ones are not authoritative. No published worked example with full inputs.

**ASK.** Name **any** provision — tax, benefit, fee, penalty, interest — for which an official body publishes both
the inputs and the complete arithmetic of a computed example, so that a stranger can reproduce the figure from
public data. Give the link and the numbers.

**SETTLES.** A link whose example lists inputs (amounts, dates, rates, categories) and a resulting figure we can
recompute.

**MOOT.** If we accept anchoring-only and delete every correctness claim from the product description.

---

## W5 — Official machine-readable access to Russian federal acts

**WALL.** Every Russian corpus we have is a commercial mirror (ConsultantPlus), which we must label "not
authoritative". That weakens the anchor claim for the entire Russian side of the two-jurisdiction plan.

**TRIED.** `pravo.gov.ru` returned a document page without article text to this client; `docs.cntd.ru` redirected;
`publication.pravo.gov.ru` was not probed with a documented API. ConsultantPlus served the text, with a current
revision date.

**ASK.** Is there a documented endpoint or file format through which an official Russian source serves the **full
text** of federal acts, including consolidated versions, to automated clients — and what are its terms of use?
Show the request pattern and a sample response.

**SETTLES.** A documented URL/API pattern with a sample of the returned text and the licensing terms.

**MOOT.** If no such access exists, in which case the Russian corpus is permanently labelled a mirror and the
anchor claim is restricted accordingly — a legitimate outcome we would state.

---

## W6 — What the accepted convention is for quote uniqueness

**WALL.** Our `S2_SPAN_AMBIGUOUS` refuses a quote that occurs more than once, counted by start position with
overlaps. In two real measurements, **6 of 14 candidate quotes failed** — and most of those failures were not
ambiguity but line wrapping. Either the rule is over-strict or our quoting procedure is wrong, and we cannot tell
which without knowing what the field does.

**TRIED.** Read our own measurements ([`lab/cost.md`](../lab/cost.md)); read ELI/Akoma Ntoso/CAP-RRS anchoring
requirements, which stop at "resolvable to a unique operative clause" and say nothing about quote uniqueness.

**ASK.** In established conventions for anchoring a quotation in a text — W3C Web Annotation `TextQuoteSelector`
with prefix/suffix, Akoma Ntoso `eId`, legal-NLP annotation corpora — how is uniqueness handled in practice: exact
span, span plus surrounding context, or character offsets? Is exact-span uniqueness ever required, and what
failure rates are reported?

**SETTLES.** The specification section describing the selector and its ambiguity handling, plus any reported
measurement of failure rates on real legal text.

**MOOT.** If we relax to context-window uniqueness; then the question becomes which window, and that is answered
by the same sources.

---

## What happens to the answers

Each answer lands as a row in [`lab/sources.md`](../lab/sources.md) with a grade, and the blocked artifact gets a
dated note in the document that owns it. An answer of "does not exist" is recorded as such and the corresponding
claim is deleted from the spec — not softened. Six negatives would close the loop for this stage, and that is a
result, not a failure.
