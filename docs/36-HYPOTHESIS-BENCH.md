# 36 — The bench: pre-registration, falsifiers, and expiring forecasts

The owner pointed at `-` (morphogenesis) and said it is a scientific bench for logging and testing hypotheses, and
that the same approach belongs in this work. He is right, and the missing piece was specific: we had measurements
(`lab/experiments.jsonl`), principles with falsifiers (`docs/29`), and no **pre-registration** — nothing that stopped
us from deciding after the fact what an experiment had been about.

That is not a moral failing, it is a design gap. A result recorded without a prediction is a number; a result recorded
against a prediction is evidence.

---

## §1 What the bench is now

| file | one line per | written |
|---|---|---|
| `lab/hypotheses.jsonl` | hypothesis: claim, **falsifier**, principles, status | before or after the test, dated |
| `lab/preregistrations.jsonl` | prediction, **digest of the file it is about**, date | **before** the run |
| `lab/experiments.jsonl` | what was measured | after the run, may name a pre-registration |

Three rules, each taken from a repository that already runs one (`morphogenesis` writes a `PRE-REG` journal event
before the run; `VecDHT` keeps `H-*` and `E-*` cards; `flowguard` makes a stale allowance a finding):

1. **No result without an origin.** An experiment row either names a pre-registration or declares itself
   `origin: exploratory`. Three rows predate the rule and are grandfathered **by name**, so the exception cannot grow
   silently.
2. **A frozen prediction cannot be re-pointed.** The pre-registration carries the sha256 of the file it is about; if
   that file changes, the prediction was about a different document and the check says so. Proven by changing one byte
   of `examples/12`: `SNAPSHOT_DRIFT`, exit 1.
3. **An open forecast expires.** A pre-registration older than the grace period with no closed hypothesis is a finding
   — an open forecast nobody closes is how a bench becomes a diary.

## §2 What was pre-registered, and what happened

| id | claim | prediction frozen before the run | outcome |
|---|---|---|---|
| **H-0001** | sentence-by-sentence encoding yields ≥1.5× the atoms of intuitive encoding, and coverage lower by ≥0.1 | ГК 395: 10 vs 6 atoms, coverage 0.900 vs 0.833, **delta 0.067 → the delta part fails** | **refuted**, and honestly: the atom-count part held (1.67×), the coverage-gap part did not. This is exactly the prediction a hindsight narrative would have quietly restated as 0.05. |
| **H-0002** | genuine ambiguity exists only below 40 normalised characters | — | **supported**, with a caveat that is the point: the measurement (585 long spans, 0 ambiguous; 604 short, 11 ambiguous) was taken **before** this registration. It is a post-hoc confirmation and is recorded as such, not as a pre-registered test. |
| **H-0003** | a guard without a planted-defect mode is found by an external reader within two rounds | catalogue guard: five of eight had no such mode | **open** — the forecast is live and will expire on its own if nobody closes it. |

H-0001 is the useful one. Without pre-registration, "coverage dropped from 0.833 to 0.900" reads as a success; with the
prediction frozen, the number that mattered (the gap between them) turned out to be half of what was predicted and the
honest status is *refuted*.

## §3 What this changes about `docs/29`

The principles register had falsifiers but no ids and no clock. Each principle that gets tested now gets a hypothesis
id, and the row in `lab/experiments.jsonl` names it. The register stays the prose, the bench becomes the record — the
same split the family uses between a card and a run.

## §4 Boundary

The bench checks the *form* of the discipline: origin declared, snapshot intact, forecast closed. It cannot check
whether the pre-registration was written before the run — only the dates and the digest can suggest it, and a
determined author can still lie about the order. That limitation is stated here rather than papered over: what
pre-registration buys is that lying now requires a deliberate act with a timestamp, not an accident of memory.
