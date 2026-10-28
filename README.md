# LexSpec

**What it is.** A specification, a schema and a reference checker for *legal statements that software can
check*: a clause is written as a set of Hohfeldian positions, each anchored to an exact span of a pinned
revision of a legal text, and a program decides whether the set is internally coherent, fully anchored, and
how much of it was actually closed.

**What it is not.** Not an AI that reads contracts and tells you they are fine. Not legal advice. Not a
theorem prover, not a statute parser, and not a claim that a clause passing the checker is lawful. The
checker never outputs the word "legal"; it outputs a verdict over a triple `(statement, encoding,
corpus@revision)` and a list of the things it did not check.

Russian mirror: [README.ru.md](README.ru.md). This file is canonical; where they disagree, this one wins.

## The one rule

> **Anchor or refuse.** An atom without an unambiguous span in a pinned text revision is not a weak claim —
> it is a different product. A phrase that occurs twice in the text does not anchor anything, because the
> citation can silently re-point after an amendment (`S2_SPAN_AMBIGUOUS`).

Everything else in the repository follows from accepting that rule, including the parts where the tool
refuses work it could have done.

## Why the four layers are kept apart

"Formalise legal language" is four problems, and collapsing them is how the field produces confident
nonsense:

| Layer | Question | What this repo has |
|---|---|---|
| **L1 Surface** | what does the sentence say, exactly? | nothing: v0.1 does not parse prose. A human or a model proposes a statement, and the proposal is falsifiable |
| **L2 Model** | which legal position is this? | Hohfeld's eight positions as a closed set, with correlatives and opposites ([spec §4](docs/10-SPEC-v0.1.md)) |
| **L3 Inference** | what follows, what conflicts? | combinational checks only: opposites, time overlap, declared conflict policy. No entailment |
| **L4 Provenance** | which bytes, at which revision, say so? | every atom anchored by span + sha256 of the corpus file ([spec §5](docs/10-SPEC-v0.1.md)) |

The interesting consequence is in L2/L3: because the positions form two squares with known opposites,
contradictions between them are **combinatorial**, so a few hundred lines of Python find them without a
prover. "A may not do X" written next to "A may do X" in the same document is not a subtle semantic problem.

## Run it

```bash
python tools/lexcheck.py examples/01-delivery-ok.lex.json          # human output
python tools/lexcheck.py examples/01-delivery-ok.lex.json --json   # machine report
python tools/lexcheck.py --canonical examples/01-delivery-ok.lex.json  # canonical form + sha256
python tests/run_tests.py                                          # the guard suite
python tools/lexspec_status.py                                     # the numbers quoted below
```

Python 3.11+, standard library only. Nothing to install.

Exit codes: `0` the statement passed, `1` refused, `2` usage or parse error.

## Verdicts

Exactly three, in ascending strength. The wording is part of the contract:

| Verdict | Means |
|---|---|
| `REFUSED` | the statement does not survive checking; every reason carries a code from a closed vocabulary |
| `CHECKED` | what is encoded is coherent and anchored where anchored, but at least one atom is open or coverage is below threshold |
| `CHECKED_ANCHORED` | every atom is closed and anchored; this is still **not** a statement about law |

Every report carries, verbatim:

```json
"not_claimed": ["legal validity",
                "completeness of the encoded law",
                "correctness of the corpus outside the pinned revision"]
```

A verdict quoted without that list is a different claim than the one the tool made. The full catalogue of
refusals — what each code means, and what a reader should do — is
[docs/11-REFUSAL-CODES.md](docs/11-REFUSAL-CODES.md).

## Read first

| File | Role |
|---|---|
| [docs/00-CHARTER.md](docs/00-CHARTER.md) | why this exists, what we refuse to build, and five falsifiers that could prove it wrong |
| [docs/10-SPEC-v0.1.md](docs/10-SPEC-v0.1.md) | **the constitution**: the document model, canonical form, Hohfeld layer, anchoring, time, conflicts, coverage, verdicts, conformance |
| [docs/11-REFUSAL-CODES.md](docs/11-REFUSAL-CODES.md) | closed vocabulary of ways a statement is wrong, with the remedy for each |
| [docs/20-METHOD.md](docs/20-METHOD.md) | how a paragraph of law becomes a checked statement, and what it costs in minutes |
| [docs/02-DESIGN-SPACE.md](docs/02-DESIGN-SPACE.md) | prior art: Catala, L4, LegalRuleML, Akoma Ntoso, deontic logic, proof assistants, LLM legal checking — what we borrow and what we refuse |
| [docs/04-SEMANTIC-VS-FORMAL.md](docs/04-SEMANTIC-VS-FORMAL.md) | when a machine-checked proof pays and when it is money wasted: CompCert, seL4, Cedar, TLA+, PBT, policy engines, and the PutnamBench incident where two formalised statements were wrong |
| [docs/05-HARNESS-LESSONS.md](docs/05-HARNESS-LESSONS.md) | what a published 672/672 proof run teaches a checker: the harness owns the stopping rule, identity is checked on the elaborated form, cost is recorded per attempt — failures included |
| [docs/06-FROM-TEXT-TO-PROOF.md](docs/06-FROM-TEXT-TO-PROOF.md) | **the research program**: twenty numbered hypotheses on turning legal text into a proof obligation, each with the test that would kill it — and why the provable target is the checker, not the clause |
| [docs/07-ROUND-01-QUESTIONS.md](docs/07-ROUND-01-QUESTIONS.md) | sixteen questions we could not answer from inside, for external models and practitioners — anchoring, Hohfeld for civil law, whether the soundness theorem is trivial, measured encoding cost, evidence admissibility |
| [docs/09-IMPLEMENTATION-LANGUAGE.md](docs/09-IMPLEMENTATION-LANGUAGE.md) | the language choice on evidence: twelve requirements derived from the spec, four candidates, the seven byte-level traps, and the Lean 4 bridge — Rust primary, Python twin ([ADR-0002](lab/decisions/ADR-0002-implementation-language.md)) |
| [docs/12-LANDSCAPE-REGISTER.md](docs/12-LANDSCAPE-REGISTER.md) | four search passes merged: 53 distinct approaches, graded by our own re-check, with the defects found — including one fabricated repository and our own schema defect |
| [docs/13-DEFEASIBILITY-CHOICE.md](docs/13-DEFEASIBILITY-CHOICE.md) | the blocking sub-problem: carve-outs. Five requirements as tests, seven candidate mechanisms with where each stops, and the five scenarios that settle the choice |
| [docs/14-ARCHITECTURE.md](docs/14-ARCHITECTURE.md) | **the chain**: law text → positions → quantities and flows → compiled rule → enforced decision → evidence walkable back to a span. Says what "reliably protected" can honestly mean, and what it cannot |
| [docs/19-PORTFOLIO.md](docs/19-PORTFOLIO.md) | **the portfolio as one system**: five repositories, the edges between them, which are built and which are not — and what "bridge between law and code" means as two conversions rather than a metaphor |
| [docs/18-CLOSED-LOOP.md](docs/18-CLOSED-LOOP.md) | **the thesis made checkable**: three objects — text, statement, code — and three pairwise checks; what "sharper" means in four numbers; the stopping rule that makes "ever sharper" falsifiable; and which pair is not checked yet |
| [docs/17-ROUND-02-QUESTIONS.md](docs/17-ROUND-02-QUESTIONS.md) | eight questions that attack the three decisions just made — computational-first, the transition layer, the certificate — asked for witnesses and artefacts rather than literature |
| [docs/16-ROUND-01-ANSWERS.md](docs/16-ROUND-01-ANSWERS.md) | four answers to round 01, merged: the verified cost measurement from Catala, why the first corpus becomes computational provisions, and the six things that changed in the spec |
| [docs/15-SUBSTRATE-INDEPENDENCE.md](docs/15-SUBSTRATE-INDEPENDENCE.md) | the optional outward layer, as a **resilience** requirement: at least two substrates able to produce and record the same decision, a handover protocol with proof, the anchored legal basis a switch needs, degraded modes, and the drill that makes the fallback real |
| [AGENTS.md](AGENTS.md) | the twelve rules for anyone, human or agent, who changes this repository |
| [schemas/statement-0.1.json](schemas/statement-0.1.json) | the schema, with the closed sets in one place |
| [examples/](examples/) | three statements: one that passes, one with opposite positions, one with a broken anchor |

## Repository map

| Group | Path |
|---|---|
| Constitution | `docs/10-SPEC-v0.1.md` · `docs/11-REFUSAL-CODES.md` |
| Why and how | `docs/00-CHARTER.md` · `docs/20-METHOD.md` · `docs/02-DESIGN-SPACE.md` |
| Machine | `schemas/` · `tools/lexcheck.py` · `tools/lexspec_status.py` |
| Evidence | `examples/` · `tests/` · `corpus/` · `tools/SELFTEST.md` |
| Process | [lab/sources.md](lab/sources.md) — source intake register · [lab/decisions/](lab/decisions/) — decisions; ADR-0001 explains why we are gathering sources before building |
| Interop | [interop/](interop/) — the note channel with [flowguard-spec](https://github.com/mak777uh/flowguard-spec); messages are append-only and pinned to commits |
| Guards | `lab/check-secrets.py` · `.github/workflows/guards.yml` |

## What this repository does not claim

- **No legal validity.** A verdict is about an encoding, never about law.
- **No completeness.** Coverage is a fraction of *the statement*; 100 % coverage of a mis-encoded clause is
  100 % coverage of a mis-encoding.
- **No statute parsing.** Nothing here reads legal prose. The corpus is a pinned excerpt, and its header
  says so.
- **No entailment.** "The law requires X" is never an output. "Atom `a1` is anchored at ——— in this revision"
  is.
- **No stability promise.** v0.1 is a draft; codes and fields may change, and the report always names the
  spec version it was checked against.

## Where this fits among the owner's projects

| Project | Shared discipline | Different subject |
|---|---|---|
| [flowguard-spec](https://github.com/mak777uh/flowguard-spec) | declare a boundary, then prove things only inside it; refusal codes; claim registry | value flow through a database control point |
| [VecDHT](https://github.com/mak777uh/VecDHT) | canonical byte form is the contract between implementations | a peer-to-peer index |
| [mak777uh/-](https://github.com/mak777uh/-) | every number carries the command that produced it | a morphogenesis bench |
| [cases](https://github.com/mak777uh/cases) | "not confirmed" is published as a result | verification case files |

The rule that transfers: **an artifact a stranger cannot re-check is a claim, and claims are not results.**

## Status

v0.1. The checker, schema, examples and tests exist and run; the numbers in this section are produced by
`python tools/lexspec_status.py` and the guard suite is in `tools/SELFTEST.md` with the commands and their
real output. What does not exist is listed in [spec §11](docs/10-SPEC-v0.1.md) — in short: no entailment, no
defeasibility, no cross-statement reasoning, no jurisdiction semantics, no signed certificate.

## License

Documents — CC BY 4.0 ([LICENSE](LICENSE)). Code — Apache-2.0. Legal texts under `corpus/` are official
documents of state bodies; under Art. 1259(6) of the Russian Civil Code they are not objects of copyright,
and each file states its source and revision in its own header.
