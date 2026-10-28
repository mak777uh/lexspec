# 09 — Implementation language: the choice, on evidence

Status: **decision input, not a decision record.** It answers one question — in which language is "the product"
written — as a function of requirements the spec already implies, not of taste. Nothing here was benchmarked:
this machine has no toolchain for two of the four candidates (Rust, Go — §8), so every performance statement is
either absent or replaced by the name of the benchmark that would settle it.

Reading order: [`10-SPEC-v0.1.md`](10-SPEC-v0.1.md) (what the checker must do), [`06-FROM-TEXT-TO-PROOF.md`](06-FROM-TEXT-TO-PROOF.md)
(the hypotheses, especially H3, H12, H13, H17, H20), [`00-CHARTER.md`](00-CHARTER.md) (non-goals).

---

## §1 Requirements, derived — not invented

Each row names where it comes from. `spec` = the constitution; `Hn` = a hypothesis in 06, which is weaker than
the spec and is labelled as such; `owner` = a constraint from the brief, which has no line in any document.

| # | Requirement | Source line that implies it |
|---|---|---|
| **R1** | Hash **exact bytes** of both the statement file and every corpus file; never hash a re-print | spec §5 (`CorpusRef.text_sha256`: "sha256 of the file's bytes"), §5.2, "the pin is by content, never by URL" (§5), H20 |
| **R2** | Produce a **deterministic canonical form**: UTF-8, no BOM, LF, keys sorted at every depth, no insignificant whitespace, non-ASCII literal | spec §3.1–§3.2, C0_CANON (§10), "computing it twice" (§3) |
| **R3** | **No floating-point numbers anywhere**; a fractional number is a statement bug, not a rounding event | spec §3.3 |
| **R4** | Read and write **JSON** only; no other input format, no proprietary container | spec §2, §12.1 |
| **R5** | Run **offline**, and be re-checkable by a stranger with the repo and no network | H12 (kill test), charter §7 ("an artifact that cannot be re-checked by a stranger is a claim") |
| **R6** | Be **callable by an agent**: a process boundary, a stable exit status, machine-readable output | H13 ("the encoder-facing API returns `CandidateAtom`"), README "Exit codes: 0 / 1 / 2" |
| **R7** | A **verdict only the checker can construct**: no path from encoder-supplied data to `Verdict` except through the check function | H13 ("`Verdict` constructible only inside the checker module"), H8 ("`verdict` is computed by a function that never takes prover output") |
| **R8** | Handle a corpus **large enough to matter**: tens of MB of pinned text, many spans, span uniqueness over the whole file | spec §5 rule 4 (`occurs exactly once`), owner brief ("tens of MB") |
| **R9** | Run on **Windows** natively, with WSL available but not required | owner brief; the CRLF hazard is already recorded in [`lab/2026-10-28-checkout-line-endings.md`](../lab/2026-10-28-checkout-line-endings.md) |
| **R10** | Produce and consume **Lean 4 proof artefacts** without letting them move a verdict | H2, H3, H8 ("a prover may add evidence beside a verdict and may never raise it") |
| **R11** | Have a path to a **WASM build**, if the checker is ever hosted inside an agent sandbox | owner brief (conditional; no spec line) |
| **R12** | Ship an artefact a stranger can **re-run** to reproduce the verdict, including the checker's own identity | H12, spec §11.7 ("a signed, self-contained certificate is a v1 candidate"), spec §9 ("a verdict produced with a non-default threshold must be reported with that threshold") |

R12 is the one requirement the brief did not list. It is included because H12's kill test is the project's own
success test, and because it separates "a program" from "a second copy of the program on the stranger's machine".

---

## §2 The crux, stated precisely

"Canonical JSON" sounds like one problem and is mostly a small one here, because **§3.3 removes the hard part
of [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html)**: JCS's number serialisation (ECMAScript
`Number::toString`, the "Note 2" rounding rule, the `1e+21` threshold) exists to normalise doubles, and a
statement may not contain a double. What remains is seven byte-level traps. No candidate gets all seven from
its standard library.

| # | Trap | What goes wrong silently |
|---|---|---|
| **T1** | Duplicate object keys | Last value wins, no error — in Python, in JS, in Go's v1 decoder, and in `serde_json`'s `Value`. A signature over the canonical form then attests to a document different from the one a human read |
| **T2** | `1` versus `1.0` after parse | The two are different bytes and different statements. A language that collapses them cannot compute `statement_sha256` over what the author wrote (§3) |
| **T3** | Integers beyond 2^53 | `9007199254740993` is a legal JSON number and silently becomes `…992` wherever JSON numbers are doubles |
| **T4** | String escaping | §3.2 pins only the non-ASCII half ("emitted literally"). What a control character must become is unstated — RFC 8785 mandates `\u00XX`, lowercase hex, with `\b\t\n\f\r` as short forms. Two conformant readings, two hashes |
| **T5** | The sort unit for keys | "lexicographically" (§3.2) does not say *over what*. UTF-16 code units (JS, and what JCS mandates) and Unicode code points (Python, Rust, Go, UTF-8 byte order) disagree for characters above U+FFFF |
| **T6** | File-level bytes: BOM, CRLF, trailing newline | Invisible after parsing, fatal to the hash. §3.1 covers the statement; §5 covers the corpus |
| **T7** | Occurrence counting for spans | "occurs exactly once" (§5 rule 4) does not say whether overlapping occurrences count. `"aaa".count("aa")` is **1**; an `indexOf` loop advancing by one returns **2** — one anchors, the other refuses |

T4, T5 and T7 are defects in the spec, not in any language. §3.2 needs two more sentences — the escaping rule for
control characters, and **"sorted by Unicode code point"** with one test vector carrying a key above U+FFFF — and
§5 rule 4 needs to say whether overlapping occurrences count. All three are cheaper to fix in the document than
in two implementations that disagree. T1 is a defect in every standard library, which is why the current
implementation installs `object_pairs_hook` to reject duplicates
([`tools/lexcheck.py`](../tools/lexcheck.py) lines 230–237) rather than trusting `json.loads`.

T2 and T3 are where languages actually differ, and they are measurable on this machine (§8).

---

## §3 Candidate matrix

Legend: **free** = the standard library already behaves as required; **hook** = a documented switch, callback or
type makes it work; **hand** = must be written, and is the interesting part; **no** = cannot be done without
replacing the library.

### §3.1 R1–R7 (identity and boundary)

| | R1 bytes→sha256 | R2 canonical form | R3 no floats | R4 JSON I/O | R5 offline | R6 agent-callable | R7 verdict seal |
|---|---|---|---|---|---|---|---|
| **Rust** | free — `sha2` 0.11.1 | hand — ~100-line writer; sorting free (`BTreeMap`, `str: Ord` = code-point order) | free — `Number` is `i64`/`u64`/`f64`; refuse the `f64` arm | free — `serde_json` 1.0.154 | free at run time; `cargo vendor` for a build | free — single `.exe`, argv + stdin JSON | **free+** — private field, no `pub` constructor; a `pub(crate)` witness is checkable by review |
| **Python** | free — `hashlib.sha256` | hook — `sort_keys`+`separators`+`ensure_ascii=False`+`allow_nan=False`; still hand for duplicate keys and floats | free — `int`/`float` are distinct types (probe P1) | free — `json` | free — stdlib only, nothing to fetch | free — `python -m`, argv + stdin | **no** — no seal exists; an AST scan is a test, not a type |
| **TypeScript** | free — `node:crypto` | **no** — `JSON.parse` erases T2 and T3 (probe J1, J2); a lossless parser must be hand-written first | **no** — same reason; after `JSON.parse` the distinction is gone | free — `JSON` | hook — `node_modules` must be committed or fetched | free — `node`, argv + stdin | hook — `#private` field is real at run time, but structural typing lets a look-alike object satisfy an interface |
| **Go** | free — `crypto/sha256` | hook — map keys sorted (v1, documented); must disable HTML/JS escaping for T4 | hook — `any` decodes to `float64`; `json.Number` must be threaded everywhere or T2 collapses | free — `encoding/json` | free — `go mod vendor` | free — single `.exe` | hook — unexported type in its own package is a real package-level seal |

### §3.2 R8–R12 (operation)

| | R8 tens of MB | R9 Windows | R10 Lean 4 | R11 WASM | R12 stranger re-runs it |
|---|---|---|---|---|---|
| **Rust** | reads bytes, searches without decoding; one 40 MB buffer per corpus | needs **MSVC Build Tools** ([rust-lang.org](https://www.rust-lang.org/tools/install)) — the only install cost in this table | equal: subprocess to `lake` | **free+** — `rustup target add wasm32-wasip1`, Tier 2, ships with rustup ([rustc book](https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html)) | **free+** — one static `.exe`, no runtime, `rust-toolchain.toml` + vendored deps |
| **Python** | decodes to `str`: 1 byte/char ASCII, 2 bytes/char Cyrillic (probe P7), so 40 MB of pinned Russian text is ~80 MB resident | free — already 3.13.11 here | equal | hand — needs CPython-in-WASM (Pyodide); **size and file-access behaviour not checked** `[unverified]` | hook — needs a pinned interpreter *and* the tree; "no network" is satisfiable, "no interpreter" is not |
| **TypeScript** | operates on UTF-16 strings; fine for 40 MB, unmeasured | free — Node v24.14.1 here | equal | **free if the host is JS** — an agent sandbox that runs Node needs no WASM at all | hook — needs Node plus a locked `node_modules` |
| **Go** | reads bytes; fine for 40 MB, unmeasured | free — official installer/zip | equal | hook — `GOOS=js GOARCH=wasm` plus the JS glue `[unverified]` | free — one static `.exe` |

### §3.3 What makes canonicalisation hard in each — the short version

**Rust.** `serde_json` gives two of the three things for free: `Map` is key-ordered unless the `preserve_order`
feature replaces it with an insertion-ordered `indexmap` (the order-preserving methods on `Map` are documented
as feature-gated), and `Number` keeps `i64`/`u64`/`f64` apart, so T2 and T3 are visible. What it does *not*
give is a canonicaliser: `Serializer` is a formatter with knobs, and `Value` cannot report that a document had
duplicate keys. So T1 and T2 still need hand code — the same hand code as everywhere else, which is the honest
comparison.

**Python.** `json.dumps` is not a canonical form; it is a formatter (probe P2 shows `sort_keys` recursing, P3
shows `1.0` surviving as `1.0`, P4 shows `NaN` emitted when `allow_nan` is left on). The four knobs plus one
`object_pairs_hook` are enough — and this is *measured*, not estimated: the canonical core of the existing
checker is 45 lines of source ([lines 268–312](../tools/lexcheck.py)) and the 60-test suite that pins it passes (§8).

**TypeScript.** `JSON.stringify` is a JCS-grade *primitive* serialiser — RFC 8785 is built on it — and
`JSON.parse` is the worst possible *parser* for this spec. On this machine: `JSON.parse("1.0")` and
`JSON.parse("1")` are the same value and both re-serialise as `1`; `JSON.parse("9007199254740993")`
re-serialises as `9007199254740992`. Identity is over the bytes an author signed (§3.4, H20), so a checker that
cannot see the difference between two numbers a statement may contain cannot hash what the author wrote. This is
the single most decisive observation in this document, and it eliminates TypeScript for the *parse* path
regardless of how good its serialiser is. (TS is also the only candidate that reorders integer-like keys —
`{"b":1,"2":2,"1":3}` becomes `{"1":3,"2":2,"b":1}` — which is T5 with teeth.)

**Go.** `encoding/json` v1 sorts map keys (documented) and escapes `<`, `>`, `&`, U+2028 and U+2029 inside
strings by default — T4 — so `SetEscapeHTML(false)` is mandatory, and whether that also stops the U+2028/29
escaping is **not stated on the page I read** `[unverified]`; one test settles it. `Unmarshal` into `any` yields
`float64`, so `json.Number` or `UseNumber()` must be threaded through every layer or T2 and T3 collapse exactly
as in JS. Go 1.25+ also ships `encoding/json/v2`, whose documented defaults differ in the two places that
matter here: maps marshal **non-deterministically** unless `Deterministic` is set, and strings use minimal
escaping — a better starting point, at the cost of a second set of semantics to pin.

---

## §4 The Lean 4 interaction

Lean 4 is not a candidate for the checker. It is the target for H3's theorems, and the seam is one-way (H8).
Four ways to connect, and what each is actually worth:

| Option | Mechanism | Proves | Does not prove | Cost |
|---|---|---|---|---|
| **(a) emit + shell out** | the checker writes a `.lean` file and runs `lake build +Module` (the reference manual states this gives the same guarantees as the blue ticks), then reads the exit status and `#print axioms` | the theorem, about the Lean model of the detector | anything about the Rust code that produced the verdict | 1 unit for the generator, 1 for the harness |
| **(b) JSON-RPC / `lake serve`** | keep a language server alive, stream goals | nothing extra | nothing extra | stateful daemon, protocol churn; only worth it for editor feedback |
| **(c) make Lean the detector** | define the algebra and the detector once in Lean, run it with `lake exe`; the other language becomes an I/O shell | the executed code *is* the proved code — the model↔code gap closes by construction | that the shell hashed the right bytes | moves `checker_version` into the Lean toolchain and makes R5/R12 depend on Lean being installed |
| **(d) no bridge in v1** | nothing | — | — | 0 |

**For v0.2 the honest answer is (a), plus (d) as the default state.** Concretely: the checker gains a
`--lean` flag that writes `lean/LexSpec/Generated/<statement-id>.lean` containing the statement as a Lean
literal and the two theorem statements of H3; CI runs `lake build` and records
`#print axioms` output. Recorded evidence, never a verdict input (H8, H13).

What that buys, precisely: a claim that *if* the model in `lean/LexSpec/Basic.lean` is the algebra in spec §4
and §7, then `findConflicts s = [] → ∀ a b ∈ s, ¬ Conflicts a b` holds — plus a machine-checked list of the
axioms it rests on. The reference manual's grading is the right vocabulary here: the blue double checks are
meaningful *if* one trusts the libraries, `#print axioms` catches `sorryAx` (an incomplete proof or a `sorry`
in a dependency) and custom axioms, `lean4checker --fresh` replays the `.olean` files through the kernel, and
`lake comparator` with external checkers is the gold standard for hostile input. Our generated file is honest
input, not hostile, so the blue ticks plus `#print axioms` is the proportionate level — and the report should
say so rather than implying the stronger one.

What it does not buy, and this must be written next to the theorem: **the proof is about a definitional twin.**
Rust's `findConflicts` and Lean's `findConflicts` are two implementations of one sentence. The gap between them
is closed by a differential test — feed `examples/*.lex.json` to both and compare findings — not by the proof.
That is why H2's kill test (stop if the model needs more than ~400 lines before the first theorem) matters more
than the theorem itself.

Toolchain facts, from the reference manual and from this machine (§8): `lean`, `lake`, `leanc`, `leanmake`,
`leanchecker` ship in a toolchain; `elan` installs toolchains; Lake commands include `lake build`, `lake exe`,
`lake env`, `lake lean`, `lake comparator`. `lake env` and `lake lean` are listed in the manual's table of
contents but I did not open their sections — treat their exact semantics as `[unverified]`. Lean's C FFI exists
(`Run-Time Code §12.4`), so option (c) could later call into a compiled core, but that is a v1 shape and it
collides with R12's "one static artefact".

---

## §5 Recommendation

### §5.1 The choice

**Rust is the primary language for the checker. Python is the runner-up and stays, permanently, as the second
implementation and the lab harness.**

Against R1–R12: R1 free, R2 free-plus-sorting (the hand-written writer is ~100 lines and is the same writer
every candidate needs), R3 free (the type system distinguishes the three number cases and the compiler makes
you handle each), R4 free, R5 free at run time, R6 free (one `.exe`), **R7 the strongest of the four without a
runtime** (private field + no public constructor; the H13 kill test becomes code review of one module instead of
an AST scan of a dynamic language), R8 fine (bytes in memory, no decoding; unmeasured), R9 the only cost (MSVC
Build Tools), R10 equal (subprocess either way), R11 free at Tier 2, R12 free (a single static binary is exactly
what H12's kill test asks a stranger to run).

Python against the same list: R1 free, R2 free-in-practice (measured: 45 lines + 60 tests), **R3 free and
better than Go or TS** (probe P1), R4 free, R5 best-in-class (stdlib only — nothing to download to run it),
R6 free, **R7 the failure** (no seal exists; H13 degrades to a test that a reviewer must trust), R8 fine but
unmeasured, R9 free, R10 equal, R11 expensive, R12 weakest (interpreter + tree).

The decision therefore turns on **R7**, and only on R7 plus R12. R3 eliminated TypeScript but did not choose the
winner: three of four candidates satisfy it.

Why keep Python anyway — the part that is not a consolation prize: §3 makes identity a property of bytes, and
the only real test of a byte-identity claim is a second implementation that was written from the spec and
disagrees loudly when the first one drifts. Charter §6's S2 success criterion is literally "two independent
encoders of the same clause produce statements whose canonical hashes differ but whose verdicts agree". A
Rust checker with a Python twin turns that from a hope into a regression test, and it costs nothing today
because the Python one already exists.

### §5.2 What would overturn it

Each falsifier is cheap, and each names the artefact that settles it.

| # | If this is true | Then |
|---|---|---|
| **F1** | a Rust canonicaliser + strict parser needs **more than 250 lines** before the first golden vector passes | "Rust makes byte-exactness simpler" is false — the same hand code is needed everywhere, and the argument reduces to R7/R12 alone |
| **F2** | H13's seal can be enforced in Python by an AST scan that **fails closed** on the mutation test in H13's kill test | R7 stops favouring Rust; the cost of the seal becomes one test, and Python's R5/R8/R9 advantages win |
| **F3** | H12's replay test passes with `python -m lexcheck` plus a pinned interpreter and the repo | R12 stops favouring Rust; only R7 remains |
| **F4** | the sandbox that will host the checker is **JS-only** | R11's balance tilts to TypeScript, but R3 still disqualifies it for the parse path — the answer would be a Rust core compiled to WASM, not a TS checker |
| **F5** | the owner rules H13 decorative (its own kill test says the split "costs accuracy and buys nothing") | Python wins outright on cost; this document's recommendation is void |

The measurement that would settle F1 is a line count on a real file, not an argument. Performance settles nothing
here: the benchmark named in §8 would show whether any candidate is slow enough at 40 MB to matter, and if one
were, the first fix would be a hash cache keyed by `(path, size, mtime)` — language-independent.

---

## §6 What must be downloaded, exactly

Verified by query or by command in this session; `[unverified]` marks what I did not confirm.

| For | Item | Version / exact form | Source | Status |
|---|---|---|---|---|
| Rust | `rustup-init.exe` (x64) | MSVC ABI | [rust-lang.org/tools/install](https://www.rust-lang.org/tools/install) | verified — the page offers `x86_64-pc-windows-msvc` |
| Rust | Visual Studio C++ Build Tools | "2013 or later", needed on Windows | same page | verified as a requirement |
| Rust | `serde_json` | 1.0.154 (docs.rs build, 11 Oct 2026) | [docs.rs](https://docs.rs/serde_json/latest/serde_json/struct.Map.html) | verified |
| Rust | `sha2` | 0.11.1 (registry, 12 Oct 2026) | crates.io registry query | verified (registry). Whether the 0.11 API matches the 0.10 examples in circulation was **not** checked `[unverified]` — pin what you code against |
| Rust | `unicode-normalization` | 0.1.26 (registry, 16 Oct 2026) | crates.io registry query | verified (registry) — needed only if term comparison normalises (the current checker uses `unicodedata` NFC for comparison, never for the hash) |
| Rust | WASM target | `rustup target add wasm32-wasip1` | [rustc book](https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html) | verified — Tier 2, ships with rustup, no external compiler for the std case |
| Rust | argv parsing | `std::env` (no crate) for v0.2 | — | design choice; `clap` not version-checked `[unverified]` |
| Python | CPython | 3.13.11 already installed | `python --version` | verified on this machine |
| Python | packages | **none** — `json`, `hashlib`, `unicodedata`, `argparse`, `pathlib` | [docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html) | verified |
| TypeScript | Node | v24.14.1 already installed | `node --version` | verified on this machine |
| TypeScript | `typescript`, `@types/node` | version not checked | npm | `[unverified]` |
| TypeScript | JCS canonicaliser | `canonicalize` (npm), named by RFC 8785 Appendix G as a verified-compatible implementation | [RFC 8785 §G](https://www.rfc-editor.org/rfc/rfc8785.html) | verified that the RFC names it; version `[unverified]` |
| Go | toolchain | stdlib docs currently describe `go1.27.3` | [pkg.go.dev/encoding/json](https://pkg.go.dev/encoding/json) | verified as the doc version; the installer itself not opened `[unverified]` |
| Go | NFC | `golang.org/x/text/unicode/norm` | — | name is standard; version `[unverified]` |
| Lean | `elan` + toolchain | Lean 4.36.0-rc1, Lake 5.0.0-src; also installed: v4.30.0, v4.34.1 | `lean --version`, `elan toolchain list` | verified on this machine — **nothing to download to start H3** |
| Lean | packages | none for the model; `@leanprover/Cli` only if the Lean side grows a CLI | [Lake manual](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/) | verified that the manual uses it as the example dependency |

The only *new* download for the recommendation is the first two rows: rustup plus MSVC Build Tools. Everything
else is either already present or a `cargo add`.

---

## §7 Migration cost, stated once

Unit of account: **1 unit = one reviewed change of ≤ 300 lines including its tests, leaving
`tests/run_tests.py` green.** The shape being priced is measured (§8): 1,224 lines of checker, 601 lines of
tests, 60 tests, 6 examples, 1 schema.

| Scenario | Estimate | Confidence |
|---|---|---|
| Keep Python, harden it (v0.2 features on top of what exists) | 10–13 units | medium — the features are new in any language |
| Port v0.1 behaviour to Rust, tests included | 12–16 units | medium — includes re-deriving the 60 tests, which are the real asset |
| Build v0.2 (certificate, policy, freshness, Lean emit) in Rust | +10–14 units | low — no comparable work exists to calibrate against |
| **Switch language after the v0.2 milestone** | **22–30 units, plus one re-run per `lab/` record that quotes a command** | this is the number to avoid |

This is an estimate, not a measurement: the units are anchored on the measured size of the current
implementation, which is the only calibration available. The non-unit cost is worse — every `lab/` record
quoting `python tools/lexcheck.py` stops being reproducible the moment Python is demoted rather than kept (§5.1).

---

## §8 Evidence from this machine

Every row is a command run in this session on the owner's machine; none of it is a benchmark.

| # | Command | Output |
|---|---|---|
| P1 | `json.dumps(1)` then `json.dumps(1.0)` | `1` / `1.0` — the int/float distinction survives |
| P2 | `json.dumps({"b":1,"a":{"d":2,"c":3}}, sort_keys=True, separators=(",",":"))` | `{"a":{"c":3,"d":2},"b":1}` — sorting recurses |
| P3 | `json.loads("1e3")` | `1000.0` — an exponent is a float, so §3.3 refuses it |
| P4 | `json.dumps(float("nan"))` | `NaN` — not JSON; `allow_nan=False` is mandatory |
| P5 | `json.loads('{"x":1,"x":2}')` | `{'x': 2}` — duplicate keys are silent (T1) |
| P6 | `"aaa".count("aa")` | `1` — non-overlapping (T7) |
| P7 | `sys.getsizeof("a"*1000)`, `sys.getsizeof("й"*1000)` | `1049` vs `2049` — 1 byte/char ASCII, 2 bytes/char Cyrillic |
| J1 | `JSON.stringify(JSON.parse("1.0"))` | `1` — T2 lost at parse |
| J2 | `JSON.stringify(JSON.parse("9007199254740993"))` | `9007199254740992` — T3 lost at parse |
| J3 | `JSON.stringify({b:1,"2":2,"1":3,a:4})` | `{"1":3,"2":2,"b":1,"a":4}` — integer-like keys hoisted |
| J4 | `JSON.stringify("\u2028").length`, `JSON.stringify("й")` | `3` (quote + U+2028 + quote) and `"й"` — non-ASCII literal, so TS satisfies T4 |
| J5 | `node -e "require('node:crypto')…"` | works, sha256("abc") = `ba7816bf…` — no install needed |
| — | `python -B tests/run_tests.py` | `Ran 60 tests … OK` (20.0 s) |
| — | `(Get-Item corpus/gk-rf-2026-10-01.txt).Length` | **1,737 bytes** — the pinned corpus is three orders of magnitude short of R8 |
| — | `lean --version`, `lake --version`, `elan toolchain list` | `4.36.0-rc1`, `5.0.0-src`, three toolchains |
| — | `python --version`, `node --version` | `3.13.11`, `v24.14.1`; **no `cargo`, no `go` on PATH** |

The corpus line matters for the recommendation in a way that is easy to miss: R8 is currently satisfied by
nothing, because there is nothing to satisfy. The benchmark that would settle it is one file —
`tools/bench_anchor.py <corpus> <spans.json>`: pin 40 MB of real text, 200 spans, cold process, report wall time
and peak RSS for (a) the sha256 of the corpus and (b) the occurrence count of every span. Write it before any
R8 claim, and report both implementations.

---

## §9 What this document does not claim

- **Not a benchmark.** No candidate was built here; three are not installed. Every performance sentence is
  either removed or replaced by the benchmark named in §8.
- **Not a statement about law, or about the product's correctness.** It is a statement about which language
  makes the spec's byte-level identity and H13's seal cheapest to keep true.
- **Not a decision.** `lab/decisions/` holds decisions; this is the input to one. Adopting it also requires a
  row in README.md's "Read first" table and in the spec's reading order, which this file does not edit.
- **Not complete.** T5 is an unresolved defect in spec §3.2 that has to be fixed before two implementations can
  be compared at all; the WASM requirement R11 is conditional and its two non-Rust rows are `[unverified]`.

---

## Sources

| url | what it is | verified |
|---|---|---|
| https://www.rfc-editor.org/rfc/rfc8785.html | RFC 8785, *JSON Canonicalization Scheme*, June 2020 — §3.2.2.2 string escaping, §3.2.2.3 numbers, §3.2.3 UTF-16 code-unit sort order and its explicit note that UTF-8 sorting differs, Appendix D big numbers, Appendix G open-source implementations | yes |
| https://docs.rs/serde_json/latest/serde_json/struct.Map.html | `serde_json::Map` API reference, crate 1.0.154 (11 Oct 2026); order-preserving methods documented as available on the `preserve_order` feature only | yes |
| https://docs.rs/crate/serde_json/latest/features | `serde_json` feature list: `preserve_order` depends on `indexmap` + `foldhash`; also `arbitrary_precision`, `float_roundtrip`, `raw_value`, `unbounded_depth` | yes |
| https://docs.python.org/3/library/json.html | Python 3.15 `json` docs — `sort_keys`, `separators`, `ensure_ascii`, `allow_nan`, `object_pairs_hook`, `parse_float`/`parse_int`, the int→int / real→float table, duplicate-name behaviour, "does not impose limits beyond Python datatypes" | yes |
| https://pkg.go.dev/encoding/json | Go `encoding/json` docs, go1.27.3 — "The map keys are sorted and used as JSON object keys", default HTML/JS escaping of `<`, `>`, `&`, U+2028, U+2029, `UseNumber`, and the v1↔v2 difference list (v2 maps non-deterministic unless `Deterministic`) | yes |
| https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify | MDN `JSON.stringify` — property order follows `Object.keys`, `NaN`/`Infinity` → `null`, `undefined` dropped, lone surrogates escaped | yes |
| https://lean-lang.org/doc/reference/latest/ | *The Lean Language Reference*, covering Lean 4.36.0-rc2 — table of contents, kernel description | yes |
| https://lean-lang.org/doc/reference/latest/ValidatingProofs/ | "Validating a Lean Proof" — blue ticks, `#print axioms` and the three benign axioms (`propext`, `Classical.choice`, `Quot.sound`) plus `sorryAx`, `lean4checker --fresh`, `lake comparator`, `Lean.trustCompiler` history | yes |
| https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/ | toolchain contents: `lean`, `lake`, `leanc`, `leanmake`, `leanchecker`; `elan` as the toolchain manager | yes |
| https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/ | Lake manual — workspace layout, `lake build`/`exe`/`env`/`lean`/`comparator` in the TOC, manifests, offline package overrides | yes (TOC and concepts read; `lake env` / `lake lean` sections **not** opened) |
| https://lean-lang.org/doc/reference/latest/Interacting-with-Lean/ | `#eval`, `#print axioms`, `#guard_msgs`; the message log; `#eval` refuses terms depending on `sorry` | yes |
| https://lean-lang.org/doc/reference/latest/Run-Time-Code/ | Lean runtime: reference counting, tasks/threads, C FFI (§12.4) | yes |
| https://www.rust-lang.org/tools/install | Rust install — `rustup-init.exe` for `x86_64-pc-windows-msvc`, MSVC Build Tools requirement, 6-week release cadence, cross-compilation targets | yes |
| https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html | `wasm32-wasip1` is Tier 2, `rustup target add wasm32-wasip1`, self-contained sysroot, renamed from `wasm32-wasi` in March 2024 | yes |
| https://crates.io/crates/sha2 | `sha2` 0.11.1, published 2026-10-12 (via registry query, not the HTML page) | yes (registry) |
| https://crates.io/crates/unicode-normalization | `unicode-normalization` 0.1.26, published 2026-10-16 (via registry query) | yes (registry) |
| — | a web search for Lean CLI documentation that returned unrelated Chinese-language pages and no Lean material | no — nothing in this document rests on it |

Internal references (not sources): [`docs/10-SPEC-v0.1.md`](10-SPEC-v0.1.md), [`docs/06-FROM-TEXT-TO-PROOF.md`](06-FROM-TEXT-TO-PROOF.md),
[`docs/00-CHARTER.md`](00-CHARTER.md), [`AGENTS.md`](../AGENTS.md), [`tools/lexcheck.py`](../tools/lexcheck.py),
[`lab/2026-10-28-checkout-line-endings.md`](../lab/2026-10-28-checkout-line-endings.md).
