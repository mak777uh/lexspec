# ADR-0002 — Implementation language: Rust primary, Python as the permanent twin

- **Date:** 2026-10-28
- **Status:** accepted as a direction; **confirmed by the owner on 2026-10-28** ("хорошо"); **nothing is implemented** — [ADR-0001](ADR-0001-gather-before-build.md) still governs when building starts
- **Evidence:** [`docs/09-IMPLEMENTATION-LANGUAGE.md`](../../docs/09-IMPLEMENTATION-LANGUAGE.md) — requirements, candidate matrices, measurements taken on this machine, download list, and what would overturn the choice

## Context

The checker computes identity over **bytes**. A statement's hash must be stable across machines and across
implementations, or a verdict stops being reproducible by a stranger — which is the only reason the project
exists (charter C1, C2). That requirement turns an ordinary language choice into the choice of how easily a
wrong hash can be produced.

Twelve requirements were derived from the spec and the hypothesis register before any language was considered.
Two of them decided the outcome:

- **R3** — no floating-point numbers anywhere (spec §3). A parser that collapses `1` and `1.0` cannot hash what
  the author wrote.
- **R7** — the verdict must be constructible only inside the checker (H13). This is the difference between a
  rule and a mechanism.

## Decision

1. **Rust is the primary implementation language** for the checker.
2. **Python remains a permanent second implementation**, not a prototype to be discarded. It is the *twin*
   whose disagreement with Rust is the only real test of byte-level identity, and it stays the harness for the
   lab and for adversarial fixtures.
3. **TypeScript is excluded** — not by taste, but by measurement: on this machine `JSON.parse("1.0")` and
   `JSON.parse("1")` are the same value and both re-serialise as `1`, and `9007199254740993` becomes
   `…992`. Identity is over bytes; a parser that cannot see the difference cannot be the primary.
4. **Go is a viable fallback**, not chosen: R7 is achievable there (unexported type in its own package) but
   has to be defended against `encoding/json`'s HTML escaping and its `float64` default.
5. **Lean 4 is not a candidate for the checker.** It is the target for H3's proofs, and v0.2's bridge is
   "emit a Lean file, `lake build`, record `#print axioms` as evidence" — never as a verdict upgrade (H8).

## Why Rust, in one line each

- `1` and `1.0` stay distinguishable after parse (`Number` keeps `i64`/`u64`/`f64` apart), so R3 is structural.
- Key ordering by code point is what `BTreeMap`/`str: Ord` already does — R2's hardest sub-problem is free,
  while Python needs `sort_keys` to be *the same* rule and JavaScript needs a hand-written comparator.
- R7 becomes a type: a private field with no public constructor, enforceable by review, rather than an AST scan
  that is a test.
- R12 (a stranger replays the certificate) is one static `.exe` plus `rust-toolchain.toml` and vendored deps;
  the Python twin needs an interpreter and a tree.
- `wasm32-wasip1` is a Tier-2 rustup target, so an agent-sandbox build is a flag rather than a project.

## Costs accepted

- **MSVC Build Tools on Windows** is now a prerequisite — the only real install cost in the comparison.
- Two implementations must be kept in step. That is deliberate: the twin exists to disagree.
- Neither `cargo` nor `go` is installed on this machine yet (§6 of docs/09 lists exact versions).

## What would overturn this

1. If the byte-identical canonicaliser in Rust turns out to need hand-written duplicate-key detection *and*
   hand-written string escaping *and* more than ~150 lines before the first test, Python's 45-line canonical
   core (measured) wins on simplicity and Rust's advantage shrinks to R7 alone.
2. If the Lean bridge turns out to require a Rust-Lean FFI rather than a subprocess, the interaction cost
   changes and Go — which also subprocesses — becomes equal.
3. If the primary consumer is a JavaScript host (an agent runtime in Node), the `.exe` advantage disappears
   and a WASM build from either language is the real requirement.

## Consequences for the documents

- `docs/09` §6 is now the install checklist; it is not a build instruction.
- The Python implementation is **not** deprecated. Any change to `tools/lexcheck.py` must state whether the
  Rust twin is expected to agree, and the divergence test is the point.
- Nothing in this ADR changes the spec. It changes what a future implementation must be able to prove about
  itself.

---

**Implemented, 2026-10-31.** The first slice is in `rust/`: a dependency-free crate that canonicalises and hashes, and
agrees with the Python twin byte for byte on **12 of 12** examples (`python lab/compare-rust-python-canonical.py`).
The decision above said identity is over bytes and that a second implementation is the only real test of it; that test
now runs. What remains is everything except identity — validation, anchoring, coverage, verdicts — and the record of
what was deliberately not built is in [`docs/40`](../../docs/40-RUST-FIRST-SLICE.md) §3.
