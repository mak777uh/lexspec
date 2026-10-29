# 28 — A classifier for the surface layer: what it can do, in what order, and what blocks it

Owner's suggestion: later, train a classifier (or pull the smallest adequate one from HuggingFace) for our task.
This note fixes *which* task, orders the candidates cheapest-first, and states the gates — because "train a
classifier on legal text" is not a task, and a model that guesses well is exactly what this repository is built to
distrust.

---

## §1 Where it sits, and what it may never do

Layer **L1 (surface)**: turning a sentence into *candidate* positions. The classifier's output is a **candidate**,
never a verdict — the proposer is not the acceptor ([`docs/06`](06-FROM-TEXT-TO-PROOF.md) H13, charter C1). Every
candidate enters the pipeline in the same state as a model-written proposal: unanchored, unclosed, and invisible in
the verdict until it passes `S2_*` and closure like anything else.

So a classifier cannot make the product less honest. It can only make encoding cheaper — and that is the only
reason to build one.

---

## §2 Three possible tasks, ranked by our measured bottleneck

| Task | Input → output | Where it helps | Verdict |
|---|---|---|---|
| **T3 anchor ranking** | an atom's action/terms → the span in the pinned corpus that most likely supports it | the dominant cost in both measurements: finding the span. `span_hint` made a *found* quote usable, but finding it is still human work | **highest value** |
| **T2 atom segmentation** | a paragraph → the boundaries of normative units | medium: reduces the "one sentence, two positions" error, which our method doc calls the most common split mistake | medium |
| **T1 modality/position classification** | a span → one of the eight Hohfeld positions, or "no position" | low: a careful encoder with a checklist does this in seconds, and a wrong label is invisible in the report (no code catches a misclassification) | **lowest** — and the riskiest, because it fails silently |

Ranking T3 first is not taste: it is what the two measurements show. 43 % of span attempts failed on formatting,
and the remaining time went to *locating* the right sentence, not to deciding whether it creates a duty.

---

## §3 The ladder, cheapest first

1. **Rule and lexicon baseline (no dependencies).** Modality markers in Russian and English (`обязан`, `должен`,
   `вправе`, `не вправе`, `не допускается`, `подлежит`, `may`, `shall`, `must not`), plus the article/paragraph
   structure already in the corpus. This catches most T1 and segments T2 crudely. **Cost: hours. Risk: none.**
2. **TF-IDF + linear model (scikit-learn from PyPI).** Feasible today: PyPI answers 200, and the install is ~30 MB.
   Useful for T3 candidate ranking once there are labels to rank against.
3. **A small encoder (transformers/torch).** Blocked today, for two independent reasons: no `torch`/`transformers`
   installed, and **HuggingFace weight downloads do not work from this network** — `resolve/main/*.bin` redirects
   (302) to `cdn-lfs.huggingface.co`, which does not answer (000), and the xet bridge returns 403. Config files and
   the API answer 200; weights do not.
   Candidates when it unblocks, smallest first: `cointegrated/rubert-tiny2` (~29 M parameters, Russian),
   a multilingual MiniLM (~33 M usable layers), `LaBSE` (~118 M) only if the smaller two underfit.

**The order is not a preference, it is an obligation.** Charter C6 requires every mechanism to name its source or
its gap; a transformer whose gap is "we have 16 labelled atoms" has no gap worth the cost.

---

## §4 Gates — what must be true before any supervised training

| Gate | Condition | Why |
|---|---|---|
| **G1** | ≥ **200 closed atoms** with human-confirmed spans, across ≥ 2 jurisdictions | below this, a fine-tune memorises our three corpora; the whole point is transfer to a clause we have not seen |
| **G2** | the rule baseline's cost per closed atom is measured | if rules already reach the same minutes-per-atom, a model adds maintenance and removes explainability for nothing |
| **G3** | a **held-out provision** exists that no encoder has seen | otherwise the metric is a memory test, not a check |

Today: 16 atoms, one jurisdiction pair, no held-out provision. **G1 is not close.** The honest path to it is the
audit mode ([`docs/18`](18-CLOSED-LOOP.md) §4): every real finding adds a labelled atom.

---

## §5 The metric that decides, and it is not accuracy

A classifier is worth its maintenance only if it moves **minutes per closed atom**, and its errors must be
*visible*. Concretely:

| Metric | Target | Why this one |
|---|---|---|
| **anchor hit@3** | the correct span appears in the model's top 3 candidates | the human then confirms instead of searching — that is where the minutes are |
| **silent-error rate** | a wrong candidate must never produce a `CHECKED_ANCHORED` | guaranteed by architecture: a wrong span fails `S2_*`, so the classifier cannot smuggle an error past the checker |
| minutes per closed atom, before vs after | −30 % or better | below that, the model is a hobby |

Note what the architecture already guarantees: because every candidate must be anchored and closed, a classifier
error cannot become a false verdict — it can only waste a reviewer's minute. That is the property that makes a
classifier safe here at all, and it is worth stating before anyone proposes the opposite.

---

## §6 What would make this whole note obsolete

- If `span_hint` plus a better corpus layout (normalised, unwrapped, indexed) brings span search under a minute,
  T3 has nothing to sell and the classifier is unjustified.
- If the audit mode turns out to need *interpretation* rather than *retrieval*, no classifier helps: the task is
  judgement, and judgement is the human link we refuse to model.
- If the small-model download stays blocked and the rule baseline scales linearly with corpus size, we stay with
  rules and say so.
