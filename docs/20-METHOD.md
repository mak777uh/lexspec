# Method — how a clause becomes a checked statement, and what it costs

This file is the working protocol. The spec says what a statement *is*; this says how a human or an agent
gets from a paragraph of law to a verdict, honestly, and how we measure whether the exercise was worth it.

## 1. The loop

```
read the clause
   → 1. split into atoms (legal positions, not sentences)
   → 2. choose the Hohfeld relation for each atom
   → 3. name terms; decide closed / open for each
   → 4. pin the corpus (revision + sha256)
   → 5. quote exact spans for every atom
   → 6. run lexcheck
   → 7. read the codes; fix the statement, never the checker
   → 8. record cost (minutes, codes hit, final coverage)
```

Step 7 is the one that degrades first under time pressure. The rule is in
[`AGENTS.md`](../AGENTS.md) §3: the gate is not weakened to make a test green.

## 2. Splitting a clause into atoms

A sentence is not an atom. One sentence of law routinely carries two or three positions. The test for a
correct split:

> For each atom, ask: *who* is in *which* position, with respect to *what action of whom*?

If two answers come back for one candidate atom, it is two atoms. Examples of the three common splits:

| Sentence shape | Atoms |
|---|---|
| "The supplier shall deliver the goods within the term of the contract." | `duty(supplier → buyer, deliver goods)` |
| "The buyer has the right to demand early delivery." | `right(buyer → supplier, demand early delivery)` |
| "The supplier may involve third parties in performance." | `privilege(supplier → buyer, involve third parties)` + the correlative `no-right(buyer → supplier, object to involvement)` |

The third row is the one people get wrong. A permission granted to A is a *removal* of a claim from B, and
the removal is itself a position. Encoding only the privilege loses the thing a dispute is actually about.

## 3. Choosing the relation

Order of questions, in this order, because the earlier ones are cheaper:

1. **Is someone required to do something?** `duty` (and the bearer of the correlative is a `right`).
2. **Is someone free to do something, where freedom was not the default?** `privilege`, plus the `no-right`
   of the counterparty.
3. **Is someone able to change the legal position of another?** `power` (correlative `liability`).
4. **Is someone protected from such a change?** `immunity` (correlative `disability`).

If none fits, the atom is outside v0.1. Say so, mark it `open`, and let coverage fall. Do **not** bend a
`duty` into a `power` to make the statement pass; a wrong relation is worse than an open term, because an
open term is visible in the report and a wrong relation is not.

## 4. Terms: closed or open

A term is `closed` when its `def` is specific enough that two readers would place the same facts inside it.
Practical test: write three borderline cases. If you cannot decide all three from the `def` alone, the term
is `open`.

Marking a term `open` is the honest move and it is not free: it lowers coverage. This is intended. The
alternative — a confident `def` that quietly includes or excludes the disputed case — is exactly the failure
mode this project exists to avoid.

## 5. Pinning the corpus

1. Take the text **from the official source**, at a stated revision.
2. Save it as a file under `corpus/`, named `<source>-<revision>.txt`.
3. Put `# SOURCE:`, `# REVISION:` and, where the text is an excerpt, `# NOTE:` in the header — inside the
   file, because the file's bytes are what the hash covers.
4. Compute `sha256` of the file's bytes and record it in `corpus[].text_sha256`.
5. Never edit a pinned file. A new revision is a new file with a new id and a new hash; the old one stays,
   because statements anchored to it must keep resolving.

A corpus is not "the law". It is the exact bytes a statement was checked against, and the report must make
that clear to someone who has never opened this repository.

## 6. Cost, measured

Every encoded clause gets a row in `lab/cost.md`:

| field | why |
|---|---|
| `clause` | stable identifier (source + article + revision) |
| `atoms` | how many positions were found |
| `open_terms` | how many terms could not be closed |
| `minutes_to_first_verdict` | wall clock, reading to first `lexcheck` run |
| `minutes_to_pass` | wall clock to `CHECKED_ANCHORED`, or `—` with the reason |
| `codes_hit` | every code the process produced, in order |
| `origin` | `human` or `model:<name>@<date>` |

The number that decides whether this project is worth continuing is **minutes per article**. Falsifier F3 in
the Charter says so. If the number is larger than the cost of a careful human checklist, the encoding
approach is not paying for itself and we say so in the open.

Corollary: a clause that takes an hour because the tooling is bad is a tooling defect, not a legal
difficulty. Log which one it was.

## 7. Model-assisted encoding

A model may propose a statement. That proposal is a hypothesis, and the repository treats it as one:

- `origin: model:<name>@<date>` in the cost row and in the statement's `lab/` record;
- the proposal is accepted only after `lexcheck` passes **and** a human or a second model confirms that each
  `anchor.span` actually supports its atom — the checker proves the span exists, never that the span says
  what the atom claims;
- a rejected proposal is kept, with the code that killed it. That is the most valuable artifact in this
  workflow, because it is a labelled example of the failure mode.

This is the boundary between LexSpec and every "AI reviews your contract" product: the model is allowed to
write proposals, and is never allowed to be the thing that decides.

## 8. Review of a statement by a second party

A reviewer who did not write the statement should be able to answer four questions from the report alone:

1. Which exact bytes was this checked against?
2. What was closed, and what was left open?
3. Which findings were raised, and what would each require?
4. What does the verdict **not** say?

If any of the four cannot be answered, the report — not the reviewer — is defective.

## 9. Cost of a wrong answer

Ranked by damage, which is the only ranking that matters here:

1. **A confident wrong verdict that a reader acts on.** Prevented by `not_claimed` being in every report and
   by the verdict ladder never reaching "legal".
2. **A silent reduction of coverage.** Prevented by `S4_UNDECLARED_ESCAPE`.
3. **A citation that re-points after an amendment.** Prevented by `S2_SPAN_AMBIGUOUS`.
4. **A refusal that a reader cannot act on.** Prevented only by keeping the code vocabulary small and by
   writing the catalogue for a reader, not for the author.

Everything else is a bug with a fix. These four are the ones that would end the project's usefulness.
