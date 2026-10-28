# 18 — The closed loop: text, statement, code, and the divergence that tightens them

Status: **thesis and gap analysis**, not spec. The owner's formulation, made checkable.

> «Наша замкнутая система позволяет проверять код, юридический язык и их соответствие друг другу и делать их
> все более чёткими и математически ясными.»

Written because "closed" is a claim, and a claim is only worth something if you can say what would break it. This
document says what the loop is, what checks each pair, and — honestly — which pairs are not checked yet.

---

## §1 Three objects, three pairwise checks

There are not two things to compare but three, and closure means **every pair is checked**, not that a diagram
has a circle in it.

```
                    ┌──────────────────────────────┐
     legal text ────┤ 1  anchoring + coverage      ├──── statement
     (pinned)       │    S2_*, coverage, escapes   │     (positions,
                    └──────────────────────────────┘      quantities, defeat)
                            │                                   │
                            │                                   │
                    ┌───────┴───────────────────────────────────┴──────┐
                    │ 3  end-to-end: decision → rule → atom → span     │
                    │    decision record, certificate                  │
                    └───────┬──────────────────────────────────────────┘
                            │                                   │
                    ┌───────┴───────────────────────────────────┴──────┐
                    │ 2  compilation fidelity + twin evaluation        │
                    │    atom id carried; engine artifact regenerable  │
                    └──────────────────────────────────────────────────┘
                            │                                   │
                           code  ───────────────────────────────┘
                        (rules, engine, decisions)
```

| Pair | The question | What checks it today | Status |
|---|---|---|---|
| **1. text ↔ statement** | does this position point at one place in this revision, and how much of the statement is closed? | `S2_*`, coverage, declared escapes | **built** (v0.1) |
| **2. statement ↔ code** | does the running artifact compute what the statement says — no more, no less? | compilation carrying `atom id` + anchor hash; twin evaluation of two implementations on a fixed corpus | **planned** (docs/14 §4, ADR-0002) |
| **3. code ↔ text** | given a decision, can a stranger walk back to the bytes that authorised it? | decision record (rule, atom, anchor hash, revision, versions) + certificate | **planned** (H12, docs/14 §4) |

**A system with pair 1 only is open** — it checks the paper against the paper. That is what this repository is
today, and saying so is the point of this section.

---

## §2 What "sharper" means, in numbers

"Ever sharper" is a slogan until it has a measure and a stopping rule. Four numbers, all already computable or
specified:

1. **Coverage** — fraction of atoms closed. Rises as terms, quantities and defeat are modelled.
2. **Escape rate** — unclosed atoms per statement, with the reason. Should *fall for a given clause* as layers
   arrive, and should *never silently fall* — an escape that disappears without the model changing is a bug.
3. **Divergence count** — cases where the compiled artifact and the encoding disagree, measured on a generated
   case set. Should be zero on the declared fragment; a non-zero divergence is the single most valuable finding
   the system can produce, because it means the code and the law were never the same thing.
4. **Rounds to stability** — how many tighten-and-recheck cycles a clause needs before coverage stops improving.

The loop is: **measure → tighten the encoding or the code → re-measure.** Sharper means: coverage up, escapes down
and declared, divergence zero, rounds to stability finite.

---

## §3 The stopping rule (without it, "ever" is a promise nobody can check)

A claim of endless sharpening cannot be falsified, so it cannot be a claim. The loop stops for a clause when all
three hold:

- coverage ≥ the declared threshold for the strength of verdict wanted;
- divergence on the declared fragment is zero;
- the residue is written down as escapes with reasons.

**The residue is the product, not the failure.** A clause that ends at coverage 0.50 with three named escapes is
a finished result: it says exactly which parts of the law this system can decide and which it hands to a human.
A clause that ends at 0.99 with one undeclared escape is a worse artifact, because the missing part is invisible —
which is the failure this whole project was built to detect.

---

## §4 What is missing, stated as work rather than as vision

| Missing | Why it matters | Where it lands |
|---|---|---|
| **An audit mode for code that already exists** | most code was written before any statement existed; today we can only check statements we wrote ourselves | a new capability: given repository + policy artifacts, produce *candidate* atoms with evidence and mark what has no legal anchor at all |
| **Divergence detection between artifact and encoding** | pair 2 is planned but unbuilt, and it is the pair that finds real defects | generated case sets + twin evaluation; the Vernie & Grabmair method is the reference |
| **A term-level anchor** | terms are the unanchored part of the model (measured: GDPR Art. 17 closed four terms with paraphrases nobody anchored) | `term.anchor` — a definition must point at the span that defines it |
| **A residue report a lawyer can act on** | escapes are currently technical strings | a per-clause sheet: what is modelled, what is not, and who must decide |

The audit mode is the one that changes the product's market: it lets the system say something about the code that
already runs, instead of only about encodings it authored itself.

---

## §5 The claim this thesis permits

> For a declared corpus, a declared encoding and a declared engine, every decision the boundary makes can be
> walked back to the exact bytes that authorised it; where that walk fails, the failure is named as a defect in
> one of the three objects — text, statement, or code — rather than absorbed.

That is what "closed" can honestly mean. It does not mean the loop proves the law; it means the loop never lets a
gap go unnamed. And it makes the three objects commensurable in one currency: **a reference that either resolves
or is refused.**

---

## §6 What would falsify the thesis

1. If pair 2 cannot be checked without rewriting the code under audit, the audit mode is not an audit; it is a
   migration, and the thesis weakens to "we can check code we wrote".
2. If divergence between two correct-looking encodings is common *and* undecidable from the declared fragment,
   then "make it clearer" converges to a residue that is too large to be useful — measurable as rounds to
   stability never terminating.
3. If a lawyer cannot act on the residue report, the closure is technical only, and the product is a linter for
   people who already agree with it.
