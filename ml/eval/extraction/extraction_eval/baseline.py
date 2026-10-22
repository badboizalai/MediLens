"""Deterministic "oracle-with-noise" baseline generator.

NOT A MODEL RESULT. It copies the ground truth and injects seeded noise so CI exercises the
scoring pipeline without any LLM call. Its scores say nothing about extraction quality.
"""

import copy
import json
import random

LABEL = "NOT_A_MODEL_RESULT: oracle-with-noise baseline for CI plumbing"
SEED = 20261023
P_DROP = 0.04  # remove a leaf field
P_CORRUPT = 0.04  # alter a leaf value
P_REGION = 0.04  # wrong region_code
P_CITE = 0.01  # citation points at text not in the document
_SKIP = ("confidence", "source", "region")


def _corrupt(v, rng):
    if isinstance(v, bool):
        return not v
    if isinstance(v, int):
        return v + 1
    if isinstance(v, str) and v:
        i = rng.randrange(len(v))
        return v[:i] + ("x" if v[i] != "x" else "y") + v[i + 1 :]
    return v


def _noise(o, rng):
    if isinstance(o, list):
        for item in o:
            _noise(item, rng)
        return
    if not isinstance(o, dict):
        return
    if "value" in o and "confidence" in o:
        if rng.random() < P_CORRUPT:
            o["value"] = _corrupt(o["value"], rng)
        src = o.get("source")
        if isinstance(src, dict) and rng.random() < P_CITE:
            src["quote"] = "not in the document"
        return
    region = o.get("region")
    if isinstance(region, dict) and region.get("region_code") and rng.random() < P_REGION:
        region["region_code"] = "unknown_region"
    for k in list(o):
        if k in _SKIP:
            continue
        v = o[k]
        if isinstance(v, (dict, list)):
            _noise(v, rng)
        elif isinstance(v, (str, int)) and not isinstance(v, bool):
            if rng.random() < P_DROP:
                del o[k]
            elif rng.random() < P_CORRUPT:
                o[k] = _corrupt(v, rng)


def generate(gold_records, seed=SEED):
    rng = random.Random(seed)  # noqa: S311 - deterministic test noise, not crypto
    out = []
    for rec in gold_records:
        fields = copy.deepcopy(rec["fields"])
        _noise(fields, rng)
        out.append(
            {
                "doc_id": rec["doc_id"],
                "unit": rec.get("unit"),
                "quality": rec.get("quality"),
                "fields": fields,
                "_label": LABEL,
            }
        )
    return out


def dumps(records):
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)
