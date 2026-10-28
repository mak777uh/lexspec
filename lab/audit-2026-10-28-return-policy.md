# Audit 2026-10-28 — a return policy against the anchored norm

This is the first run of the **code → law** direction ([`docs/18`](../docs/18-CLOSED-LOOP.md) pair 2/3, [`docs/19`](../docs/19-PORTFOLIO.md) §3).
It is done by hand, on an illustrative policy, and it is labelled as such. What it demonstrates is the *finding
shape*, not a real company's compliance.

**The norm, anchored and machine-checked:** Закон РФ «О защите прав потребителей», ст. 26.1 п. 4 —
statement [`examples/09-zozpp-26-1.lex.json`](../examples/09-zozpp-26-1.lex.json) `9b184183…`, corpus
[`corpus/zozpp-26-1-2026-10-28.txt`](../corpus/zozpp-26-1-2026-10-28.txt) `3b403229…`, verdict `CHECKED`,
coverage 0.250, 4 of 4 atoms anchored, 3 declared escapes.

**The code under audit** — an illustrative Rego policy of the kind that ships in most storefronts:

```rego
package returns

default allow_refund := false

allow_refund if {
    input.order.delivered_days_ago <= 30          # the "30-day returns" promise
    input.item.custom_made == false
}

refund_deadline_days := 30                         # seller pays within 30 days of the demand
```

## Finding 1 — divergence on a deadline, and it is the expensive kind

The policy promises to *pay within 30 days* of the demand. The anchored norm says: «не позднее чем через
десять дней со дня предъявления потребителем соответствующего требования» — ten days, at the span
`не позднее чем через десять дней со дня предъявления потребителем соответствующего требования`
(`a4` in the statement, unclosed for exactly this reason: the deadline is a quantity in time).

**Class:** the code permits a delay the norm forbids. Not a wording difference — a 20-day window in which the
seller is in breach while the software reports the refund as "processing normally".

## Finding 2 — a missing branch, where the law's branch exists because the seller failed

The policy has one path: `delivered_days_ago <= 30`. The norm has a second: if the return information was not
provided in writing at delivery, the consumer has **three months**, not seven days.

**Class:** the code is silent where the law is explicit, and the silent case is the one the seller caused. A
storefront with this policy shortens the consumer's right precisely when it should be longest. The fix is a
branch, not a constant.

## Finding 3 — an open term smuggled in as a boolean

The policy tests `input.item.custom_made == false`. The norm's predicate is «товар … имеющего
индивидуально-определенные свойства, если указанный товар может быть использован исключительно приобретающим
его потребителем» — a narrower and contested test. A boolean named `custom_made` is not that predicate; whoever
sets the flag decides the scope of the norm.

**Class:** an escape, not a violation. It is recorded as `OPEN_TERM` on `a3`'s neighbour and it belongs in the
report as "the code's predicate is not the norm's predicate", because the day someone sets the flag for
"engraved" goods, the code will refuse a return the norm allows.

## What this run shows about the tool, honestly

**The audit is not automated.** Everything above was produced by reading three files and running one checker.
The automated version needs an extraction step: from the code, propose candidate assumptions (a number, a
branch, a predicate) with the line that carries them; from the norm, the anchored atoms; then compare. That
step is the missing capability — and this run defines its output shape:

```
finding | class            | where in the code              | where in the norm (anchor)      | what is wrong
1       | divergence       | refund_deadline_days := 30     | a4 span «десять дней»           | deadline too long by 20 days
2       | gap              | allow_refund (single branch)   | a2 span «в течение трех месяцев» | mandated branch absent
3       | open predicate   | input.item.custom_made         | a3 span «индивидуально-определенные» | code predicate ≠ norm predicate
```

**A footnote that is itself a finding.** Writing the statement with Python on Windows produced CRLF line
endings, and `C0_CANON` refused the file: *"file contains CRLF line endings (spec §3.1: LF only)"*. The tool
caught its own author, in the same session, on the exact trap the canonical form exists for. That is the system
working, and it is also a reminder that the encoding path must not depend on a language's default in text mode.

## What this changes

Per charter C7 an edge either moves or it does not. **The code → law edge has moved from "not built" to
"demonstrated by hand, not automated"** — three findings, one output shape, one missing capability named. The
next step is the extraction step, and it should be prototyped on this same policy so the comparison is
reproducible.
