#!/usr/bin/env python3
"""Prepend an entry to assets/activity.json (the homepage activity feed).

Usage:
    python3 scripts/log-activity.py SOURCE "Title text" [URL]

Examples:
    python3 scripts/log-activity.py CLAUDE "arxiv-weekly · 14 papers · world models, RL theory, sparse training"
    python3 scripts/log-activity.py PROJECT "topoadamw · v0.2 · GUDHI 4.0 support" "https://github.com/SVAH-X/topoadamw/releases/v0.2"

SOURCE controls the colored pill shown on the homepage. Recognized values
(case-insensitive, normalized to upper): CLAUDE, GITHUB, ARXIV, HACKATHON,
SITE, PROJECT. Anything else falls back to a neutral gray pill.

The entry's date defaults to today (UTC). Override with --date YYYY-MM-DD.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIVITY = REPO_ROOT / "assets" / "activity.json"
MAX_ENTRIES = 50


def main() -> int:
    p = argparse.ArgumentParser(description="Prepend an entry to the homepage activity feed.")
    p.add_argument("source", help="Source pill (CLAUDE | GITHUB | ARXIV | HACKATHON | SITE | PROJECT | other)")
    p.add_argument("title", help="Title text shown after the source pill")
    p.add_argument("url", nargs="?", default="", help="Optional URL for the ↗ link")
    p.add_argument("--date", default=None, help="ISO date (YYYY-MM-DD); defaults to today UTC")
    args = p.parse_args()

    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = {
        "date": date,
        "source": args.source.upper(),
        "title": args.title,
        "url": args.url,
    }

    if ACTIVITY.exists():
        with ACTIVITY.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"error: {ACTIVITY} root is not a list", file=sys.stderr)
            return 1
    else:
        data = []

    # Skip exact duplicates posted within the same day to make the routine idempotent.
    if any(e.get("date") == entry["date"] and e.get("title") == entry["title"] for e in data):
        print(f"skip: identical entry already present for {entry['date']}")
        return 0

    data.insert(0, entry)
    data = data[:MAX_ENTRIES]

    with ACTIVITY.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"prepended: {entry}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
