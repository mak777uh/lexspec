# 39 — Memory audit: what is in the repository, and what is not

The owner asked whether anything unnecessary had been put into memory. Answered by measurement, not by recollection.

## §1 Size, measured

| area | size |
|---|---|
| `docs/` (39 files) | 0.49 MB |
| `lab/` (36 files) | 0.28 MB |
| `tools/` + `tests/` | 0.40 MB |
| `corpus/` (5 files) | 0.04 MB |
| `cross-audit/` + `interop/` | 0.07 MB |
| **whole worktree** | **≈1.6 MB** |

The largest tracked file is `tools/lexcheck.py` at 84 KB. There is no PDF, no archive, no generated bundle, no model
weight, and nothing over 100 KB.

## §2 What was checked and found clean

- **No junk tracked**: no `*.tmp`, no scratch scripts, no absolute Windows paths outside the one guard that forbids
  them, no chat export. The 466 KB digest that carried other people's messages **was never committed** — it was
  removed before the first `git add`, which is verified by `git log --all -- lab/chat-export-digest.json` returning
  nothing.
- **Data files are small**: `chat-export-summary.json` 3.6 KB (aggregates only), `usefulness-inventory.json` 5.5 KB,
  `hypotheses.jsonl` 2.1 KB, `preregistrations.jsonl` 1.2 KB, `experiments.jsonl` 3.8 KB.
- **Nothing untracked** in the working tree.

## §3 What was *not* clean, and is now fixed

A link-graph pass over `docs/`, `lab/` and `interop/` found **five documents that nothing linked to**:

| orphan | why it mattered |
|---|---|
| `lab/legal-read-gk-395.md` | the doctrinal read that produced four of our atoms and the П7 principle was unreachable from the README |
| `docs/08-INTEROP.md` | the channel's rules — the thing that justifies writing notes into other repositories |
| `lab/decisions/ADR-0005-chain-to-the-boundary.md` | the decision behind the architecture document was not linked from it |
| two `interop/2026-10-28-*` notes | the first notes of the exchange, listed in the index without links |

That is the repository's own kind of clutter: not size, but **unreachability**. A file nobody links to is a file nobody
reads, and a file that is not read drifts while looking maintained. All five are now linked, and the pass is a guard
(`lab/check-orphans.py`) so the next orphan is caught by CI rather than by an audit.

## §4 The prose question, answered honestly

The repository has **39 documents for about 4 000 lines of code**. That ratio is deliberate — the product *is* the
argument — but it is also the place where clutter will next appear, and the guard for it is different: a link graph
catches unreachable files, not redundant ones.

Three documents genuinely overlap: `docs/33` (rubric of usefulness), `docs/34` (the questionnaire) and `docs/35` (the
inventory of ten reports). They were written within hours of each other and could be one file with three sections.
Recorded here as a known redundancy rather than merged in a hurry: consolidating prose during a session that is also
changing the code is how contradictions get introduced, and this repository's rule is that the spec changes in one
commit with its guards.

## §5 Boundary

This audit measures the *tree*. It says nothing about whether the prose is worth reading — only that a reader can reach
all of it, that nothing large or private is stored, and that the one redundancy found is named.
