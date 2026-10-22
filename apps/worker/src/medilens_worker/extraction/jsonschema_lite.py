"""Tiny JSON Schema validator for the keyword subset used by ml/schemas v1.

Stdlib only (no new worker dependency). Supports type, properties, required,
additionalProperties, items, enum, minimum, maximum, minItems, maxItems,
maxLength, pattern and $ref resolved through a $id registry.
"""

import re
from urllib.parse import urljoin


def _is_type(v, t: str) -> bool:
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if t == "boolean":
        return isinstance(v, bool)
    if t == "null":
        return v is None
    return isinstance(v, {"object": dict, "array": list, "string": str}[t])


class Validator:
    def __init__(self, schemas: list[dict]) -> None:
        self._by_id = {s["$id"]: s for s in schemas}

    def _resolve(self, ref: str, base: str, root: dict) -> tuple[dict, str, dict]:
        url, _, frag = urljoin(base, ref).partition("#")
        doc = self._by_id[url] if url in self._by_id else root
        node = doc
        for part in [p for p in frag.split("/") if p]:
            node = node[part]
        return node, doc.get("$id", base), doc

    def errors(self, instance, schema: dict) -> list[str]:
        out: list[str] = []
        self._check(instance, schema, schema.get("$id", ""), schema, "$", out)
        return out

    def _check(self, v, s: dict, base: str, root: dict, path: str, out: list[str]) -> None:
        if "$ref" in s:
            node, nbase, nroot = self._resolve(s["$ref"], base, root)
            self._check(v, node, nbase, nroot, path, out)
            return
        t = s.get("type")
        if t is not None:
            ts = [t] if isinstance(t, str) else t
            if not any(_is_type(v, x) for x in ts):
                out.append(f"{path}: expected {ts}, got {type(v).__name__}")
                return
        if "enum" in s and v not in s["enum"]:
            out.append(f"{path}: not in enum")
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if "minimum" in s and v < s["minimum"]:
                out.append(f"{path}: below minimum {s['minimum']}")
            if "maximum" in s and v > s["maximum"]:
                out.append(f"{path}: above maximum {s['maximum']}")
        if isinstance(v, str):
            if "maxLength" in s and len(v) > s["maxLength"]:
                out.append(f"{path}: longer than {s['maxLength']}")
            if "pattern" in s and not re.search(s["pattern"], v):
                out.append(f"{path}: does not match pattern")
        if isinstance(v, list):
            if "minItems" in s and len(v) < s["minItems"]:
                out.append(f"{path}: fewer than {s['minItems']} items")
            if "maxItems" in s and len(v) > s["maxItems"]:
                out.append(f"{path}: more than {s['maxItems']} items")
            if "items" in s:
                for i, item in enumerate(v):
                    self._check(item, s["items"], base, root, f"{path}[{i}]", out)
        if isinstance(v, dict):
            props = s.get("properties", {})
            for k in s.get("required", []):
                if k not in v:
                    out.append(f"{path}: missing required '{k}'")
            if s.get("additionalProperties") is False:
                for k in v:
                    if k not in props:
                        out.append(f"{path}: unexpected field '{k}'")
            for k, sub in props.items():
                if k in v:
                    self._check(v[k], sub, base, root, f"{path}.{k}", out)
