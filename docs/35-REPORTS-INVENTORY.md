# 35 — All the reports, read for the shape of the evidence

Ten of the winners' reports were located, fetched and read in full (inventory: `lab/usefulness-inventory.json`,
collector: `lab/usefulness-inventory.py`). The point of reading all of them rather than the top scorer is that the
distribution is more informative than the ranking: **a project with 14 installs scored 94, and a project with 2 500
users scored 76.**

---

## §1 The inventory

| project | score | domain | the "one data point" it offered | class of evidence |
|---|---|---|---|---|
| **PMB** | 115 | local-first memory for coding agents (BM25 + vector + graph over MCP) | 1.0 release on PyPI and the MCP registry; **pre-traction on raw numbers** | distribution + admission of no adoption |
| **Snatch Guard** | 94 | iPhone theft detection (accelerometer + Screen Time) | **117 000 phones stolen in London in 2024**, and Android has had the equivalent since 2024 while iOS has none | **problem evidence, external** — with 14 installs |
| **AIOProductOS** | 94 | product OS joining feedback, revenue, work and code on one record | design partners **wired their live production sources** (revenue, tracker, support inbox) | **costly commitment**, not signups |
| **Claude Code Organizer** | 87.94 | dashboard for Claude Code memories, configs, MCP servers | npm downloads 1 200 → 8 135 in two weeks, 209 stars, registry listing | **adoption volume**, third-party observable |
| **Visby** | 76 | brand visibility across AI search | ~2 500 users, ~1 800 weekly, ~20 % visibility improvement for brands acting on tasks | adoption (self-reported) + measured effect |
| **FoxPlug** | 67.19 | white-label launch kits | **no revenue**; free kits gifted to Product Hunt makers | honest zero + a mechanism |
| **TransactionLink** | 66.13 | KYB/KYC onboarding automation | explicitly refuses the consumer metric: "reach is better measured by **verification volume**" | **metric choice** matched to the transaction |
| **HostLens AI** | 55.35 | graph-native host intelligence (Neo4j prize) | not extracted in this pass | — |
| **FlowMind** | 47 | AI project manager that auto-assigns tasks | the text I read offers no checkable point | promotional |
| **Ella's AI Agent** | 46.06 | agent product | not extracted in this pass | — |

Not found by search (10 of 20): Siiqo, Cofoundr, HOL Guard, Visual MCP Gateway, tenv, Autonomous Company Deep
Research Agent, hello.cv, Developer Farm, theCloaq, Tinky Town. Their absence is recorded rather than papered over:
the report site has no list endpoint and the tag page is rendered client-side.

## §2 What the ranking does not mean, and the four deep reads

**The score is not adoption.** Snatch Guard scored 94 with **14 installs** and 1 390 landing-page visitors; PMB scored
115 while saying in its own words that it is "pre-traction on raw monthly numbers". Whatever the algorithm rewards, it
is not installs.

What those two did instead was argue with two different, stronger things:

- **Snatch Guard: problem evidence.** 117 000 thefts in one city in one year is a number it did not produce, and the
  existence of an Android equivalent since 2024 proves the gap is real rather than invented. The instrument had 14
  users and the *problem* had a hundred thousand victims. That is the only kind of claim a stranger can check without
  trusting the author.
- **AIOProductOS: costly commitment.** "Signups are cheap and prove nothing; connecting the systems that run your
  business to a new spine is a real act of trust." The evidence is a behaviour that costs the user something.

**Claude Code Organizer: adoption volume** — the one class that requires no argument, only a download counter, and
the only one a stranger can verify without trusting anyone.

**TransactionLink: metric choice.** A B2B compliance product refuses "monthly visitors" and names verification volume
instead — because the metric has to match the transaction. Copies of this insight are cheap and rare: *choose the unit
in which your thing is actually consumed, and refuse the units that flatter you.*

## §3 The synthesis: three classes, not one score

| class | what it is | who can verify | our instance |
|---|---|---|---|
| **problem evidence** | an external fact showing the problem is real, independent of our product | anyone, from a public source | **we have several**: 6 of 14 quotes failed on real corpora; a schema allowed less than the shipped examples used; a documented exit code did not exist — each found by an outsider or by our own measurement, each a fact about the problem class |
| **costly commitment** | someone spends their own effort wiring, publishing or re-running | the person who spent it | **one**: `flowguard` wrote a verifier that imports our canonicaliser and diffs it byte for byte, and re-ran its own reproduction to close `F-3-1` |
| **adoption volume** | downloads, installs, weekly actives | anyone, from a counter | **none** |

The genre collapses these into one number, and the number then reads as "usefulness", which is why 14 installs and
2 500 users can sit 18 points apart while the 14-install project has the stronger claim about *need*.

**Adopted into `lab/usefulness.md`:** the three classes, our actual instances per class, and the rule that a claim of
usefulness must say which class it belongs to. It also changes one of our answers: question 2 of the questionnaire is
not "what is your traction" — it is "what external fact shows the problem is real", and for that we do have evidence.

## §4 What was taken from the mechanisms, not the marketing

- **PMB** — local-first memory with hybrid lexical + vector + graph retrieval over MCP. The transferable idea is not
  the stack but the **shape**: our `lab/experiments.jsonl` and verdict reports are exactly the kind of durable record
  an agent should be able to query, and MCP is the current way to expose it. Recorded as a candidate, not built: a
  server with no users is a second product.
- **TransactionLink** — the metric must match the transaction. For us the transaction is "a verdict consumed by
  someone deciding something", so the unit is *verdicts cited*, not stars, not visits.
- **Snatch Guard** — a high score without adoption is legitimate **only** when the problem evidence is external. That
  is the one place where our repository already has something to show, and it has never said so.

## §5 Boundary

Read in full: 10 reports. Extracted only by regex, not by hand: HostLens AI, Ella's AI Agent (scores and slugs only).
Not found: 10 reports (listed in §1). Not read: the score breakdown pages at `proofofusefulness.com`, the comments, and
any winner's product itself. No claim here about whether these products work.
