#!/usr/bin/env python3
"""Check BR -> US -> TC traceability.

Usage:
    python check_traceability.py <traceability-matrix.csv> <business-rules.md>

The rules file is scanned for codes like BR-012. The matrix must have
columns br_id, us_id, tc_id, status. Prints rules with no story, rules with
no test, and tests that failed. Exit code 1 if any MUST gap is found.
"""

import csv
import re
import sys
from collections import defaultdict


def load_rules(path: str) -> list[str]:
    text = open(path, encoding="utf-8").read()
    return sorted(set(re.findall(r"\bBR-\d{3}\b", text)))


def load_matrix(path: str):
    stories, tests, failed = defaultdict(set), defaultdict(set), []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            br = (row.get("br_id") or "").strip()
            us = (row.get("us_id") or "").strip()
            tc = (row.get("tc_id") or "").strip()
            status = (row.get("status") or "").strip().lower()
            if not br:
                continue
            if us:
                stories[br].add(us)
            if tc:
                tests[br].add(tc)
            if status == "failed":
                failed.append((br, us, tc))
    return stories, tests, failed


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    rules = load_rules(sys.argv[2])
    stories, tests, failed = load_matrix(sys.argv[1])
    no_story = [r for r in rules if not stories.get(r)]
    no_test = [r for r in rules if not tests.get(r)]

    print(f"Rules found: {len(rules)}")
    print(f"Rules without story ({len(no_story)}): {', '.join(no_story) or '-'}")
    print(f"Rules without test  ({len(no_test)}): {', '.join(no_test) or '-'}")
    print(f"Failed tests ({len(failed)}):")
    for br, us, tc in failed:
        print(f"  {br} / {us or '-'} / {tc or '-'}")
    coverage = 100 * (len(rules) - len(no_test)) / len(rules) if rules else 100
    print(f"Test coverage of rules: {coverage:.1f}%")
    return 1 if (no_story or no_test or failed) else 0


if __name__ == "__main__":
    sys.exit(main())
