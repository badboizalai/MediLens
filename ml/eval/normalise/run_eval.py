"""Top-1 LOINC accuracy of to_loinc on the synthetic set (D62).

Rows with an empty `gold` must be refused (None). Positives = rows with a gold code.
Usage: python ml/eval/normalise/run_eval.py [--out ml/eval/normalise/REPORT.md]
A hand-written "## Notes" section already in the report is kept on re-run.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "worker" / "src"))

from medilens_worker.normalise import to_loinc  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE / "synthetic_labs.csv"
TARGET = 0.85


def evaluate():
    rows = []
    for r in csv.DictReader(DATA.open(encoding="utf-8", newline="")):
        m = to_loinc(r["text"], r["unit"] or None)
        got = m.code if m else ""
        if r["gold"] and got == r["gold"]:
            cls = "correct"
        elif r["gold"] and not got:
            cls = "missed (abstained)"
        elif r["gold"]:
            cls = "wrong code"
        elif got:
            cls = "false accept (should refuse)"
        else:
            cls = "correct refusal"
        rows.append((r["text"], r["unit"], r["gold"], got, cls))
    return rows


def report(rows) -> str:
    pos = [r for r in rows if r[2]]
    neg = [r for r in rows if not r[2]]
    ok = sum(r[4] == "correct" for r in pos)
    answered = [r for r in pos if r[3]]
    cls = Counter(r[4] for r in rows)
    errs = [r for r in rows if r[4] not in ("correct", "correct refusal")]
    acc = ok / len(pos)
    out = [
        "# Normaliser eval (S7-T62, D62)",
        "",
        "`to_loinc` on `ml/eval/normalise/synthetic_labs.csv` (own-authored synthetic strings; "
        "VI/EN names, values and units in text or separate, typos, and strings that must be refused). "
        "ICD-10 is not evaluated: LIC-002 is not approved and no ICD-10 code is loaded.",
        "",
        f"- Strings: **{len(rows)}** ({len(pos)} with a gold LOINC code, {len(neg)} that must be refused)",
        f"- **Top-1 code accuracy: {acc:.3f}** ({ok}/{len(pos)}), target >= {TARGET} -> "
        + ("PASS" if acc >= TARGET else "FAIL"),
        f"- Precision when answered: {ok / len(answered):.3f} ({ok}/{len(answered)})"
        if answered
        else "- Precision when answered: n/a",
        f"- Refusal accuracy on negatives: {cls['correct refusal']}/{len(neg)}",
        "- Outcomes: " + ", ".join(f"{k} {n}" for k, n in sorted(cls.items())),
    ]
    if errs:
        out += [
            "",
            "## Errors",
            "",
            "| text | unit | gold | got | class |",
            "|---|---|---|---|---|",
        ]
        out += [f"| {t} | {u} | {g} | {o} | {c} |" for t, u, g, o, c in errs]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "REPORT.md")
    args = ap.parse_args()
    notes = ""
    if args.out.exists() and "\n## Notes" in (old := args.out.read_text("utf-8")):
        notes = old[old.index("\n## Notes") :]
    text = report(evaluate())
    args.out.write_text(text + notes, "utf-8")
    print(text)
