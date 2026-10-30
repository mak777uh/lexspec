# 37 — The Telegram export: what it contains, and the honest answer that it is not a legal source

The owner sent `ChatExport_2026-10-30/result.json` for study. It is a two-year Telegram export: **7 022 entries, 4 749
of them messages**, 2024-10-20 → 2026-10-30, dominated by two voices, with **1 533 links to arXiv**, 1 026 to GitHub,
400 to alphaxiv, 243 to HuggingFace. Digest scripts: [`lab/digest-chat-export.py`](../lab/digest-chat-export.py),
[`lab/digest-chat-export-pass2.py`](../lab/digest-chat-export-pass2.py); **aggregates only** in
[`lab/chat-export-summary.json`](../lab/chat-export-summary.json).

---

## §1 The measurement error worth reporting before the findings

The first pass counted messages by stems and reported **150 "law" messages**. The second pass, with word-boundary
patterns, found **43** — and most of those are metaphors: *"From Laws to Motivation"* (a reinforcement-learning paper),
*"Zipf's Law"*, *"закономерность"*. The stem `прав` had been matching `правильно` and `правда`.

| pass | pattern | count | what it actually measured |
|---|---|---|---|
| 1 | stems | 150 | the word "прав" in any form, mostly "correct" |
| 2 | `\b(закон|юридическ|правов|договор|…)\b` | 43 | legal vocabulary, still mostly metaphor |

**This is P7 in miniature.** A count over a badly chosen term set is a number that looks like a measurement, and it is
exactly the defect the repository keeps finding in its own guards. The two numbers are recorded side by side because
the difference between them *is* the error of the first method.

## §2 What the export is

Themes by message count (boundary-anchored): **agents 461**, evaluation 116, provenance 88, formalisation 80,
standards 45, verification 44, safety 38. The channel is an LLM research feed: papers, repositories, launches, tooling.
The most-cited hosts are arXiv and GitHub by an order of magnitude.

**It is not a legal channel.** Forty-three messages with legal vocabulary, most of them using "law" as a metaphor,
zero of them about codifying a statute, anchoring a clause, or checking a contract. Reading it for legal insight would
be a category error, and saying so is more useful than extracting two quotes and calling it a source.

## §3 The three leads that do matter, each mapped to a question we already carry

| lead | in the export | why it matters here |
|---|---|---|
| **Terence Tao, *Machine-Assisted Proof*** (AMS Notices, 2025) | linked 2024-12-29 | the strongest statement of what a proof assistant does and does not deliver — the source class behind `H3` (*soundness is relative*) |
| **Wolfram, *Who Can Understand the Proof?*** (2025) | linked 2025-01-10 | the legibility gap: a formal artefact can be checkable and incomprehensible at once. That is our **C6** (every mechanism names its source or its gap) and the reason `not_claimed` exists |
| **ImProver** (2410.04753), **Reasoning Gym**, Lean IMO dataset (2411.18872) | linked Jan 2025 | algorithmically checkable environments with a machine-checked oracle — the `ADR-0008` oracle question, in a domain that already solved it |

None of these is legal. All three bear on the same structural question we have been circling: **the difference between a
thing being checkable and a person being able to check it.** That gap is where this project lives, and the export is
evidence that the AI-research community is circling it too, from the other side.

## §4 What was taken, what was not

**Taken:** three references to add to the source register with the questions they bear on, and the methodological
lesson of §1 (recorded as a worked example of an error we warn about).

**Not taken:** anything as a *legal* source — there is nothing there. No claim in this repository may cite this export
for a proposition about law, corpora, or judicial practice. The export is a record of what the owner reads, not
evidence about the world.

**Also not taken:** the arXiv feed as a landscape input. `docs/12` grades 53 approaches against our own re-check; adding
papers because they were linked in a chat would be volume pretending to be coverage — the exact failure this repository
spent a week removing.

## §5 Boundary

Read: the digest of all 4 749 messages by theme, plus the 43 legal-vocabulary messages and the top arXiv identifiers.
Not read: the 1 533 papers behind the links, the 1 026 repositories, or the discussions outside the extracted themes.
The export itself stays outside the repository, and so do the messages: the first version of the digest stored
message bodies and the secrets guard refused it, which was right twice over — other people's chat is not a
measurement, and a committed file that quotes a chat is publishing someone else's words. The summary keeps
counts, link hosts and arXiv identifiers; the scripts take the export path from --source or
$LEXSPEC_CHAT_EXPORT, so no machine-local path reaches the repository.
