#!/usr/bin/env python3
"""Evaluate MediLens extraction output against a golden set.

Usage:
    python eval_extraction.py --gold gold.jsonl --pred pred.jsonl [--out report.md] [--fuzzy 0.9]
    python eval_extraction.py --cer --gold gold_lines.jsonl --pred pred_lines.jsonl

Field mode: each JSONL line is {"doc_id", "unit", "quality"?, "fields": {...}}.
Nested dicts/lists are flattened to (path, value) pairs. Lists of objects are
matched by a key ("fdi" for teeth, "text" for diagnoses, "name" for
observations, "site" for metastases) before comparison, so order does not matter.
Wrapped fields {"value": ..., "confidence": ...} are unwrapped to their value.

CER mode: each JSONL line is {"id", "text"}.
"""
import argparse
import json
import sys
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher

LIST_KEYS = {"teeth": "fdi", "diagnoses": "text", "observations": "name",
             "metastases": "site", "nodes": "station", "treatments": "type"}


def norm(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return f"{float(v):g}"
    s = unicodedata.normalize("NFC", str(v)).strip().lower()
    return " ".join(s.split())


def unwrap(v):
    if isinstance(v, dict) and "value" in v and "confidence" in v:
        return v["value"]
    return v


def flatten(obj, prefix=""):
    obj = unwrap(obj)
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("confidence", "source"):
                continue
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, list) and k in LIST_KEYS:
                key = LIST_KEYS[k]
                for item in v:
                    kv = norm(unwrap(item.get(key))) if isinstance(item, dict) else norm(item)
                    out.update(flatten(item, f"{path}[{kv}]"))
            elif isinstance(v, list):
                vals = sorted(n for n in (norm(unwrap(x)) for x in v) if n is not None)
                if vals:
                    out[path] = "|".join(vals)
            else:
                out.update(flatten(v, path))
    else:
        n = norm(obj)
        if n is not None and prefix:
            out[prefix] = n
    return out


def strip_accents(s):
    """Remove diacritics so Vietnamese tone-placement variants (thùy/thuỳ) compare equal."""
    decomposed = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn").replace("đ", "d")


def similar(a, b):
    return max(SequenceMatcher(None, a, b).ratio(),
               SequenceMatcher(None, strip_accents(a), strip_accents(b)).ratio())


def load(path, key="doc_id"):
    data = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                data[rec[key]] = rec
    return data


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def field_mode(a):
    gold, pred = load(a.gold), load(a.pred)
    groups = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tpf": 0})
    errors = []
    for doc_id, g in gold.items():
        p = pred.get(doc_id, {"fields": {}})
        gf, pf = flatten(g.get("fields", {})), flatten(p.get("fields", {}))
        for grp in ("ALL", f"unit={g.get('unit', '?')}", f"quality={g.get('quality', '?')}"):
            c = groups[grp]
            for path, gv in gf.items():
                pv = pf.get(path)
                if pv is None:
                    c["fn"] += 1
                    if grp == "ALL":
                        errors.append((doc_id, path, gv, None))
                elif pv == gv:
                    c["tp"] += 1
                    c["tpf"] += 1
                else:
                    c["fp"] += 1
                    c["fn"] += 1
                    if similar(pv, gv) >= a.fuzzy:
                        c["tpf"] += 1
                    if grp == "ALL":
                        errors.append((doc_id, path, gv, pv))
            for path in pf.keys() - gf.keys():
                c["fp"] += 1
                if grp == "ALL":
                    errors.append((doc_id, path, None, pf[path]))

    lines = ["# Extraction evaluation", "", f"Gold docs: {len(gold)} · Pred docs: {len(pred)}", "",
             "| Group | Precision | Recall | F1 (exact) | F1 (fuzzy) |", "| --- | --- | --- | --- | --- |"]
    for grp in sorted(groups, key=lambda x: (x != "ALL", x)):
        c = groups[grp]
        p, r, f = prf(c["tp"], c["fp"], c["fn"])
        fn_fuzzy = c["fn"] - (c["tpf"] - c["tp"])
        fp_fuzzy = c["fp"] - (c["tpf"] - c["tp"])
        _, _, ff = prf(c["tpf"], max(fp_fuzzy, 0), max(fn_fuzzy, 0))
        lines.append(f"| {grp} | {p:.3f} | {r:.3f} | {f:.3f} | {ff:.3f} |")
    lines += ["", "## First 25 errors", "", "| doc | path | gold | pred |", "| --- | --- | --- | --- |"]
    for doc_id, path, gv, pv in errors[:25]:
        lines.append(f"| {doc_id} | `{path}` | {gv} | {pv} |")
    report = "\n".join(lines)
    print(report)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(report + "\n")


def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer_mode(a):
    gold, pred = load(a.gold, "id"), load(a.pred, "id")
    edits = chars = 0
    for k, g in gold.items():
        gt = unicodedata.normalize("NFC", g["text"])
        pt = unicodedata.normalize("NFC", pred.get(k, {}).get("text", ""))
        edits += levenshtein(gt, pt)
        chars += len(gt)
    cer = edits / chars if chars else 0.0
    print(f"Lines: {len(gold)} · Characters: {chars} · CER: {cer:.4f} ({cer * 100:.2f}%)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out")
    ap.add_argument("--fuzzy", type=float, default=0.9)
    ap.add_argument("--cer", action="store_true")
    a = ap.parse_args()
    cer_mode(a) if a.cer else field_mode(a)


if __name__ == "__main__":
    sys.exit(main())
