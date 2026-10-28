# 21 — Impact plan: the order that moves the metric, not the document count

Written 2026-10-28, after two measurement rounds, one hand-run audit, and two rounds of external questions.

**What "impact" means here**, per charter C7: an edge in [`docs/19`](19-PORTFOLIO.md) §2 goes from *not built* to
*built and independently re-checkable*, or a class of our claims stops being opinion. Documents, hypotheses and
question rounds count for nothing on their own — we have written plenty already, and that is the failure mode
this plan exists to avoid.

**Effort figures are estimates** in working days for one agent working with the existing repo. None is measured.
The first thing each stage does is replace its own estimate with a number.

---

## §1 The plan in one table

| # | Stage | Artifact | Acceptance test | Est. | Kills |
|---|---|---|---|---|---|
| **0** | Settle the schema by adoption, not invention | `docs/21-ADOPTION.md` + one ADR | a field-by-field mapping of CAP-RRS §4/§5/§9 onto our statement; every remaining divergence has a named gap | 1 day | the risk of rewriting the schema after code exists |
| **1** | Make anchoring usable | `tools/span_hint.py` | every quote that failed on line wrapping in the 4 existing corpora is now resolved to its byte-exact span; minutes/atom measured before and after on one article | 1–2 days | the largest single source of encoding friction (**measured: 6 of 14 spans**) |
| **2** | Quantity layer (L5), minimal | spec §2 amendment + schema + tests + re-encoded ГК 395 | ГК 395 coverage 0.500 → ≥0.750 with the key-rate series pinned by digest; a second example with a cap over a period | 2–4 days | the whole computational class that ADR-0008 pivots to |
| **3** | Defeat (L2b), minimal, on Symboleo's vocabulary | spec + tests + re-encoded GDPR 17 | the five scenarios of [`docs/13`](13-DEFEASIBILITY-CHOICE.md) §5 reproduced exactly; GDPR 17 coverage 0.750 → 1.000 | 1–2 weeks | the second blocking gap: EU acts are unwritable without it |
| **4** | Code → law extraction, one finding class | `tools/audit.py` + `lab/audit` rerun | reproduces the three findings of the manual audit automatically, and the false-positive rate is measured on five unrelated policies | 1 week | the thesis "paper checking paper"; this is the edge nobody else has |
| **5** | Certificate v1: three layers + CAP-RRS decision fields | `tools/certify.py` + format doc | a stranger, holding only the repo and the certificate, reproduces the verdict and detects one mutated row; renewal stub and named responsible person present | 1 week | the gap between a report and evidence |
| **6** | Publish and re-check through the portfolio | interop note 2 + a resolved VecDHT/flowguard answer | one statement + certificate found by meaning and re-checked by a third party without our server | 1 week + their answers | the last unbuilt edge; also the only marketing we need |

**Sequence is not negotiable for 0 → 2.** Stage 0 decides the schema that 2 and 3 extend; building 2 first means
rewriting it in 3. Stages 4–6 are independent of each other and can interleave.

---

## §2 Why this order and not another

**0 first, because a schema change after code costs 10–30 units** (ADR-0002, ADR-0004). CAP-RRS already specifies
the record we were about to invent, and Symboleo already has the event vocabulary. Reading two documents for one
day is cheaper than any amount of rewriting.

**1 second, because it multiplies everything after it.** Every later stage is measured in "how long to encode one
real provision", and 43 % of candidate spans in our own measurements failed for a reason that is pure user
interface. Fixing that does not add a single guarantee — it makes the measurement of everything else meaningful.

**2 before 3, because quantities are cheaper and blocks more.** A computational provision needs numbers
immediately; defeat matters for the exceptions *inside* them. The measured evidence agrees: GDPR 17 lost its
defeat and stalled at 0.75; ГК 395 lost quantities and defeat and stalled at 0.50.

**4 before 5, because findings are worth more than formats.** A certificate around a checker that only checks
paper is a well-formatted nothing. The audit edge is what makes the loop closed, and it is also the part that
cannot be copied from CAP-RRS, Arxo or Symboleo — all three stop at the encoding, none starts from code that
already runs.

**6 last, because it is mostly waiting.** Two notes are out; the answers decide the shape. Doing it earlier means
designing against silence.

---

## §3 What this plan refuses, with reasons

| Refused | Why |
|---|---|
| **Lean 4 / proving the detector (H3)** | round 01, four of four: trivial unless the algebra is independent of the code. Not before an independently axiomatised algebra exists — and that is a research result, not a task |
| **A third jurisdiction** | ADR-0003: two systems or no claim. A third before the second has a measured cost is decoration |
| **General contract clauses** | ADR-0008: they need defeat, remedies and open texture, i.e. everything stages 2–4 have not built |
| **Reading more literature as a stage** | it happens inside stages as a prerequisite (0), never as a deliverable |
| **A bigger question round** | two rounds produced two corrections; a third before the code moves would produce paraphrases |
| **A product description, pricing, or a landing page** | there is no product until stage 4 produces a finding a stranger cannot produce by hand |

---

## §4 The one experiment that could kill the project, and it is cheap

**Find an authoritative recomputable oracle for one computational provision.** ADR-0008 addendum 2 requires it:
a provision enters the corpus only with a stable rule, anchored parameters and an oracle — an official calculator
or a published court judgment with principal, dates, rate periods and arithmetic.

We have one corpus and no oracle. If, after a week of looking, no such oracle exists for any computational
provision we can anchor, then the correctness half of the product has no ground truth, and the honest scope
shrinks to **anchoring + coherence + audit findings** — which is still useful, and much less than the plan above
assumes.

**Do this in parallel with stage 1, not after stage 5.** It costs a week and it decides whether stages 2–3 are
building a measurement instrument or a demo.

---

## §5 Kill criteria per stage

Written now so they are not invented later in a good mood:

- **Stage 1** — if `span_hint` does not resolve at least half of the previously failed quotes, the problem is not
  the tool but our corpus copying, and the fix belongs in the encoding procedure instead.
- **Stage 2** — if ГК 395 cannot exceed 0.750 coverage with a pinned rate series, the quantity layer is
  under-specified and must be redesigned before stage 3.
- **Stage 3** — if the five-scenario table of docs/13 cannot be reproduced, §3's proposal was wrong; adopt
  Symboleo's semantics wholesale instead of patching.
- **Stage 4** — if the false-positive rate on five unrelated policies exceeds 50 %, the audit mode is not viable
  as a product feature; keep the hand-run form and say so.
- **Stage 5** — if a stranger cannot reproduce a verdict from the certificate alone, the certificate is
  documentation, not evidence, and stage 6 must not start.

---

## §6 What "done" looks like at the end of this plan

Not a product. Three sentences true at once:

1. A real provision is encoded, with its parameters pinned, at a **measured** cost, and its residue is written
   down.
2. A running policy is compared against it, and the comparison produces findings a lawyer can act on — with a
   measured false-positive rate.
3. A stranger, given the repository and one certificate, reproduces the verdict and the finding without trusting
   us, and can find the whole thing by meaning through a network nobody owns.

That is the closed loop of [`docs/18`](18-CLOSED-LOOP.md) with numbers attached. Everything else is a way of
saying it.
