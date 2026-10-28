# Cost of encoding, measured

The unit of account is the **closed atom**, and the number that decides whether this project survives is
minutes per article (charter falsifier F3, method §6). This file records every real measurement, including the
failed attempts — a cost table that omits the failures is a press release.

Nothing here is an estimate unless it says `estimate`.

| # | clause | atoms | closed | open | minutes to first verdict | minutes to pass | codes hit | origin |
|---|---|---|---|---|---|---|---|---|
| 1 | GDPR Art. 17 (CELEX 32016R0679), revision 2026-10-28 | 4 | 3 | 1 | ~9 (session wall clock) | — (stops at `CHECKED`) | two span-uniqueness misses caused by line wrapping, then `OPEN_TERM`, `THIN_COVERAGE` | model:deepseek-v4.1-flash@2026-10-28 |
| 2 | ГК РФ ст. 395 (ред. 03.07.2016 / 08.03.2015), ревизия 2026-10-28 | 6 | 3 | 3 | ~14 (session wall clock) | — (stops at `CHECKED`, coverage 0.500) | three spans failed on line wrapping, then three escapes — one per missing layer — and `THIN_COVERAGE` | model:deepseek-v4.1-flash@2026-10-28 |

## Measurement 2 — ГК РФ ст. 395, the computational provision ADR-0008 selects

**Why this article.** It is the first corpus of the pivot: interest on a monetary obligation, where the rate
arrives by reference to the Bank of Russia key rate, and where the article carries two carve-outs and a court
power with a floor.

**Result.** `CHECKED`, **coverage 0.500** (3 of 6 atoms closed), **6 of 6 anchored**, 0 refusals, 3 escapes.
Statement `8f90e5f4…`, corpus `798ff59f…`, example
[`08-gk-rf-395.lex.json`](../examples/08-gk-rf-395.lex.json).

**What the numbers say, and it is the cleanest result the project has produced so far.** The three unclosed atoms
are not three arbitrary gaps — they are the three layers the architecture has been asking for, each met in one
article:

| Escape | Atom | Missing layer |
|---|---|---|
| `a2` — «размер процентов определяется ключевой ставкой» | the duty to pay at a rate that is *not in the statute* | **L5 quantity**: an external dated series, pinned by digest. Verified available: 209 dated records of the key rate for 2026 over the Central Bank's SOAP service |
| `a4` — «проценты не подлежат взысканию» при согласованной неустойке | a provision that *removes* the claim of п. 1 | **defeat** ([`docs/13`](../docs/13-DEFEASIBILITY-CHOICE.md)) |
| `a6` — court may reduce the interest «но не менее чем до суммы по ставке п. 1» | a power bounded below by a quantity | **quantity inside a position**, i.e. L5 and the power construct together |

So a real computational provision — the kind ADR-0008 says the product is for — is **half encodable in v0.1**,
and the other half is exactly the roadmap. That is a much stronger argument for the layer order than any of the
twenty hypotheses: the article needed all three, at once, in six atoms.

**Second finding, now systematic.** Three of six candidate spans failed again because the source wraps at ~100
characters and the quote crossed a line break (measurement 1: three of five). Across two real articles, **6 of 14
candidate spans** were rejected for this reason. The checker is right and the experience is bad: the refusal says
"span does not occur", when the useful message is "it occurs after collapsing line breaks at offset N; copy the
bytes". A `span_hint` helper that reports the byte-exact span is now the highest-value small tool in the project.

**Third finding.** The article is a better test of the model than either earlier one: it exercises power (п. 2,
п. 6), a prohibition expressed as a correlative duty (п. 5), a temporal condition (п. 3), and two independent
carve-outs (п. 1, п. 4). Four of the six atoms are *second-order* positions — which is the Hohfeld layer doing
real work rather than decorating a contract clause.

## External baselines (not our measurements — quoted from primary sources)

These exist so that our own numbers have a scale. Verified by reading the paper text, not a summary
([`docs/16` §1](../docs/16-ROUND-01-ANSWERS.md)).

| Source | Artifact | Size | Effort |
|---|---|---|---|
| Catala (arXiv 2103.03198 §6.3) | French family benefits: 27 articles of the Social Security Code + orders | ≈1,500 lines including the law text; 6 scopes, 63 context variables, 83 definitions and rules | not stated; presented by the authors as representative of "a medium-size legal document" |
| Catala (§6.3) | US IRC §121 up to (b)(4) — ≈15 % of one complex section | ≈350 lines including the law text | four 2-hour pair sessions with tax lawyers ≈ 8 pair-hours ≈ 16 person-hours |
| Catala (§4.5) | F\* mechanisation of the compiler core | ≈3,500 lines | 1 person-month |
| Catala (§5) | the compiler itself | — | ≈5 person-months |

**What these say about our unit.** "Minutes per article" is not a unit; an article ranges from a definition to a
provision with exceptions, cross-references, dates and external calculations. The usable units are **hours per
computational provision** and **lines per medium document**. Our measurement 1 is consistent with that scale: we
were fast because we encoded almost nothing.

## Measurement 1 — GDPR Art. 17, the right to erasure

**What was done.** Fetched the article, saved it as a pinned corpus file, computed its sha256, split the text
into Hohfeld positions, quoted a span for each, wrote the statement, ran `lexcheck` twice.

**Result.** `CHECKED`, coverage 0.750 (3 of 4 atoms closed), 4 of 4 anchored, 0 refusals, 2 escapes.

**How the nine minutes went.** Roughly a third of it was spent on spans that failed for a reason no theory
predicted: **the source file wraps at about 100 characters, and three of my five candidate quotes crossed a
line break**, so the byte-exact substring did not exist. A human quoting a sentence from a wrapped official text
will hit this every time. That is not a bug in the checker — the checker was right — but it is a defect in the
*experience*, and the refusal message should say what happened: current detail is "span does not occur", and the
useful message is "span does not occur in this file; it crosses a line break at offset N; quote the raw bytes".

**Three findings, and the third is the expensive one:**

1. **Anchoring works and is cheap.** Pinning by sha256 plus a unique span took no meaningful time once the
   corpus was saved. This part of the design is confirmed by use, not by argument.

2. **Corpus pinning is asymmetric between jurisdictions.** `eur-lex.europa.eu` answered **HTTP 202 with an empty
   body** to this client, so the official text could not be fetched and a mirror was used (the file says so in
   its own header and forbids citing it as law). Meanwhile the US **eCFR API returned dated, machine-readable
   content versions** on the first try (`/api/versioner/v1/versions/title-26.json`, 268 KB of version records).
   So the answer to Q2 is not one answer: for US federal regulation, a pinned official revision is an API call;
   for EU acts, as of today and from here, it is not.

3. **The carve-out is where the model breaks, in the first real article.** Art. 17(3) — "Paragraphs 1 and 2
   shall not apply to the extent that processing is necessary..." — is not a position; it is a *defeat*. v0.1
   has no such construct, so the atom was recorded as an ordinary `privilege` with an escape that says exactly
   that. The cost is not the escape: it is that **3 of 4 atoms are closed while the article's operative
   exceptions are not modelled**, so the coverage number is honest and the encoding is not usable as an
   account of the article. H9 said defert defeasibility; this measures what deferring costs — 25 % of the
   article and the whole of its defeating structure.

**An unforced choice worth flagging.** The four terms (`data subject`, `controller`, `personal data`, `erasure`)
are defined by Art. 4 of the same Regulation, which is outside this corpus. Rather than leave them open —
which would drop coverage to 0 — they were closed with paraphrases written by the encoder. That is an
assertion nobody anchored, and the checker has no way to see it. It is the most concrete instance yet of the
gap H4 and H5 describe: **terms are the unanchored part of the model.**

## What the next measurement must change

1. Quote spans by copying **raw bytes** from the saved corpus, never a reflowed sentence; and record how many
   attempts a span took — that is the number that measures the anchoring UX.
2. Encode a clause whose difficulty is *structural* rather than *open-textured*, to separate "hard because law
   is vague" from "hard because our model is thin". Art. 17 was the second kind.
3. Time a second encoder on the same clause independently, because a single encoder's minutes measure the
   tool's friction with that encoder, not the cost of encoding.
