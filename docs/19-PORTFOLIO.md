# 19 — One system: five repositories, and the bridge between law and code

Status: **portfolio map, not spec.** Written after the owner's statement that the pinned repositories are one
system, that this repository is the part which tests the others for consistency, and that its place is the bridge
between law, software, and the people who check both through VecDHT.

The purpose of this document is to make that claim checkable: what each repository actually provides to the
others, what the interface is, and — for each edge in the graph — what would have to exist for the edge to be
real rather than rhetorical.

---

## §1 The portfolio as it stands today (verified from GitHub, 2026-10-28)

| Repository | What it is | The property it owns |
|---|---|---|
| [`mak777uh/-`](https://github.com/mak777uh/-) | morphogenesis lab bench: code, protocols, run manifests, generated counts | **the discipline of the bench**: every number carries the command that produced it |
| [`mak777uh/VecDHT`](https://github.com/mak777uh/VecDHT) | peer-to-peer semantic rendezvous: signed intents, content-addressed records, no central catalogue | **distribution without a chokepoint**: a served record can be shown, and a third party can check it |
| [`mak777uh/flowguard-spec`](https://github.com/mak777uh/flowguard-spec) | prove a control boundary in the Postgres write path; bundle verifier with two external anchors | **the proof of a boundary**: not "secure", but "inside this closure no value passes the single control point" |
| [`mak777uh/cases`](https://github.com/mak777uh/cases) | public record of verification work: evidence, verdict, reproduction | **the public record**, including "not confirmed" |
| [`mak777uh/lexspec`](https://github.com/mak777uh/lexspec) | this repository: legal statements anchored to pinned text, checked, and compiled toward an enforced boundary | **the anchor between law and code**: a verdict that is relative to text, and a chain a stranger can walk back |

The portfolio has one shared rule, stated differently in each repository and identical in substance: **an artifact
a stranger cannot re-check is a claim, and claims are not results.**

---

## §2 The graph, edge by edge

```
                       ┌────────────────────────────┐
                       │  legal text (pinned)       │
                       └────────────┬───────────────┘
                                    │ anchor: span + revision + digest
                                    ▼
   ┌───────────────┐        ┌───────────────┐        ┌────────────────┐
   │ flowguard-spec│◄──────►│   lexspec     │◄──────►│     VecDHT     │
   │ proof of the  │  seam  │ anchored      │ intent │ discovery      │
   │ boundary      │        │ statement     │        │ without centre │
   └───────┬───────┘        └───────┬───────┘        └───────┬────────┘
           │                        │                        │
           │        ┌───────────────▼───────────┐            │
           └───────►│ decisions, certificates   │◄───────────┘
                    │ found and checked by      │
                    │ people, peer to peer      │
                    └───────────────┬───────────┘
                                    ▼
                            ┌───────────────┐
                            │     cases     │  the public record of what held
                            └───────────────┘
```

| Edge | What has to be true | Today |
|---|---|---|
| **text → lexspec** | a span resolves uniquely in a pinned revision, or the statement is refused | **built**; measured twice (GDPR Art. 17, ГК 395) |
| **lexspec → flowguard** | a normative constraint can bind to the same closure without weakening the proof | **asked** in interop note 1; the seam question is open |
| **flowguard → lexspec** | their verifier's byte-level binding is describable well enough for us to copy the shape | **asked**, unanswered |
| **lexspec → VecDHT** | a statement's identity (canonical hash + certificate hash) can be published as a signed intent, found by meaning, and re-checked by a stranger | **not built**; note 1 to VecDHT asks exactly this |
| **VecDHT → lexspec** | a discovered intent can be verified against its publisher's anchored statement without the publisher being online | **not built** |
| **any → cases** | a result worth recording becomes a case with evidence and a verdict | manual today |
| **any → `-`** | the bench rule (numbers carry commands) applies to every number we print | **held** by `tools/lexspec_status.py` and `tools/SELFTEST.md` |

**Read the table as the work plan.** Three edges are built or asked; four are not, and each of the four is a
concrete artifact rather than a hope.

---

## §3 What "bridge" means here, precisely

Not a metaphor and not a job title. The bridge is the **conversion in both directions**, and each direction has an
artifact:

**Law → code.** A clause becomes positions with spans, then quantities and flows, then rules carrying their atom
ids, then decisions with the anchor hash in the record. At every step the reference survives; at the end, a
decision cites the words that authorised it. This direction is specified in [`docs/14`](14-ARCHITECTURE.md) and
half-measured: two real articles attempted, one at 75 % coverage, one at 50 % — and the missing half is exactly
the three unbuilt layers.

**Code → law.** The harder direction, and the one nobody in the portfolio does yet: take code that already runs,
extract what it *assumes* about obligations, deadlines, amounts and permissions, and check those assumptions
against anchored text. Where the code assumes something the law does not say, that is a finding — the same class
of finding as a flowguard violation, discovered from the other end.

The second direction is what makes the system closed rather than illustrative: without it, we can only check
encodings we wrote ourselves, which is paper checking paper ([`docs/18`](18-CLOSED-LOOP.md) §4).

---

## §4 Where VecDHT carries it

VecDHT's own pitch says the important sentence for us: *records are content-addressed, so a node can show which
records it was served and a third party can check the claim.* Applied to legal statements, that means:

- a **statement intent** = short human text + embedding + the canonical statement hash + the certificate hash +
  the anchor digests, signed by the publisher;
- discovery is by meaning, so a person looking for "who says what about interest on late payment in Russia" finds
  the statements rather than a vendor's homepage;
- verification does not need the publisher: the record is content-addressed, so a stranger can re-check the
  certificate against the pinned corpus and refuse it;
- **no operator decides what is discoverable**, which is precisely the property a legal claim needs if its value
  is that nobody can quietly delist it.

The honest limit: VecDHT today has no release tag, no published binary, no two-machine pilot
(its own `PITCH.en.md`). So the bridge to it is designed against a specification and a single-host stand, not
against a network. That must be said in any product description, and it is said in our interop note.

---

## §5 The people at the end of the chain

The owner's phrase — *the endpoint on earth is the people who control the quality of their own legal and digital
environment* — has a technical consequence: the artifacts must be usable **by a person who does not trust us and
does not have our toolchain**. That means:

- the certificate must be re-checkable offline with a documented procedure, not by running our code;
- the statement must be readable by a lawyer without a manual (charter falsifier F1);
- the refusal must tell a reader what to do next (F4);
- and the residue — what was not modelled — must be on the same page as the verdict, not in an appendix.

Everything in this portfolio is, in the end, addressed to that person: `cases` gives them a record, `flowguard`
gives them a boundary, `VecDHT` gives them discovery without a gatekeeper, `-` gives them a bench discipline, and
this repository gives them the link between the words and the behaviour.

---

## §6 The common invariant, and what "movement" means

The owner's formulation — all repositories serve the establishment of truth, more precisely a continuous
movement toward it — becomes checkable when stated as an **operator** applied five times, and a **metric**.

The operator, identical in each repository: **replace an assertion by its check, then name what the check does
not cover.** Every repository is one instance of it:

| Repository | The opinion it replaced | The check that replaced it | The residue it names |
|---|---|---|---|
| `-` | "this number is what happened" | the number is generated by a script from run manifests | runs whose manifest is incomplete |
| `flowguard-spec` | "the system is secure" | inside a declared closure, no value passes the single control point — with a verifier and two external anchors | everything outside the closure, stated in the artifact |
| `VecDHT` | "the catalogue showed you this" | content-addressed records: a node shows what it served, a stranger re-checks | what the network cannot prove about a publisher staying online |
| `cases` | "we did good work" | a case with evidence, a verdict, and the commands to reproduce | verdicts that came back "not confirmed" |
| `lexspec` | "the clause says X" | an anchored position, coverage, and refusal codes | escapes: the part of the clause not modelled |

The metric, which is the only honest meaning of "movement":

> **The fraction of our claims that is opinion goes down, and the fraction that is residue goes up** — because
> residue is opinion that has been located, named and bounded.

That is measurable per repository, and it is the opposite of the usual research metric: a project that produces
more assertions and fewer named residues is moving *away*, however impressive its output. Concretely, for this
repository: coverage up, escapes down **and declared**, divergence zero, rounds to stability finite
([`docs/18`](18-CLOSED-LOOP.md) §2). For the portfolio: the number of built edges in §2, which is currently
three of seven.

**Three things that would mean it is not movement**, and each is cheap to check:

1. **Documents grow while edges stay unbuilt.** If a month from now §2 still shows three edges, everything added
   in between was commentary.
2. **Residue does not shrink.** If the same escapes with the same reasons reappear after the layer that was
   supposed to absorb them, the layer did not work — and the honest response is to delete the claim, not to
   rename the residue.
3. **Agreement is treated as evidence.** Five models agreeing is the failure mode we already caught once
   (`lawlib`); it cannot re-enter as a metric just because it is cheap to count.

**What "truth" means here, stated narrowly so it cannot be inflated:** truth-aptness *relative to declared
artifacts* — a span that either resolves or does not, a digest that either matches or does not, a decision that
either walks back to bytes or does not. The movement is a shrinking of the unverifiable surface. It is not a
claim that the sum of our artifacts approaches the truth about law, and this repository must never say that.

---

## §7 What would make this description false

1. **If the code → law direction cannot be built without rewriting the code**, the bridge is one-way and the
   system is illustrative, not closed.
2. **If a statement cannot be published and re-checked without our tooling**, then VecDHT carries a promise
   nobody can verify, and the "no chokepoint" property becomes a chokepoint held by us.
3. **If the four unbuilt edges stay unbuilt while the documents grow**, this repository becomes a well-argued
   essay with tests for its own parser — which is the exact failure mode the owner's other projects are built to
   avoid.
