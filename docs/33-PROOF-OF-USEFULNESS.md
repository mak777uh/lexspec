# 33 — Proof of Usefulness: the one claim this repository has never made

The owner sent the HackerNoon *Proof of Usefulness* hackathon results and asked for insights in the reports. The genre
is directly relevant, because it is a **market for the claim `lexspec` does not make**: that the software is useful.
Read: the rubric page, one winner report (Visby, 76), the score breakdowns, and the announcement.

---

## §1 What the genre actually is

| Element | How it works | What it is worth |
|---|---|---|
| **Rubric** | four named dimensions: **user adoption, revenue, technical stability, genuine problem-solving**, scored from −100 to +1000 | the useful part — it names what usefulness would consist of |
| **Inputs** | live URL or repo, description, audience, **user metrics (active users, retention, growth)**, revenue, technologies, **evidence of traction: URLs to reviews, testimonials, analytics** | the honest core: a claim about usefulness must point at an artifact outside the claimant |
| **Score** | generated **in seconds** by an algorithm from those inputs | the weak part: a number computed from self-reported data, with no verification of any input |
| **Report** | the founder's narrative around the score, decomposed by criterion | marketing with a decimal point |
| **Maturity rule** | "brand new projects will likely score lower… resubmit later as you gain users" | honest, and the one sentence we should copy verbatim in spirit |

Their own instructions say it out loud: *more detailed, quantitative evidence leads to better scores.* The score is a
function of how well you document yourself, not of whether anyone uses the thing.

## §2 Why this lands on us specifically

Our repository has a claim registry, a consistency guard, a prose-vs-tree guard, a catalogue guard, an independent
arithmetic twin, and a `not_claimed` list that names five things we do not check. It has **no line about usefulness**,
and the genre makes that absence impossible to ignore: everything we measure is about *correctness of a check*, and
nothing is about *consequence*. A stranger reading `README.md` can verify that our verdicts are reproducible and
cannot learn whether the product ever helped anyone, because nobody outside this repository has used it.

That is not a gap to close by writing a better README. It is a gap to **name**, in the same place where we name the
other five.

## §3 Adopted: the rubric without the score

**1. Four dimensions, with the evidence each would require and whether we could ever produce it ourselves.**

| dimension | evidence that would count | can we produce it? | state today |
|---|---|---|---|
| user adoption | a named person or organisation that used a verdict in a decision, with a date and a quoted artefact | **no** — only they can | none |
| revenue | a contract, an invoice, a grant letter | **no** | none |
| technical stability | a guard that runs on every push, a red path demonstrated, a reproduction a stranger executed | **yes**, partly — this is our strongest dimension and our only evidence | measured: 80 tests, 8 guards with a catalogue check, CI green |
| genuine problem-solving | an artefact produced *outside* this repository that depends on it: a re-check by a third party, a citation, a policy audited by an outsider | **no** — by definition external | one near-miss: flowguard re-ran our reproduction and closed F-3-1 |

**2. A hard rule, written into the truth registry:** this repository publishes **no usefulness score**, and no
self-assessed number of that kind is admissible. A score computed from our own inputs would be exactly the defect the
family spent two days finding in our guards — a number whose inputs nobody verifies — and we would be grading
ourselves.

**3. `not_claimed` gains a sixth line**: usefulness. Every report now says, in the artefact a reader actually reads,
that no one outside this repository has used the result. That is more useful than a paragraph in a design document,
because it travels with the verdict.

**4. The maturity rule, copied in spirit:** we will not present the project as useful while adoption is zero, and when
it stops being zero the change will be a dated row with a link, not an adjective.

## §4 What was not adopted

- **The score itself.** Automated, unfalsifiable, and computed from the appellant's own numbers. We spent this week
  removing exactly this shape from our own guards.
- **Report-as-marketing.** Their reports are written by the founder and published under the project's own account; the
  genre's economy is attention, and attention rewards confidence. Our `not_claimed` economy is the opposite.
- **The sponsorship framing.** Not a defect, just not transferable: credits from vendors do not constitute evidence of
  usefulness, and treating them as evidence would be a category error worth naming before someone else makes it.

## §5 The uncomfortable comparison, stated plainly

If `lexspec` were submitted to that hackathon, it would score low, and the rubric would be right: adoption zero,
revenue zero, problem-solving evidence one near-miss. What it has is the dimension the rubric weights least and cannot
score automatically — **technical stability with demonstrated red paths** — which is precisely the dimension we can
prove and the market rewards least.

That asymmetry is not a reason to change what we build. It is a reason to stop implying, anywhere in the repository,
that correctness is usefulness. `docs/25` says the system has never been used; §3.3 now says it in every report.

---

*Sources opened 2026-10-30: the rubric page (`hackernoon.com/everything-you-need-to-know-about-hackernoons-proof-of-usefulness-hackathon`),
the Visby report (`…/visby-earns-a-76-proof-of-usefulness-score-…`), the FoxPlug score line, and the announcement text
the owner sent. Not opened: the other ~30 winner reports; no claim here rests on them.*

---

**Follow-up:** the winners' reports themselves are interviews against a fixed questionnaire, and the questionnaire is
the part worth taking. [`docs/34`](34-USEFULNESS-REPORTS.md) records the five questions verbatim, what each winner
offered as its one checkable data point, and this repository's own answers in [`lab/usefulness.md`](../lab/usefulness.md)
— which are, in four cases out of five, "none".
