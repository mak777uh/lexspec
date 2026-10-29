# cross-audit — the exchange

This folder is the landing place for reviews of **this** repository written by the other projects in the family
(`-`, `VecDHT`, `flowguard-spec`, `harness`). It exists because an audit that everyone runs and nobody records is
just a conversation.

## What is in here

| file | what it is |
|---|---|
| `2026-10-29-lexspec-reviews-<repo>.md` in **their** repositories | our audit of that repository — one file per repository, in a `cross-audit/` folder there |
| `reviews/` (this folder) | their audits of us, kept verbatim, one file per reviewer, never edited |

## The rules we audit by, and ask to be audited by

1. **A finding without a reproducing command is not a finding.** Every row carries a command that can be run from
   the repository root.
2. **Say what you did not check.** A review's boundary is part of the review; without it, silence reads as approval.
3. **Severity is about consequence, not about effort.** `HIGH` means a claim the repository makes can be false while
   its checks are green.
4. **Nothing is fixed silently in someone else's repository.** The note is the only file we write there.
5. **A green guard that cannot go red is decoration**, and a guard that measures a different quantity than the claim
   is worse than none: it converts an unknown into a false confidence.

## Our own record as reviewers

- 2026-10-29 — `flowguard-spec`: the review we received from them found a real defect (F-3-1, the verdict depended
  on the repository marker) and a decorative threshold. Their finding is recorded in
  [`docs/30`](../docs/30-REPO-WALK.md) §1 and fixed in [`ADR-0010`](../lab/decisions/ADR-0010-threshold-is-reporting.md).
  That is the standard we hold these notes to: find something that is actually wrong, or say plainly that we did not.

6. **A review must not cite a path that exists only in the reviewer's tree.** Learned the hard way on
   2026-10-29: every note we wrote ended with a sentence naming `docs/30-REPO-WALK.md` — a file of ours, not
   of the repository being reviewed. `VecDHT`'s reference guard read it as a dangling reference and its CI
   went red from the moment our note landed (`472a0f6`). They fixed it by adding `cross-audit/` to
   `EXTERNAL_DIRS` without touching our text. If a sentence refers to our own repository, say so in words
   and do not write it as a path.

7. **A review is written against the default branch as it is at review time, and its first line names
   the date as well as the hash.** Learned the same day: our audit of `-` was taken from a clone 37 days old,
   both findings were already fixed upstream, and the cost fell on the author who answered them. Check with
   `python lab/check-audit-freshness.py <owner/name> <sha>` before publishing; a stale snapshot is a false
   statement about someone else's tree, not a minor inaccuracy.

8. **Review texts are foreign text, never evidence.** A file under `cross-audit/` may carry numbers and claims
   of its own; nothing in this repository may cite them as a checked fact. Their presence is why
   `cross-audit/README.md` alone is in the prose guard's living list and the review files are not.
