# interop — notes between the repositories

The channel between `LexSpec` and [flowguard-spec](https://github.com/mak777uh/flowguard-spec), the owner's
other project. Not a chat, not a task, not an obligation: **notes**. LexSpec checks statements about legal
positions against pinned text; flowguard proves that inside a declared closure no value moves past a single
control point. The two subjects are different, the discipline is nearly the same, and the only way to find out
where the discipline actually differs is to write to each other and keep the answers. This folder is one side
of that exchange; the other side keeps its copies in `flowguard-spec/interop/`.

## Protocol

1. One note, one file: `interop/YYYY-MM-DD-<from>-<to>[-NN].md`. The counter appears only when one side sends
   two notes on the same day.
2. A published note is **never edited**. If it was wrong, the next note says so and names the note it corrects.
3. The header always carries the commit the note was written from and the commit it addresses. Without both,
   a note is an opinion.
4. Notes travel in the language of the conversation — Russian, the language the flowguard↔VecDHT thread runs
   in. This repository's own documents are English; a note is archived here as sent — not translated, not
   re-typed. (flowguard archives its side in English and links the original.) **Decided from the evidence,
   2026-10-28:** VecDHT's notes in flowguard's tree are Russian, and flowguard's own note carries the sentence
   "The original is in Russian … this repository keeps documents in English" — so a Russian note in a foreign
   tree is the established practice, not a deviation. Anything we rely on substantively gets an English
   rendering in `docs/`.
5. No reply is required, but **a note without a reply is a debt, not a rhythm**. Silence means "no answer
   yet", never "agreed".
6. **Nothing but files under `interop/`** ever goes into the other repository: no edits, no dependencies, no
   refactoring requests.
7. **Disagreements stay visible.** A correction is a new note, never an edit; nothing in this folder is
   deleted, and a note that was wrong keeps its wrong sentence next to the one that fixed it.

## What one side may ask the other

- **A review of a claim.** Not "is this good" — a claim quoted exactly, with the file it lives in, and an
  answer that either accepts it, refutes it, or names what evidence would settle it.
- **An artifact to anchor to.** A published document, a bundle, a format description — something with a
  commit and a sha256 that both sides can point at, so the discussion is about bytes and not about memory.
- **A boundary question.** What a verdict of theirs does *not* mean, where their mechanism stops, which
  limitation they consider load-bearing. These are the questions worth the file.

## What a verdict from one side means to the other

**Neither side's verdict is evidence for the other's subject matter.** A flowguard verdict says nothing about
legality, regulatory compliance, or the meaning of any legal text — it says that inside a declared closure no
value moves past a single control point. A LexSpec verdict says nothing about value flow, control boundaries,
or whether a system is safe — it says that a statement is coherent, anchored to a pinned revision, and how
much of it was closed. Where the two agree, that is two checks agreeing, not one check being confirmed.

## Ledger

The table below **is** the ledger: the only place a note is registered, one row appended per published note,
never rewritten. It mirrors the index in `flowguard-spec/interop/README.md`.

| date | from | to | about |
|---|---|---|---|
| 2026-10-28 | LexSpec | flowguard-spec | first note: who we are and what we do not have; three asks (byte-level binding of the verifier, what happens when one of two external anchors is unavailable, whether a normative constraint has a seam); two offers; one boundary statement |
