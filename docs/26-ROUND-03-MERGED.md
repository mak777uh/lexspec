# 26 — Round 03, merged: one rule of ours is wrong, and the oracle problem is solved

Six answers to [`docs/24`](24-ROUND-03-QUESTIONS.md) arrived on 2026-10-28/29. Two claims were decisive enough that
I opened the primary sources myself, and both held — which means two of our documents now say something false.

---

## W6 — our anchoring rule is wrong, and the standard says so

**Verified verbatim** in the W3C Recommendation of 23 February 2017, §4.2.4 *Text Quote Selector*
([w3.org/TR/annotation-model](https://www.w3.org/TR/annotation-model/), fetched and grepped in this session):

> "The text **MUST be normalized before recording** in the Annotation. Thus HTML/XML tags SHOULD be removed, and
> character entities SHOULD be replaced with the character that they encode."
>
> "If, after processing the prefix, exact, and suffix, the user agent discovers **multiple matching text
> sequences**, then the selection **SHOULD be treated as matching all of the matches**."

Three consequences, and the first two are corrections to us:

1. **Our 6-of-14 span failures were a normalization gap, not ambiguity.** A quote that crosses a line break is
   not a repeated quote; it is a quote recorded against unnormalized text. Calling it `S2_SPAN_AMBIGUOUS`
   mislabels our own defect as a defect of the input.
2. **Exact-span uniqueness is stricter than the standard.** W3C does not require the wording to occur once; it
   requires `exact` plus `prefix`/`suffix` to *identify* a region, and when several matches remain it explicitly
   says to treat the selection as matching **all** of them. Our rule silently turns a legal-text convention into
   a product requirement — which is allowed, but must be declared as *our* requirement, not as the field's.
3. **The right shape is: normalized text + quote + context window + optional offsets**, with a hard failure only
   when the combined locator is *still* ambiguous. That is a spec change, not a code tweak.

**Decision (spec, v0.1.1 planned).** `anchor` gains `prefix`/`suffix` (or a declared context window), the corpus
is normalized before matching with the normalization policy recorded in the statement, and the two refusals are
separated:

| Code | Meaning now | Meaning after the change |
|---|---|---|
| `S2_SPAN_NOT_FOUND` | the quote does not occur | the quote does not occur **after normalization**; the detail says whether it occurs in the raw text (i.e. it was a line-wrap/entity problem) |
| `S2_SPAN_AMBIGUOUS` | the exact span occurs more than once | the quote **with its context** still selects more than one region |

Our product still needs one target — a citation that selects three places is not a citation. But the refusal now
names which condition failed, and the common case (line wrapping) becomes fixable instead of mysterious.

---

## W4 — the oracle problem is solved, four times over

**Verified arithmetic myself** for the first candidate: GOV.UK's published residential SDLT example, a house
bought in April 2025 for GBP 295,000 —

```
first 125,000    × 0% =      0
next  125,000    × 2% =  2,500
rest   45,000    × 5% =  2,250
                  total   4,750
```

That is band arithmetic, fully published, reproducible by a stranger from the page. Three more candidates the
answers named, each official and each publishing intermediate values:

| Oracle | What it publishes | Why it matters |
|---|---|---|
| GOV.UK SDLT example | inputs, bands, rates, intermediate amounts, result | a *progressive bands* fixture — directly comparable to quantities with periods |
| US SSA PIA bend points | 1977 AWI 9,779.44, 2025 AWI 72,800.33, 1979 bend points 180 / 1,085, the division and the rounding to the dollar | a *referenced-index* fixture, structurally the same as our key-rate case |
| ФНС России, УСН «доходы минус расходы» | income 25,000,000; expenses 24,000,000; base 1,000,000; 15 % = 150,000; minimum tax 1 % = 250,000; payable = the minimum | a *comparison of two rules* fixture — our `defeat` case in numeric form |
| ФНС России, НДФЛ на вклады 2023 | three deposits, taxable interest 154,597; threshold 150,000; 4,597 × 13 % = 598 | a *threshold* fixture |

**Decision (ADR-0008 addendum 3).** The requirement "an authoritative oracle must exist" is **satisfiable**, and
the first fixture is SDLT because its arithmetic is short enough to reproduce by hand. ГК 395 remains the
anchoring test; it is no longer the only candidate for a correctness test.

**A caution the answers supplied and I keep:** even an official oracle can omit the rounding step — SSA's own
companion page yields a figure reproducible only by truncating to the next lower $0.10, which that page does not
state. So a fixture is only usable if the *rounding rule is printed*, not inferred.

---

## W1 — segmentation settled, arithmetic still open

Three of four answers cite Пленум ВС РФ № 7 (24.03.2016), as amended 07.02.2017: for periods after 1 August 2016
the rate is the key rate "действовавшая в соответствующие периоды", which forces segmentation at each rate change.
That part is settled.

The day-count (365/366) and the rounding rule are **not** settled by any binding text we opened ourselves. One
answer claims a first-instance judgment (А09-14/2020, 10.08.2020) that prints a 23-row table and settles both —
actual/actual with the denominator changing at 1 January, per-period rounding to kopecks, sum of rounded rows
reproducing the awarded figure exactly. **`[unverified]` — I did not open that PDF.** If it holds, it is the
oracle W1 asked for; until then our quantity layer must encode the convention as a *declared choice with a cited
authority*, not as a fact.

---

## W2 — Symboleo covers two cases, not the third

Three answers converge, and the divergence between them is the useful part:

- **(a) notice-triggered termination** — yes, idiomatically: a notice is a domain event and the termination is a
  `Power` whose antecedent references it; one answer names `PterminateAgreement`.
- **(c) power creating a duty with a deadline** — yes in the ontology (powers carry deadlines; obligations carry
  deadlines), but the *composition* (power consequent creating a timed obligation) has no published worked
  example that anyone found. Treat as an implementation risk, not as covered vocabulary.
- **(b) ГК 157(3), bad faith deeming a condition fulfilled** — **no.** Symboleo has no Condition class; its
  semantics is a deterministic event calculus over observed events, and a legal fiction that deems an unobserved
  condition satisfied has no operator there.

**Decision (ADR-0009 addendum 2).** Adopt Symboleo for (a) and (c). For (b), say plainly that it is a
domain-specific rule authored by us, with the statute as its basis — a *rule*, not a vocabulary item.

---

## W3 — authenticity is not authority, and both are separable

The answers agree there is no universal substitute for a signed endorsement, and they split the problem usefully:

| Layer | What can carry it | Example |
|---|---|---|
| **authenticity of the text** | a signed official publication | EU electronic Official Journal with a qualified electronic signature (Reg. (EU) 216/2013), verifiable by a third party |
| **interpretive authority** | a published doctrine regime with a defined reliance effect | France, Livre des procédures fiscales art. L80 A: published instructions bind the administration against reassessment |
| **responsibility for the encoding** | nothing but us | a `self_asserted_no_authority` marker on the endorsement |

**Decision.** The certificate carries three separate fields and never merges them; the CAP-RRS `endorsement` is
adopted only where an authority genuinely signs, and elsewhere the record says `self_asserted_no_authority` and the
verdict cannot reach the strongest label.

---

## W5 — the Russian corpus is not "just a mirror", and the portal says what it allows

**Verified myself:** `http://publication.pravo.gov.ru/robots.txt` — 286 bytes, and it names exactly what is
excluded from crawling:

```
Disallow: /Search
Disallow: /File
```

plus a `Sitemap:` line. The sitemap (116 KB) lists daily, weekly and monthly document listings per issuing body.
So: **machine-readable discovery of official publications exists; search and file download are explicitly outside
the sanctioned surface.**

Combined with the answers' legal finding — that consolidated texts placed on the portal became official in 2022,
with mandatory status labels and preparation deadlines (`[unverified]` by us: we did not open the decree or the
FSO order) — the honest label for our Russian corpora changes from "commercial mirror, not authoritative" to:

> an **official expression** published on pravo.gov.ru, retrieved through a **non-official manifestation**
> (a commercial database), with no sanctioned automated full-text access verified from outside.

That is a smaller claim than "it is the law" and a larger one than "it is a mirror", and it is what the evidence
supports today.

---

## What changed in the repository as a result

| Document | Change |
|---|---|
| [`docs/10`](10-SPEC-v0.1.md) §5 | the span rule is corrected: normalization first, then quote + context, and the two refusals split by cause |
| [`docs/11`](11-REFUSAL-CODES.md) | `S2_SPAN_NOT_FOUND` and `S2_SPAN_AMBIGUOUS` re-worded; the first now says the quote may be a line-wrap or entity artefact |
| [ADR-0008](../lab/decisions/ADR-0008-computational-first.md) | addendum 3: the oracle requirement is satisfiable; four fixtures named; SDLT first; rounding must be printed |
| [ADR-0009](../lab/decisions/ADR-0009-transition-layer.md) | addendum 2: (a) and (c) adopted from Symboleo, (b) is authored per statute |
| [`docs/25`](25-TRUTH-AND-BOUNDS.md) | §2 rows corrected: 6/14 is a normalization gap, not ambiguity; two new verified facts (W3C clause, robots.txt) |
| corpus headers (RU) | the label becomes "official expression, non-official manifestation" |

**What did not change:** the two-jurisdiction plan, the refusal vocabulary's size, and the stage order. W4 unblocks
stage 2 rather than reordering it, and W6 makes stage 1 smaller than planned — `span_hint` is now "normalize, then
report the byte-exact span", which is a strictly easier tool.


---

## Addendum, 2026-10-29 — W1's segmentation and rate source are now verified, not quoted

After `pypdf` was installed, the court PDFs turned out to be unreachable anyway (TLS failure to `vsrf.ru`,
`sudact.ru`, `kad.arbitr.ru`, `garant.ru`). But `consultant.ru` answers, and it carries the Plenum text. Reading
п. 39 directly produced this sentence:

> «…размер процентов за пользование чужими денежными средствами, начисляемых за периоды просрочки, имевшие место
> после 31 июля 2016 года, определяется на основании **ключевой ставки Банка России, действовавшей в
> соответствующие периоды** (пункт 1 статьи 395 ГК РФ в редакции Федерального закона от 3 июля 2016 года
> N 315-ФЗ)».

And, immediately after it, a sentence we had not been told about and which matters more for the quantity layer:

> «Источниками информации о средних ставках банковского процента по вкладам физических лиц, а также о ключевой
> ставке Банка России являются **официальный сайт Банка России в сети "Интернет"** и официальное издание Банка
> России "Вестник Банка России"».

**Three consequences.**

1. **Segmentation is verified**: the rate is the one "in force in the relevant periods", so a delay spanning rate
   changes must be cut at each change. What three answers said, now read at source.
2. **The authority for the rate series is named by the Plenum itself** — the Bank of Russia website. Our SOAP
   probe of `cbr.ru` (209 dated records) is therefore not a convenience, it is the source the ruling points at.
   The quantity layer can cite it: `basis: Plenum No. 7 п. 39` → `series: cbr.ru key rate` → digest.
3. **Day-count and rounding remain open.** Nothing in п. 39 states them, and the claimed 23-row judgment
   (А09-14/2020) is behind a TLS wall from this machine. Until it is read, the quantity layer encodes those two as
   **declared parameters with a cited authority**, printed in every report — not as facts.

The `[unverified]` marking on that judgment stands, and the reason is now specific: not "we did not look", but
"the host refuses this client at TLS".
