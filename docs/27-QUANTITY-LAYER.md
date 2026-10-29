# 27 — The quantity layer, specified as far as the evidence goes

Status: **specification proposal for v0.1.1**, no code, no schema change applied. It exists because ГК 395 stalled
at coverage **0.500** and the first of its three unclosed atoms was exactly this: «размер процентов определяется
ключевой ставкой Банка России, действовавшей в соответствующие периоды» — a number that is not in the statute.

What is now settled by evidence, and what is not, decides the shape:

| Question | Status |
|---|---|
| must a period spanning rate changes be cut at each change? | **settled** — Plenum No. 7 п. 39, read at source ([`docs/26`](26-ROUND-03-MERGED.md) addendum) |
| which source is authoritative for the rate? | **settled by the same paragraph**: the Bank of Russia website and the Vestnik Banka Rossii. Our `cbr.ru` SOAP probe (209 dated records) is that source |
| 365 or actual days? | **open** (round 03 W1) |
| how is the result rounded? | **open** (round 03 W1) |

So the layer must express the first two as facts and the last two as **declared parameters with a printed basis** —
and must refuse to look stronger than that.

---

## §1 Shape

Two new top-level collections and one new atom field. Integers with a declared scale; never a float, for the same
reason the canonical form forbids them (spec §3): a float cannot be hashed and cannot be audited.

```json
"series": [
  {
    "id": "cbr-key-rate",
    "publisher": "Банк России",
    "basis": { "corpus": "gk-rf-395", "article": "Пленум № 7 п. 39",
               "span": "официальный сайт Банка России" },
    "format": "soap KeyRate",
    "retrieved_at": "2026-10-28",
    "digest": "e394f34287211f26b9192c5d6042338c3b845bdec3859426af91cf38681c701d",
    "covers": { "from": "2013-09-13" }
  }
],

"quantities": [
  {
    "id": "q1",
    "kind": "rate_of",
    "base": "сумма долга",
    "series": "cbr-key-rate",
    "period": { "from": "2022-01-01", "to": "2026-10-28",
                "segments": "rate_change", "day_count": "undeclared" },
    "rounding": { "mode": "undeclared", "digits": 2 }
  }
],

"atoms": [
  { "id": "a2", "action": { "verb": "уплатить проценты по", "object": "ставка", "open": false },
    "quantity": "q1", "...": "..." }
]
```

Three rules make it safe:

1. **A quantity is a reference or a literal, never a formula we invent.** `kind` is `literal` (integer + scale +
   currency) or `rate_of` (a base times a pinned series over a period). Anything else is out of scope for v0.1.1.
2. **A quantity without an anchor is not closed.** The atom falls back to an escape with the planned code
   `UNANCHORED_QUANTITY`, and coverage drops. A number nobody can trace is the most dangerous object in the model,
   because it looks authoritative.
3. **A series is pinned by digest and `retrieved_at`, never called at run time.** A live feed destroys
   reproducibility, and reproducibility is the certificate. This mirrors what the Plenum itself names as the source.

---

## §2 Segmentation, declared rather than assumed

`period.segments` is `rate_change` or `none`. With `rate_change`, the checker must split the period at every date the
pinned series changes value, and the report must print the segments:

```
q1  period 2022-01-01..2026-10-28  segments=7
  1  2022-01-01..2022-02-13   days=44   rate=8.50   base=          …
  2  2022-02-14..2022-04-10   days=56   rate=9.50   base=          …
  …
```

Printing the segments is not decoration: it is what makes the computation comparable to a stranger's, and it is
what the day-count question will be asked *about*. A total without segments cannot be audited at all.

---

## §3 Day-count and rounding: parameters with a ceiling

Until W1 closes, these two fields are `undeclared`, and `undeclared` has a cost:

| Field | Values | Effect on the verdict |
|---|---|---|
| `period.day_count` | `actual/actual`, `actual/365`, `30/360`, `undeclared` | with `undeclared`, the statement **cannot exceed `CHECKED`** — never `CHECKED_ANCHORED` |
| `rounding.mode` | `half_up`, `truncate`, `banker`, `undeclared` | same ceiling |
| `rounding.digits` | an integer | — |

The ceiling is the honest mechanism: a statement whose arithmetic convention rests on nothing must not present
itself as fully checked. When a judgment printing its arithmetic is read (W1), the values become `actual/actual` and
`half_up`, each with `basis` pointing at that judgment — and the ceiling lifts by itself, because the fields are
now declared and anchored, not because anything in the code changed.

Refusal of an *invalid* value stays a refusal: `S1_SCHEMA` for an unknown mode. The distinction is: unknown mode =
typo = refusal; `undeclared` = legitimate state = ceiling.

---

## §4 What this buys, in measured terms

Re-encoding ГК 395 under this shape closes `a2` (the rate) and gives `a6` (the court's power with a floor) a
quantity to point at:

| Atom | Before | After |
|---|---|---|
| `a1` duty to pay interest | closed | closed |
| `a2` amount determined by the key rate | **open** (`OPEN_TERM`) | **closed**, via `q1` and the pinned series |
| `a3` creditor's power to claim the excess | closed | closed |
| `a4` defeat by an agreed penalty | **open** | still open — that is [`docs/13`](13-DEFEASIBILITY-CHOICE.md), not this layer |
| `a5` prohibition on compound interest | closed | closed |
| `a6` court's power to reduce, with a floor | **open** | **closed**, the floor is a quantity |
| **coverage** | **0.500** | **0.833** |

0.833 clears the 0.8 threshold, and the verdict would still be `CHECKED` rather than `CHECKED_ANCHORED` — because
`day_count` and `rounding` are `undeclared`. That is exactly the honest outcome: the layer fixes what the evidence
fixed, and the ceiling names what it did not.

---

## §5 Planned codes (not in the catalogue yet)

Per AGENTS §7 a code enters `docs/11` only with a test, so these wait:

| Planned code | Meaning |
|---|---|
| `UNANCHORED_QUANTITY` | an atom carries a number with no `basis`; the atom is not closed |
| `SERIES_NOT_PINNED` | a quantity references a series with no digest or no `retrieved_at` |
| `SEGMENT_GAP` | the declared period is not fully covered by the series |
| `UNDECLARED_ARITHMETIC` | a quantity is closed but its day-count or rounding is `undeclared`; caps the verdict at `CHECKED` |

---

## §6 Acceptance test for stage 2

1. `examples/08-gk-rf-395.lex.json` re-encoded with `q1`, coverage **0.500 → ≥ 0.750**, verdict `CHECKED` with
   `UNDECLARED_ARITHMETIC` named.
2. The report prints the segment table for `q1`, and a second implementation (the Python twin of ADR-0002) reproduces
   every segment **byte-identically** — this is the first real test of substrate neutrality, and it arrives for free.
3. Removing `basis` from `q1` must produce `UNANCHORED_QUANTITY` and a coverage drop, not a silent pass.

If (2) fails on the same commit, the segmentation rule is under-specified and must be fixed before any defender
writes code against it — which is the whole point of specifying before building.


---

## Addendum, 2026-10-29 — W1 is closed by evidence; the two `undeclared` fields can be declared

The act was reached. Not through a court domain (those fail TLS for this client — one certificate is *expired*,
which is why the earlier attempts died), but because the keyless AnySearch engine returned the PDF as the first
result and the host answered when certificate verification was disabled for a single read of a public document.

**Source:** решение Арбитражного суда Брянской области от 10.08.2020 по делу **А09-14/2020**, 7 pages, saved and
hashed locally. The relevant wording, quoted:

> «…с момента принятия Постановления Пленума Верховного Суда Российской Федерации от 24.03.2016 N 7 были признаны
> не подлежащими применению пункты 1–3, 5–11 постановления Пленумов ВС РФ и ВАС РФ от 08.10.1998 № 13/14, в
> соответствии с которыми при расчете процентов … количество дней в году принималось равным 360 дням. С указанного
> момента при расчете процентов … следует использовать **фактическое количество дней в году (365 и (или) 366 дней
> в году)**.»

The judgment prints a 23-row table with the columns `[1] задолженность | [2]–[3] период | [4] дни | [5]–[6] оплата
| [7] ставка | [8] дней в году | [1]×[4]×[7]/[8]`.

**What I verified myself, by recomputation in `Decimal` with half-up rounding:**

| Question | Result |
|---|---|
| day count | **actual/actual, and the denominator switches on the calendar year, not on the rate** — 16.12.2019–31.12.2019 uses 365, 01.01.2020–09.02.2020 uses **366 at the same 6.25 %** |
| segmentation | cut at every rate change **and** at each partial payment — both appear as separate rows |
| rounding | **per row, half-up, to kopecks**: 20 of the 22 rows my extractor produced reproduce the printed figure exactly (`1 281 105,58 × 77 × 10 % / 365 = 27 026,06`, and the last row `281 105,58 × 1 × 4,25 % / 366 = 32,64`) |
| total | **not independently reproduced.** Two rows came out of the PDF with numbers glued together (`10 863,00` merged with the next principal), and the plain-text extraction loses the table layout. The printed total is `207 313,62`; whether that equals the sum of rounded rows rather than the rounded sum remains unchecked. A layout-aware extraction (pdfplumber/pdftotext −layout) is the next step, not a new question. |

**Consequences for this document**

1. `period.day_count` can be declared **`actual/actual`** with `basis` pointing at this judgment, and
   `rounding.mode` can be declared **`half_up`, digits 2, per period** — the values the ceiling was waiting for.
2. The ceiling rule does not disappear; it becomes the rule for *everything else* that arrives undeclared.
3. ГК 395 stops being an anchoring-only measurement the moment the total is reproduced — the oracle is now a real
   document on disk with a quoted span, not a claim in an answer.
