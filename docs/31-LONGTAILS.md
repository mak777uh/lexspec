# 31 — LongTails: what a formally verified research loop teaches a legal checker

| | |
|---|---|
| source | [`k3nfalt/longtails`](https://github.com/k3nfalt/longtails), Apache-2.0, Lean 4, created 2026-10-14 |
| read on | 2026-10-30, from the repository itself (README, `run_comparator.py`, `AGENTS.md`) |
| status | study, three adoptions, one boundary |
| what it is | a Lean 4 framework where agents propose optimisation results and a machine checks both the theorem and its oracle-complexity budget against a formal **Setup** |

The owner sent it as "maybe useful". It is useful, and the reason is uncomfortable: it is the closest working
example of the architecture this repository claims to build, in a domain where the last step is checkable.

---

## §1 What they actually built

A **Setup** is one Lean structure that fixes everything a result may assume:

```lean4
abbrev spec : Setup where
  Params := Params          -- what the user supplies
  Public := Public
  Instance p := p.E → ℝ     -- the object under study
  Query p  := p.E           -- what the oracle asks
  Reply p  := p.E           -- what it answers
  Output p := p.E
  valid q := 0 < q.L ∧ 0 ≤ q.R ∧ 0 < q.ε
  admissible q f oracle := ConvexOn ℝ Set.univ f ∧ … ∧ (∃ xstar, IsMinOn f Set.univ xstar ∧ ‖q.x0 - xstar‖ ≤ q.R)
  successful q f output P := ∃ xstar, IsMinOn f Set.univ xstar ∧ ∀ᵐ ω ∂P, f (output ω) - f xstar ≤ q.ε
```

A result is `theorem result : Convergence spec budget`, where `budget` is an **explicit formula** in the setup
parameters. Because the theorem is *parameterised by* `spec`, a proof that silently assumed more would not typecheck
against the declared setup — the contract is not documentation, it is the type.

The audit is a separate program (`run_comparator.py`, wrapping `leanprover/comparator`): it extracts the declared
budget, regenerates a challenge from the setup, and requires the proof to use only `propext`, `Classical.choice`,
`Quot.sound` — **no `sorry`, no added axioms**. Agents (Codex, Claude Code) do the search; the machine disposes.

Reported state at 2026-10-30: 132 setups with proved bounds, 145 novelty reviews, 84 merged agent branches, and one
example where an agent improved a published bound from `L₁R` to `(L₁R)^{2/3}` while removing a `(1+ν)` factor.

---

## §2 The part that transfers exactly

| LongTails | This repository | verdict |
|---|---|---|
| `Setup` — one structure fixing assumptions and target | `statement` — atoms, anchors, escapes, verdict rules (spec §2–§9) | **same idea**, and ours is weaker: our contract is prose plus a schema, theirs is a type |
| `result : Convergence spec budget` | a report `(verdict, coverage, findings)` about `(statement, corpus@revision)` | same shape: the claim is about a declared contract, not about the world |
| `Comparator` — an independent program, not the author's checker | `tools/lexcheck.py` | **different**: theirs is built by other people and pinned; ours is ours |
| "no `sorry`, no added axioms" | declared `escapes[]`, `S2_*` refusals | principled difference, see §4 |
| novelty reviews: arXiv refs, search date, verdict, confidence | `docs/12-LANDSCAPE-REGISTER.md`, `[unverified]` marks | same move: machine-checked core, separately-judged novelty |
| agents propose, machine disposes | [`docs/06`](06-FROM-TEXT-TO-PROOF.md) H13, charter C1 | same rule, arrived at independently |

The structural lesson is one sentence: **the verifier must be able to say what the author did not say.** LongTails'
Comparator re-derives the budget from the Setup; it does not take the author's word that the budget is what the
theorem proves.

---

## §3 Adoption 1 — an independent second implementation (the one we owe anyway)

Their audit is a *second program* against the same contract. Our checker is a single program, and `ADR-0002` promised
a Python twin precisely so that substrate neutrality would be measured rather than asserted. LongTails shows the twin
is not a luxury: an audit written by the same hand that wrote the claim is an audit that shares its blind spots.

**Taken:** `tools/lexcheck_twin.py` — an independent implementation of the quantity arithmetic (integer rounding by
numerator arithmetic, not `Decimal.quantize`), which recomputes every segment and the total and compares them with the
checker's report. It is deliberately a *different algorithm* for the same semantics; agreement is evidence, and
disagreement is a finding.

## §4 Adoption 2 — an escape needs a defence, not a reason string

LongTails forbids `sorry` absolutely, because in mathematics an unproved step is no result at all. Law is not like
that: a term may be genuinely open-textured, and refusing to encode it is honest. But the discipline around the
refusal is transferable:

- their proof cannot grow an assumption without breaking the type;
- our escape can grow a reason string without breaking anything.

**Taken:** every escape must name the **layer** that could close it (`L2b` defeat, `L5` quantities, an open term
needing a definition with a basis) and, where a layer exists, the row in `lab/experiments.jsonl` that will close it.
An escape with no such pointer is a `sorry` with a comment.

## §5 Adoption 3 — a novelty verdict carries its search date and its confidence

Their review tables record, per prior work: arXiv link, **date of search**, verdict, and confidence. Our landscape
register records approach, source, grade — but a grade without the date it was assigned rots silently, which is the
same defect as a stale digest.

**Taken:** every row in the landscape register and every `[unverified]` mark carries the date it was last searched.

---

## §6 The boundary — and it is the same boundary we already named

LongTails closes the loop because **mathematical truth has a verifier**: a Lean term either typechecks or it does not.
The problem they did *not* solve is novelty — and they say so, putting it in a separate table judged by humans and
models with an explicit confidence.

Our loop has the same shape one level down: the machine checks **anchoring, coherence, arithmetic**; it cannot check
**whether the atom set captures the norm** — that is our P7, and it is the analogue of their novelty question. Their
paper-level claim ("the verified proof stopped being the bottleneck; novelty is disputed") maps exactly onto ours:
*the encoding stopped being the bottleneck; interpretation is disputed.*

So the honest summary of what LongTails gives us is not a technique but a **calibration**: a group of four
mathematicians, with a proof assistant, still had to leave the judgement step outside the machine and label it as
judgement. Anyone claiming a legal checker that closes the interpretation gap is claiming more than a Lean 4 team
claimed in a field where the gap is smaller.

---

## §7 What I did not take, and why

- **Agents as the primary producer.** Their loop is built for search over a formal space; ours has one legal system
  and no ground truth to search against. We cannot evaluate a candidate statement the way they evaluate a candidate
  bound.
- **Lean itself.** Encoding a statute in Lean would move the ambiguity into the formalisation and then verify the
  formalisation, which is the soundness-is-relative problem in [`docs/06`](06-FROM-TEXT-TO-PROOF.md) H3. It would look
  stronger and mean the same.
- **Their CI shape.** A full Mathlib build is hours; our guards must stay under a couple of minutes. Their nightly
  full audit is the pattern to copy if ours ever grows that expensive.
