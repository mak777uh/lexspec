# 40 — Rust: the first slice, and what byte-identity means

The owner confirmed the direction already recorded in [`ADR-0002`](../lab/decisions/ADR-0002-implementation-language.md):
**Rust is the primary implementation, the Python checker is the permanent twin.** This document records the first
slice, what it proves, and what it does not.

---

## §1 What was built

`rust/` — a binary crate with **no dependencies at all**:

| file | what it is |
|---|---|
| `src/sha256.rs` | SHA-256 written by hand, with known-answer vectors and a chunking test |
| `src/canonical.rs` | JSON parser and canonical emitter, with duplicate keys refused and floats refused by name |
| `src/main.rs` | `lexspec canonical <file>` — prints the canonical text and its digest |
| `Cargo.toml` | `[dependencies]` empty, and a comment saying why |

The absence of dependencies is a decision, not an accident: this tool's product is a claim about *bytes over time*, and
a chain of custody that begins with a supply chain has already lost the argument. Two consequences follow immediately —
`sha2` and `serde_json` were both declined — and one of them turned out to matter for correctness rather than taste:
`serde_json` keeps the last duplicate key silently, while spec §3 says a document with two identical keys is not a
document. The hand-written parser refuses it.

## §2 What it proves

**12 of 12 examples produce a byte-identical canonical form and the same digest as the Python tool.**

```
ok    01-delivery-ok.lex.json                    00f179ed760bdfa7
ok    02-opposite-conflict.lex.json              2aab24f4d2048bc8
…
ok    12-gk-rf-395-doctrinal.lex.json            619c75ec52013c6d

byte-identical: 12/12
```

That is the acceptance test ADR-0002 set, and it is the *only* thing worth testing first: identity is over bytes, so a
second implementation that parses to the same structure but serialises differently is not a second opinion, it is a
second bug. Reproduce with `python lab/compare-rust-python-canonical.py`.

Also proven, because a second implementation is where these show up:

- keys are sorted by code point at every depth, not by locale;
- whitespace disappears regardless of how it was written;
- `0.5` is refused with a message that names the reason (a float cannot be hashed reproducibly);
- `{"a":1,"a":2}` is refused, with a message that says what a duplicate key means;
- control characters are escaped, Cyrillic stays literal UTF-8;
- `{} {}` is not a document.

## §3 What it does not prove yet

Everything except identity. The Rust binary **cannot check a statement**: no schema validation, no anchoring, no
positions, no coverage, no verdict, no quantities, no defeat. The Python checker remains the executable contract, and
the Rust side is, for now, a canonicaliser with a very good test.

That ordering is deliberate and matches the specification-first rule: the contract is being frozen in Python while the
Rust port follows it step by step, each step gated by byte equality on the same inputs. The next slices, in order, are
the ones whose agreement is cheapest to check and most valuable to have:

| next | what must agree |
|---|---|
| statement validation | the same `S1_*` codes for the same malformed documents |
| anchoring (normalise, then match) | the same spans resolve, the same ones are ambiguous |
| coverage and verdict | the same numbers and the same verdict on all 12 examples |
| report JSON | byte-identical, which is the strong test |

## §4 The toolchain, for the record

Rust was already present on this machine: `cargo 1.99.1`, `rustc 1.99.1`, default host `x86_64-pc-windows-gnu`, and the
linker that works is the standalone mingw under the user profile (`<profile>/mingw64/bin`) (the MSVC linker is absent, and the mingw
that ships with miniconda fails to link — a trap `VecDHT` documented before us). Building therefore needs that
directory first on `PATH`; the crate itself needs nothing else.

## §5 Boundary

Read and built: the four files above, `cargo test` (8 tests: 3 known-answer digests, chunking, 6 canonical rules).
Not done: any statement checking, any CLI compatibility with the Python flags, any CI step — the Rust build is not in
`guards.yml` yet, deliberately, because a build that does not yet check anything would add a minute to every push for
no evidence.
