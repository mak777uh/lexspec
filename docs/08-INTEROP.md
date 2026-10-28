# 08 — INTEROP: the channel to flowguard-spec

LexSpec and [flowguard-spec](https://github.com/mak777uh/flowguard-spec) are checked against each other on
purpose. flowguard proves that inside a declared closure no value moves past a single control point and issues
a statement a third party can re-derive; LexSpec anchors every normative atom to an exact span of a pinned
revision and issues a verdict over `(statement, encoding, corpus@revision)`. Different subjects, nearly the same
discipline — so the questions travel: does a verifier bind bytes or trust fields, what happens when an external
anchor is unavailable, and is there a seam where a *normative* constraint could be attached without weakening
the existing proof.

The channel is [`interop/`](../interop/README.md): one file per note, dated filename, append-only. The protocol
lives there and is not repeated here.

**The ledger is the index table in [`interop/README.md`](../interop/README.md#ledger)** — one row appended per
published note. There is no separate ledger file, deliberately: a ledger that can drift from the folder it
describes is a second source of truth.

**A note is never edited after publication.** A correction is a new note that names the one it corrects. A note
that was wrong keeps its wrong sentence next to the answer, because a channel where the past is always right
cannot be read a month later.

Neither side's verdict is evidence for the other's subject matter: a flowguard verdict says nothing about
legality, and a LexSpec verdict says nothing about value flow.

| date | direction | the ask in one line |
|---|---|---|
| 2026-10-28 | LexSpec → flowguard-spec | what the verifier binds byte for byte, what the two external anchors do when one is unavailable, and whether a normative constraint has a seam — plus two offers and one boundary statement |
