# 23 — The working loop: push, test, hit a wall, ask

The owner's operating instruction, written down so it does not have to be re-invented each session:

> push the truth as far as it goes, test it; when you hit a wall where the next step is unclear, we run a round
> of questions.

This document defines the three words in that sentence precisely, because a loop with vague terms turns into
"ask whenever it is hard".

---

## §1 The loop

```
push        advance the artifact that can be checked (a measurement, a guard, a spec paragraph that removes an
            ambiguity, an adopted mechanism). If it cannot be checked, it is not pushing.
test        prove the advance works: run the guard, run the tests, reproduce the number, mutate and see it fail.
wall        a point where the next advance needs a fact that is not in the repository and cannot be derived
            from it by work I can do alone.
round       a small set of questions, each tied to one wall, each naming what would settle it.
merge       answers land as rows in lab/sources.md and as dated amendments; nothing is edited silently.
```

The loop is not "ask when stuck". Most stuck-ness is not a wall: it is missing work. The distinction is §2.

## §2 What counts as a wall

A wall has all four properties. If one is missing, it is work, not a wall.

1. **The fact is external.** It lives in a court judgment, a publisher's endpoint, a specification's semantics, or
   someone's operational experience — not in our documents and not derivable by reading what we already have.
2. **I have tried to get it.** The round names what was attempted: which sources were opened, which failed, and
   how. A question without an attempt is laziness with a citation.
3. **It blocks a named next artifact.** "It would be interesting to know" is not blocking. "Stage 2 cannot be
   specified without it" is.
4. **An answer would change something written.** If no answer changes the spec, the guard or the plan, the
   question does not belong in a round.

## §3 What a question must contain

Every question carries five lines, and a round is rejected if any are missing:

```
WALL     what is blocked, and the artifact that cannot be written
TRIED    what I opened or ran, and how it failed
ASK      the question, answerable in one paragraph
SETTLES  what would count as an answer — a document, a judgment, a spec section, a dataset
MOOT     what would make the question unnecessary (so we can strike it rather than answer it)
```

**Witness bias.** Ask for a project, judgment, endpoint, dataset or specification section — never "what does the
literature say". Two rounds showed that the useful answers were all witnesses and the useless ones were
categories.

**No answer is a result.** Four "nobody has measured that" answers closed Q8 and Q11 properly. A round that
returns five negatives has done its job, provided the negatives are specific.

## §4 What the loop forbids

- **Asking before the repository has tried.** If the answer is in `docs/`, `lab/sources.md` or a primary source we
  already know how to open, it is not a wall.
- **Asking the same wall twice.** A repeat means the first answer was not read or the question was bad; fix the
  question, do not re-send it.
- **A round as a substitute for work.** Rounds are expensive for the reader; a round per day means the loop has
  become the product.
- **Accepting an answer without opening its source.** The merge grades every row; unopened rows are `-`, not
  `verified`.

## §5 Where the loop currently stands

| Stage | State | Wall? |
|---|---|---|
| 0 — adopt the field vocabulary | done ([`docs/22`](22-ADOPTION.md)) | no |
| spec consistency guard | done, self-tested, in CI | no |
| 1 — `span_hint` | not started | **no wall**: it is work, and the failure data already exists |
| 2 — quantity layer | specified in outline only | **wall**: the day-count and rounding convention for statutory interest in Russian practice — see round 03, W1 |
| 3 — defeat | proposal in [`docs/13`](13-DEFEASIBILITY-CHOICE.md) | **wall**: whether Symboleo's published semantics actually expresses ГК 450.1 / 157(3) — W2 |
| 4 — code → law audit | one hand-run finding | no wall yet; it needs the extraction step, which is work |
| 5 — certificate | three layers known, no format | **wall**: what replaces an authority endorsement when no authority will sign — W3 |
| 6 — portfolio edges | two notes out, no answers | **external wall**, waiting |
| corpus | ConsultantPlus only, commercial | **wall**: official machine-readable access to Russian acts — W5 |
| uniqueness rule | 43 % of spans fail on line wrapping | **wall**: what the accepted convention is for quote uniqueness — W6 |
| oracle | none found | **wall**: any provision with a fully published arithmetic — W4 |

Round 03 ([`docs/24`](24-ROUND-03-QUESTIONS.md)) is exactly these six walls, one question each, none of them a
repeat of rounds 01–02.


---

## §6 What this machine can and cannot reach (measured 2026-10-29)

`lab/probe-egress.py` probes three groups of hosts. Result:

| Group | Reachable | Detail |
|---|---|---|
| **search** (discovery) | 5 of 5 answer, **0 usable** | DuckDuckGo returns its anomaly page (HTTP 202), Mojeek a JavaScript captcha, Qwant a JS shell whose API answers 403, Bing and Startpage challenge pages, SearXNG instances unreachable |
| **docs** (retrieval) | 3 of 4 | IETF and arXiv fine; EUR-Lex answers 202 with an empty body; w3.org answers 403 to a plain client but works through the harness fetcher |
| **legal** | 3 of 7 | ConsultantPlus, `publication.pravo.gov.ru` and `pravo.gov.ru` fine; **`vsrf.ru`, `sudact.ru`, `kad.arbitr.ru`, `garant.ru` fail at TLS** (`UNEXPECTED_EOF_WHILE_READING`) |

**The distinction that governs this stage: retrieval works, discovery does not.** With a URL we can open a
primary source and quote it. Without one we cannot find it, so any question that needs discovery must be answered
by a human or deferred to a round — and a round cannot be answered by us either, because *finding* the sources is
the same blocked capability.

Practical consequences recorded here so they are not re-learned:

1. `lab/search.py` is kept but is **not functional in this network**; it is written for an environment where
   engines answer. Do not treat its empty result as "nothing exists".
2. Round answers that supply URLs are far more valuable than answers that supply names, for exactly this reason.
3. Russian court acts are unreachable from here; the day-count/rounding convention (W1) therefore cannot be
   verified on this machine even though it is one URL away.
