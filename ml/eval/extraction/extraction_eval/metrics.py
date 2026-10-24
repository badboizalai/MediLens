"""Score predicted extraction JSON against ground truth.

Ported from .claude/skills/medilens-ai-ml-engineer/scripts/eval_extraction.py and extended with
per-field-path scores, region-code accuracy and citation validity.

Record format (JSONL): {"doc_id", "unit", "quality"?, "fields": {...}}. Wrapped fields
{"value", "confidence", "source"?: {"page", "quote"}} are unwrapped to their value.
"""

import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher

LIST_KEYS = {
    "teeth": "fdi",
    "diagnoses": "text",
    "observations": "name",
    "metastases": "site",
    "nodes": "station",
    "treatments": "type",
    "periodontal": "condition",
}
SKIP_KEYS = ("confidence", "source")
_INDEX = re.compile(r"\[[^\]]*\]")


def norm(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, (int, float)):
        return f"{float(v):g}"
    s = unicodedata.normalize("NFC", str(v)).strip().lower()
    return " ".join(s.split())


def unwrap(v):
    if isinstance(v, dict) and "value" in v and "confidence" in v:
        return v["value"]
    return v


def flatten(obj, prefix="", conf=None):
    """Flatten nested fields into {path: normalised value}; lists of objects are keyed.

    If `conf` is a dict it is filled with {path: confidence} for wrapped leaf values.
    """
    if conf is not None and prefix and isinstance(obj, dict):
        c = obj.get("confidence")
        if isinstance(c, (int, float)) and not isinstance(c, bool):
            if "value" in obj:
                conf[prefix] = float(c)
            elif "region_code" in obj:  # region object: confidence belongs to its code
                conf[f"{prefix}.region_code"] = float(c)
    obj = unwrap(obj)
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP_KEYS:
                continue
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, list) and k in LIST_KEYS:
                key = LIST_KEYS[k]
                for item in v:
                    kv = norm(unwrap(item.get(key))) if isinstance(item, dict) else norm(item)
                    out.update(flatten(item, f"{path}[{kv}]", conf))
            elif isinstance(v, list):
                vals = sorted(n for n in (norm(unwrap(x)) for x in v) if n is not None)
                if vals:
                    out[path] = "|".join(vals)
            else:
                out.update(flatten(v, path, conf))
    else:
        n = norm(obj)
        if n is not None and prefix:
            out[prefix] = n
    return out


def field_path(path):
    """`teeth[14].condition` -> `teeth[].condition` (aggregate across instances)."""
    return _INDEX.sub("[]", path)


def _strip_accents(s):
    d = unicodedata.normalize("NFD", s)
    return "".join(c for c in d if unicodedata.category(c) != "Mn").replace("đ", "d")


def similar(a, b):
    return max(
        SequenceMatcher(None, a, b).ratio(),
        SequenceMatcher(None, _strip_accents(a), _strip_accents(b)).ratio(),
    )


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


class _Counts:
    __slots__ = ("tp", "fp", "fn", "tpf")

    def __init__(self):
        self.tp = self.fp = self.fn = self.tpf = 0

    def scores(self):
        p, r, f = prf(self.tp, self.fp, self.fn)
        shift = self.tpf - self.tp
        _, _, ff = prf(self.tpf, max(self.fp - shift, 0), max(self.fn - shift, 0))
        return {
            "precision": p,
            "recall": r,
            "f1": f,
            "f1_fuzzy": ff,
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
        }


def region_codes(fields):
    """{path: region_code} for every `region` object with a non-null region_code."""
    out = {}

    def walk(o, prefix):
        if isinstance(o, dict):
            for k, v in o.items():
                path = f"{prefix}.{k}" if prefix else k
                if k == "region" and isinstance(v, dict):
                    if v.get("region_code") is not None:
                        out[prefix] = v["region_code"]
                elif isinstance(v, list) and k in LIST_KEYS:
                    for item in v:
                        kv = (
                            norm(unwrap(item.get(LIST_KEYS[k]))) if isinstance(item, dict) else None
                        )
                        walk(item, f"{path}[{kv}]")
                else:
                    walk(v, path)

    walk(fields, "")
    return out


def citations(obj):
    """All {page, quote} citations (every `source` object) in a fields tree."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "source" and isinstance(v, dict):
                out.append(v)
            else:
                out.extend(citations(v))
    elif isinstance(obj, list):
        for item in obj:
            out.extend(citations(item))
    return out


def citation_valid(cite, gold_quotes):
    """Valid = positive int page, non-empty quote, and quote is text of the document (same page)."""
    page, quote = cite.get("page"), cite.get("quote")
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        return False
    if not isinstance(quote, str) or not norm(quote):
        return False
    q = norm(quote)
    return any(p == page and q in gq for p, gq in gold_quotes)


def calibration(pairs, n_bins=10):
    """Expected calibration error. pairs: [(confidence in [0,1], correct bool)].

    Equal-width bins; ECE = sum(n_b/n * |acc_b - conf_b|). Also the error rate among conf >= 0.7
    (plan section 10.1). Returns None-valued ECE when there are no pairs (never invents one).
    """
    n = len(pairs)
    bins = [[0, 0.0, 0] for _ in range(n_bins)]  # n, sum conf, n correct
    for c, ok in pairs:
        b = bins[min(int(max(c, 0.0) * n_bins), n_bins - 1)]
        b[0] += 1
        b[1] += c
        b[2] += ok
    ece = sum(abs(b[2] - b[1]) for b in bins) / n if n else None
    hi = [ok for c, ok in pairs if c >= 0.7]
    return {
        "ece": ece,
        "n": n,
        "error_rate_conf_ge_0.7": (1 - sum(hi) / len(hi)) if hi else None,
        "n_conf_ge_0.7": len(hi),
        "bins": [
            {
                "lo": i / n_bins,
                "hi": (i + 1) / n_bins,
                "n": b[0],
                "mean_conf": b[1] / b[0] if b[0] else None,
                "accuracy": b[2] / b[0] if b[0] else None,
            }
            for i, b in enumerate(bins)
        ],
    }


def score(gold, pred, fuzzy=0.9, max_errors=25):
    """gold/pred: {doc_id: record}. Returns a JSON-serialisable report dict."""
    groups = defaultdict(_Counts)
    by_unit_path = defaultdict(_Counts)
    region_ok = region_total = 0
    cite_ok = cite_total = 0
    errors = []
    cal_pairs = {"ALL": []}
    region_by_unit = defaultdict(lambda: [0, 0])  # unit -> [correct, total]
    for doc_id, g in gold.items():
        p = pred.get(doc_id, {"fields": {}})
        unit = g.get("unit", "?")
        pconf = {}
        gf, pf = flatten(g.get("fields", {})), flatten(p.get("fields", {}), conf=pconf)
        for path, c in pconf.items():  # every predicted field with a stated confidence
            if path in pf:
                pair = (min(max(c, 0.0), 1.0), pf[path] == gf.get(path))
                cal_pairs["ALL"].append(pair)
                cal_pairs.setdefault(f"unit={unit}", []).append(pair)
        keys = ["ALL", f"unit={unit}", f"quality={g.get('quality', '?')}"]
        for name, val in sorted(g.get("strata", {}).items()):  # golden-v2: lang/layout/noise
            keys += [f"{name}={val}", f"{name}={val}@unit={unit}"]
        bumps = []  # (path, kind, fuzzy-close)
        for path, gv in gf.items():
            pv = pf.get(path)
            if pv is None:
                bumps.append((path, "fn", False))
                errors.append((doc_id, path, gv, None))
            elif pv == gv:
                bumps.append((path, "tp", True))
            else:
                bumps.append((path, "wrong", similar(pv, gv) >= fuzzy))
                errors.append((doc_id, path, gv, pv))
        for path in pf.keys() - gf.keys():
            bumps.append((path, "fp", False))
            errors.append((doc_id, path, None, pf[path]))
        for path, kind, close in bumps:
            for c in (*(groups[k] for k in keys), by_unit_path[(unit, field_path(path))]):
                if kind == "tp":
                    c.tp += 1
                    c.tpf += 1
                elif kind == "fn":
                    c.fn += 1
                elif kind == "fp":
                    c.fp += 1
                else:
                    c.fp += 1
                    c.fn += 1
                    c.tpf += close

        gr, pr = region_codes(g.get("fields", {})), region_codes(p.get("fields", {}))
        for path, code in gr.items():
            region_total += 1
            region_ok += pr.get(path) == code
            region_by_unit[unit][1] += 1
            region_by_unit[unit][0] += pr.get(path) == code

        gold_quotes = [
            (c.get("page"), norm(c.get("quote")) or "") for c in citations(g.get("fields", {}))
        ]
        for cite in citations(p.get("fields", {})):
            cite_total += 1
            cite_ok += citation_valid(cite, gold_quotes)

    per_path = {}
    for (unit, path), c in sorted(by_unit_path.items()):
        per_path.setdefault(unit, {})[path] = c.scores()
    return {
        "gold_docs": len(gold),
        "pred_docs": len(pred),
        "missing_pred_docs": len(gold.keys() - pred.keys()),
        "overall": groups["ALL"].scores(),
        "groups": {k: v.scores() for k, v in sorted(groups.items()) if k != "ALL"},
        "per_field_path": per_path,
        "region_accuracy": {
            "value": region_ok / region_total if region_total else 0.0,
            "correct": region_ok,
            "total": region_total,
        },
        "region_accuracy_by_unit": {
            u: {"value": ok / t, "correct": ok, "total": t}
            for u, (ok, t) in sorted(region_by_unit.items())
        },
        "calibration": {k: calibration(v) for k, v in sorted(cal_pairs.items())},
        "citation_validity": {
            "value": cite_ok / cite_total if cite_total else 0.0,
            "valid": cite_ok,
            "total": cite_total,
        },
        "first_errors": [
            {"doc": d, "path": p, "gold": g, "pred": v} for d, p, g, v in errors[:max_errors]
        ],
    }


def check_gate(report, thresholds):
    """Return a list of human-readable failures (empty = pass)."""
    fails = []

    def need(name, value, minimum):
        if value < minimum:
            fails.append(f"{name} = {value:.3f} < {minimum:.3f}")

    need("field F1 (overall)", report["overall"]["f1"], thresholds["field_f1_overall"])
    for grp, s in report["groups"].items():
        if grp.startswith("unit="):
            need(f"field F1 ({grp})", s["f1"], thresholds["field_f1_per_unit"])
    need("region accuracy", report["region_accuracy"]["value"], thresholds["region_accuracy"])
    need("citation validity", report["citation_validity"]["value"], thresholds["citation_validity"])
    ece = report["calibration"]["ALL"]["ece"]
    if ece is not None and "ece_max" in thresholds and ece > thresholds["ece_max"]:
        fails.append(f"ECE = {ece:.3f} > {thresholds['ece_max']:.3f}")
    if report["gold_docs"] < thresholds.get("min_gold_docs", 0):
        fails.append(f"gold docs = {report['gold_docs']} < {thresholds['min_gold_docs']}")
    if report["missing_pred_docs"]:
        fails.append(f"{report['missing_pred_docs']} gold docs have no prediction")
    return fails
