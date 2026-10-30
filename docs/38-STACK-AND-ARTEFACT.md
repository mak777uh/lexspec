# 38 — The stack advice from the chat, and the smallest artefact that answers it

The owner pasted a thread recommending a stack for AI products: **Python backend, React for web, shadcn + TanStack for
UI (easy for models to integrate), NestJS for large backends, Hono for small ones** — with the argument that current
models are best trained on these stacks, so reliability is higher, "especially if you give the model an explicit list
of high-reliability libraries".

This note records what the advice is worth, what was taken, and what was refused.

---

## §1 What kind of claim it is

Community experience, twice removed: the author says "проверено", and the thing that was checked is their own delivery
history, not a measurement anyone can reproduce. By this repository's own rule — *a number without a command is not a
result* — that makes it an opinion. It is recorded as an opinion in
[`lab/sources.md`](../lab/sources.md), with the date, and it moved nothing in the checker.

It does contain one observation that is testable in principle and true in practice: **models are better at stacks they
saw more of**, so generated UI code in React + shadcn will look more plausible than in an exotic framework. The trap in
"look more plausible" is the one this repository knows by name: generated code is a hypothesis until something checks
it ([`docs/06`](06-FROM-TEXT-TO-PROOF.md), AGENTS §9).

## §2 Why a stack is not the next step

Three facts about this project, in order of weight:

1. **No one has used a verdict** — stated in every report and answered in [`lab/usefulness.md`](../lab/usefulness.md).
   A UI is a way of serving users; there are none.
2. **The checker's output is already the product**: JSON that names the verdict, coverage, findings, the corpus bytes
   and hash, the positions, the quantities, and the six-line `not_claimed` block.
3. **Every dependency is a surface that needs its own guards.** A React build would add a toolchain, a lockfile, an
   update channel and a supply chain to a repository whose entire CI runs on a bare Python and finishes in a minute.

## §3 What was built instead

[`tools/report_html.py`](../tools/report_html.py): one command turns a JSON report into a **single self-contained HTML
file** — no JavaScript, no CDN, no framework, 4 KB for the quantified ГК 395 statement. It renders the verdict, the
corpus block with digests and revisions, the findings, the positions, the quantities with the total, and the
`not_claimed` block as the last thing a reader sees.

Two tests pin the properties that make it useful rather than decorative:

- the page contains the verdict, `legal validity` and `usefulness` — the boundary travels with the artefact;
- the page contains **no `http://` or `https://` at all**: nothing has to load from the network for a verdict to be
  read, and the file stays under 60 KB so it can be emailed to a lawyer.

That is the honest answer to the stack advice: the first thing a reader needs is not a React application, it is a page
that shows what was checked against which bytes and what was not claimed — and that page must work offline, because a
legal artefact that depends on a CDN is a legal artefact that can stop being readable.

## §4 When the stack question becomes real

Recorded as deferred with triggers, not as a rejection:

| trigger | then |
|---|---|
| a user asks to run checks without a terminal | a static page over the JSON is already enough; add a file picker, still no framework |
| several users need shared history | a server appears, and the JSON remains the wire format |
| someone needs to author statements in a browser | a form over the schema, with the checker as the only authority — never a second validator in the client |
| the page needs interactivity beyond reading | **then** a framework, chosen with the same evidence standard: bundle size, dependency count, and a guard that pins the lockfile |

The one rule that does not move: **a UI may render a verdict and may never compute one.** A second implementation of the
checker in the browser would be exactly the differential-versus-independent confusion the family already warned about.

## §5 Boundary

Read: the pasted thread. Not read: the projects where the advice was "проверено", any benchmark of model performance on
these stacks, or the shadcn/TanStack/NestJS/Hono documentation. No claim here about whether those stacks are good — only
that the claim, as made, is experience rather than evidence, and that this repository has no user who needs a stack yet.
