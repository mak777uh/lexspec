"""check-audit-freshness.py — a review must name a snapshot that was current when it was written.

Written after the correction of 2026-10-29: a review of another repository was taken from a local clone a month old,
both findings turned out to be already fixed upstream, and the author spent an evening answering a defect that no
longer existed. The cost of a stale snapshot is borne by the person reviewed, not by the reviewer, which is why this
is a rule and a tool rather than a resolution to be careful.

Usage, before publishing a review:
    python lab/check-audit-freshness.py mak777uh/- 9cbdcf2
    python lab/check-audit-freshness.py mak777uh/VecDHT f30786f --max-age-days 2

Exit: 0 the snapshot is recent enough, 1 it is older than the limit, 2 the snapshot could not be resolved.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request


def commit_date(repo: str, sha: str) -> dt.datetime:
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    req = urllib.request.Request(url, headers={"User-Agent": "dsh", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as f:
        data = json.load(f)
    stamp = data["commit"]["author"]["date"]
    return dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Refuse a review whose snapshot is stale.")
    ap.add_argument("repo", help="owner/name, e.g. mak777uh/VecDHT")
    ap.add_argument("sha", help="the commit the review names as its subject")
    ap.add_argument("--max-age-days", type=int, default=3, help="how old a snapshot may be (default 3)")
    args = ap.parse_args(argv)

    try:
        when = commit_date(args.repo, args.sha)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print(f"check-audit-freshness: {args.sha} does not exist in {args.repo}", file=sys.stderr)
            return 2
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"check-audit-freshness: cannot resolve the commit: {exc}", file=sys.stderr)
        return 2

    age = (dt.datetime.now(dt.timezone.utc) - when).days
    verdict = "ok" if age <= args.max_age_days else "STALE"
    print(f"{verdict}: {args.repo}@{args.sha[:7]} is {age} day(s) old (limit {args.max_age_days}); committed {when.isoformat()}")
    if age > args.max_age_days:
        print(
            "  A review taken from a snapshot this old describes a tree that no longer exists; re-clone from the\n"
            "  default branch before writing, and name the date as well as the hash in the note's first line.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
