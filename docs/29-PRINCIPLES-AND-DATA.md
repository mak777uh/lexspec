# 29 — Principles, experiments, and the dataset they leave behind

The owner's priority, restated because it changes the order of work: **find principles and test them with
experiments, and keep every experiment as a dataset for later.** A classifier is a possible consumer of that
dataset, not a reason to build one ([`docs/28`](28-CLASSIFIER-LADDER.md) is demoted to an appendix of this idea).

A principle here is a **regularity with a measurement behind it**, stated so that an experiment can refute it.
Anything vaguer is a slogan with a decimal point.

---

## §1 The record

Every encoding attempt is one row in [`lab/experiments.jsonl`](../lab/experiments.jsonl), append-only, written by
`python lab/experiment.py add …` from the statement itself: the tool runs the checker, reads coverage, counts and
codes from its report, and hashes both the statement and its corpus. The human adds only what a tool cannot know: how
long it took, how many anchor attempts failed and why, and which principle the row speaks to.

```
id · date · provision{id, jurisdiction, kind, article} · corpus{file, sha256}
statement{file, sha256, atoms, closed, anchored, coverage, verdict} · codes[]
unclosed[{atom, code, detail}] · anchoring{attempts, failures, cause}
timing{minutes_to_first_verdict, minutes_to_pass, by} · principles_touched[] · note
```

A correction is a new row with `corrects: E-XXXX` — the old row is never edited. Three rows exist already:

| id | provision | atoms | closed | coverage | minutes | what it cost |
|---|---|---|---|---|---|---|
| E-0001 | GDPR Art. 17 | 4 | 3 | 0.750 | 9 | a carve-out the model cannot express |
| E-0002 | ГК 395 | 6 | 3 | 0.500 | 14 | a rate by reference, a defeat, a bounded power |
| E-0003 | ЗоЗПП 26.1(4) | 4 | 1 | 0.250 | 11 | one open-textured central term |

---

## §2 The principles under test

Each is stated as a claim, with the metric that measures it and the experiment that would settle it. Current
evidence is marked **weak** (three rows) or **none** — nothing here is a finding yet.

**P1 — Cost scales with the number of distinct quantities, dates and actors in a provision, not with its length.**
*Metric:* minutes per closed atom against the count of numeric/date tokens.
*Evidence:* **weak** — 395 (six atoms, three quantities, 14 min) versus 26.1 (four atoms, three deadlines, 11 min)
versus Art. 17 (four atoms, no quantities, 9 min).
*Settles when:* five provisions of comparable length and different quantity density give a monotone relation.
*Refuted by:* a long, quantity-free provision that costs more than a short computational one.

**P2 — Coverage is predicted by the number of open-textured terms, and almost nothing else.**
*Metric:* coverage against the count of `status: "open"` terms plus terms closed by paraphrase.
*Evidence:* **weak but pointed** — 26.1's coverage 0.250 comes from one term («товар надлежащего качества») that the
provision turns on; Art. 17 reaches 0.750 only because four terms were closed by paraphrase, which is itself an
unanchored assertion.
*Settles when:* ten provisions show the correlation, and a provision with no open terms but low coverage appears
(refuting the principle) or fails to appear.
*Refuted by:* a fully closed vocabulary with coverage below 0.5 for reasons other than defeat.

**P3 — A provision that grants and then restricts needs defeat; without it, coverage caps near 0.75.**
*Metric:* fraction of provisions containing a restriction after a grant; coverage before and after a defeat construct
exists.
*Evidence:* **weak** — 17(3) and 395 п. 4 are both of this shape, and both are exactly the unclosed atoms.
*Settles when:* [`docs/13`](13-DEFEASIBILITY-CHOICE.md)'s five scenarios are implemented and the same provisions
re-cross 0.75.

**P4 — Anchoring failures are a formatting phenomenon, not an ambiguity phenomenon.**
*Metric:* span attempts, failures, and the cause distribution.
*Evidence:* **strong for our own procedure** — 6 of 14 attempts failed across two provisions, all on line wrapping;
`span_hint` recovered all six afterwards ([`docs/21`](21-IMPACT-PLAN.md) §7).
*This one is already settled for wrapped text;* the open half is whether *genuine* ambiguity occurs in real corpora
and at what rate — a sample of 200 random spans would answer it.

**P5 — A provision whose numbers come from an external pinned series cannot exceed `CHECKED` before the quantity
layer, and reaches `CHECKED_ANCHORED` by declaration alone after it.**
*Metric:* coverage and verdict before/after L5 on the same provision.
*Evidence:* **none yet** — this is precisely stage 2's acceptance test ([`docs/27`](27-QUANTITY-LAYER.md) §6), and it
is written here so that a failure is recorded rather than explained away.

**P6 — The number of anchors per atom is one; an atom needing several spans signals a wrong split.**
*Metric:* anchors per atom, and whether splitting the atom resolves it.
*Evidence:* **none.** Cheap to test: re-split the 14 atoms recorded so far and see whether any wants two spans.

---

## §3 What the dataset is for, and what it is not

It is **the artifact that survives every other decision**. If the encoding approach is abandoned, the rows still
describe what real provisions cost to formalise, which is useful to anyone. If it is continued, the rows are the
only honest basis for generalisation — and, yes, the training set a classifier would need
([`docs/28`](28-CLASSIFIER-LADDER.md) G1 asks for 200 closed atoms; the register is how they accumulate).

It is **not** evidence of anything until it is big enough, and it must never be summarised as "our measurements
show" while it holds three rows. The threshold written into the plan: **no generalisation claim before 20
provisions**, and every such claim must name the rows it rests on.

---

## §4 What to do next, in order

1. **Add a row for every encoding from now on**, including failed ones — a failure row is the most valuable kind,
   because it is the only record of a principle being wrong.
2. **P4's second half**: sample 200 random spans from the corpora and count genuine ambiguities. An hour of work,
   and it converts a suspicion into a number.
3. **P5 when stage 2 lands**: the same provision before and after, in two rows, with `corrects` if the first was
   misjudged.
4. **P6's cheap test** on the 14 existing atoms.
5. Only after ~20 provisions: look for the correlation P1 and P2 claim, and write down whichever way it comes out.
