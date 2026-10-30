# 34 — The usefulness reports: what the genre reuses, and the five questions it forces

`docs/33` took the rubric of HackerNoon's *Proof of Usefulness* and measured this repository against it. This document
goes one level deeper: the winners' reports are not essays, they are **interviews against a fixed questionnaire**, and
the questionnaire is the reusable artefact.

Read on 2026-10-30: Claude Code Organizer (87.94), Visby (76), FoxPlug (67.19), FlowMind (47), plus the rubric page and
the announcement. Not opened: the remaining ~26 reports; nothing below rests on them.

---

## §1 The questionnaire, verbatim

Every report answers the same questions, in the same order. The five that carry weight:

1. **"What is your traction to date?"**
2. **"Not vanity metrics or projections — what's the one data point that proves people genuinely need what you've
   built?"**
3. **"How do you measure genuine user adoption versus 'tourists' who sign up but never return?"**
4. **"What's your retention story?"**
5. **"If we re-score your project in 12 months, which criterion will show the biggest improvement, and what are you
   doing right now to make that happen?"**

Then the score (a number from −100 to +1000) and a public report page per project.

**Question 2 is the whole genre.** It forbids the two moves that make usefulness claims cheap — vanity metrics and
projections — and it demands one point that a stranger could check. The score, by contrast, is computed from the
appellant's own inputs in seconds (see `docs/33` §1); it is the weak half.

## §2 What each winner actually offered as that one data point

| project | score | the data point | third-party observable? |
|---|---|---|---|
| Claude Code Organizer | 87.94 | npm downloads: **1,200 in week 1 → 8,135 in week 2**, 209 GitHub stars, an MCP registry listing | **yes** — npm and GitHub numbers are not the author's to invent |
| Visby | 76 | ~2,500 users, ~1,800 weekly active, **~20 % AI-visibility improvement within the first month** for brands acting on the tasks | partly — the user counts are self-reported, the improvement is measured against a crawler |
| FoxPlug | 67.19 | no revenue; "give-first" — free white-label launch kits gifted to Product Hunt makers | no — and it says so, and is scored anyway |
| FlowMind | 47 | (report largely promotional; no checkable point found in the text I read) | no |

Two things follow, and they are not the same thing:

- the **high scorer** is the one whose evidence a stranger can verify without trusting them (a download curve);
- the **honest low scorer** (FoxPlug) states "without revenue" in the first paragraph and is not punished for it beyond
  the number.

## §3 The transfer to this repository

**Adopted:** `lab/usefulness.md` — our own answers to the same five questions, with no score and no projections. It is
linked from `docs/33` and from the README, and it is the one place where a reader can see the distance between "the
checker works" and "someone needed it".

**Adopted as a rule:** a usefulness claim needs an artefact **outside the claimant** — a download count, a citation, a
third party's reproduction, a decision that cites the verdict. Anything produced by us about ourselves is, by
definition, the vanity metric the questionnaire forbids.

**A symmetry worth naming:** FoxPlug's "give-first" strategy — producing free artefacts to create evidence — is exactly
what this repository has been doing with the cross-audit exchange. Four reviews out, one defect found in us, two
mechanisms imported, one CI broken and fixed. That is real evidence of usefulness by the genre's own standard, and it
is *ours to name only because the other side wrote it down*.

## §4 What the genre cannot do, and where we agree with it

The questionnaire cannot distinguish "useful" from "popular", and its own instructions admit the weighting: brand-new
products score low, established products high. That is an honest description of a market, not of utility — and it means
a legal checker with no users would be scored near the floor while telling the truth about the law.

We take the questions and reject the arithmetic. §5 is the consequence: a repository that answers them in public and
prints its own zero.
