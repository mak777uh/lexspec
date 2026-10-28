# 2026-10-28 — the corpus pin depends on checkout line endings

**origin: model** (written by the engineer building the reference checker)
**status: open hazard, mitigated in-repo only for the files the checker reads**

## The observation

`corpus[].text_sha256` is the sha256 of the corpus file's *bytes* (spec §5: the
pin is by content, never by URL). C0_CANON also requires the statement file to be
LF and BOM-free (spec §3.1). Both facts make the verdict depend on how git wrote
the working tree, not only on what was committed.

On a Windows machine with `core.autocrlf=true`, a fresh clone converts LF to CRLF
in `.txt`/`.json` text files. The repository itself is fine — the committed bytes
are LF — but the working tree is not, and then:

- every example is refused with `C0_CANON` (CRLF in the statement file), and
- every atom fails to anchor with `S2_HASH_MISMATCH` (the corpus file's bytes
  differ from the pinned digest).

Both failures are *correct behaviour* of the checker: the pinned text really is
not the text on disk. The defect is in how the repository is checked out, not in
the check.

## Why this was not "fixed" in code

Normalising line endings inside `lexcheck.py` (hash the file after stripping
`\r`, or reading with universal newlines) would make the reported digest differ
from the bytes an author signed. That is the one thing a content pin cannot do:
it would turn "verified against these exact bytes" into "verified against some
normalised version of these bytes", which is a weaker and differently-worded
claim. Refusal is the honest outcome, so the checker refuses.

## The fix belongs in a root file this work does not own

A `.gitattributes` at the repository root, e.g.

```
* text=auto eol=lf
*.txt -text
*.json text eol=lf
```

The `*.txt -text` line is the load-bearing one: it tells git never to touch the
bytes of a pinned corpus text, so the digest means the same thing on every
platform. Until it exists, a Windows clone may legitimately fail `guards.yml`,
and the failure will name `C0_CANON` / `S2_HASH_MISMATCH` rather than this note.

## Boundary of this note

Written from the repository state at the date above, on a machine with
`git config --get core.autocrlf` unset at repository level. The global git
configuration was not read; if it sets `autocrlf=false`, the hazard is theoretical
on that machine and real for anyone cloning with the default Windows setting.
