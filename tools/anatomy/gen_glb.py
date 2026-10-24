#!/usr/bin/env python3
"""Generate stylised procedural placeholder GLBs (stdlib only): python3 tools/anatomy/gen_glb.py

Mesh/node names == region_code; LOD1 = `<region_code>__lod1` (coarser). Units: metres, +Y up,
patient's right = -X (viewer front view). Not real anatomy (BR-042: illustration only).
"""

import json
import math
import struct
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "packages/anatomy-assets/glb"


def ellipsoid(c, r, seg):
    v, t = [], []
    for i in range(seg + 1):
        p = math.pi * i / seg
        for j in range(seg * 2):
            a = math.pi * j / seg
            v.append(
                (
                    c[0] + r[0] * math.sin(p) * math.cos(a),
                    c[1] + r[1] * math.cos(p),
                    c[2] + r[2] * math.sin(p) * math.sin(a),
                )
            )
    w = seg * 2
    for i in range(seg):
        for j in range(w):
            a, b = i * w + j, i * w + (j + 1) % w
            t += [(a, a + w, b), (b, a + w, b + w)]
    return v, t


def _unit(d):
    m = math.sqrt(sum(x * x for x in d)) or 1
    return [x / m for x in d]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def tube(pts, rad, seg):
    """Round tube of radius rad along a polyline (ends left open)."""
    v, t, n = [], [], len(pts)
    for k, p in enumerate(pts):
        d = _unit([pts[min(k + 1, n - 1)][i] - pts[max(k - 1, 0)][i] for i in range(3)])
        u = _unit(_cross(d, (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)))
        w = _cross(d, u)
        for s in range(seg):
            a = 2 * math.pi * s / seg
            v.append(
                tuple(p[i] + rad * (math.cos(a) * u[i] + math.sin(a) * w[i]) for i in range(3))
            )
    for k in range(n - 1):
        for s in range(seg):
            a, b = k * seg + s, k * seg + (s + 1) % seg
            t += [(a, a + seg, b), (b, a + seg, b + seg)]
    return v, t


def merge(parts):
    v, t = [], []
    for pv, pt in parts:
        t += [tuple(i + len(v) for i in tri) for tri in pt]
        v += pv
    return v, t


def build(shapes):
    """shapes: {name: fn(seg)->(verts, tris)}. Emits lod0 (seg 12) + lod1 (seg 6) per name."""
    blob, views, accs, meshes, nodes = bytearray(), [], [], [], []
    for name, fn in shapes.items():
        for suffix, seg in (("", 12), ("__lod1", 6)):
            v, t = fn(seg)
            pos = b"".join(struct.pack("<3f", *p) for p in v)
            idx = b"".join(struct.pack("<3H", *tri) for tri in t)
            bounds = {
                "min": [min(p[i] for p in v) for i in range(3)],
                "max": [max(p[i] for p in v) for i in range(3)],
            }
            prim = {"mode": 4}
            for data, target, comp, typ, cnt, extra in (
                (pos, 34962, 5126, "VEC3", len(v), bounds),
                (idx, 34963, 5123, "SCALAR", len(t) * 3, {}),
            ):
                views.append(
                    {
                        "buffer": 0,
                        "byteOffset": len(blob),
                        "byteLength": len(data),
                        "target": target,
                    }
                )
                blob += data + b"\0" * (-len(data) % 4)
                accs.append(
                    {
                        "bufferView": len(views) - 1,
                        "componentType": comp,
                        "type": typ,
                        "count": cnt,
                        **extra,
                    }
                )
            prim["attributes"] = {"POSITION": len(accs) - 2}
            prim["indices"] = len(accs) - 1
            meshes.append({"name": name + suffix, "primitives": [prim]})
            nodes.append({"name": name + suffix, "mesh": len(meshes) - 1})
    nodes.append({"name": "aux_root", "children": list(range(len(nodes)))})
    js = {
        "asset": {"version": "2.0", "generator": "tools/anatomy/gen_glb.py"},
        "scene": 0,
        "scenes": [{"nodes": [len(nodes) - 1]}],
        "nodes": nodes,
        "meshes": meshes,
        "accessors": accs,
        "bufferViews": views,
        "buffers": [{"byteLength": len(blob)}],
    }
    j = json.dumps(js, separators=(",", ":")).encode()
    j += b" " * (-len(j) % 4)
    total = 12 + 8 + len(j) + 8 + len(blob)
    head = struct.pack("<4sII", b"glTF", 2, total)
    return (
        head
        + struct.pack("<I4s", len(j), b"JSON")
        + j
        + struct.pack("<I4s", len(blob), b"BIN\0")
        + bytes(blob)
    )


def ell(c, r):
    return lambda s: ellipsoid(c, r, s)


def tb(pts, rad):
    return lambda s: tube(pts, rad, max(s // 2, 3))


def _body(s):
    q = max(s // 2, 3)
    return merge(
        [
            ellipsoid((0, 1.35, 0), (0.2, 0.3, 0.12), s),  # chest
            ellipsoid((0, 1.0, 0), (0.17, 0.25, 0.1), s),  # abdomen
            ellipsoid((0, 1.75, 0), (0.09, 0.11, 0.09), s),  # head
            tube([(-0.22, 1.5, 0), (-0.42, 1.1, 0), (-0.5, 0.75, 0)], 0.04, q),
            tube([(0.22, 1.5, 0), (0.42, 1.1, 0), (0.5, 0.75, 0)], 0.04, q),
            tube([(-0.1, 0.8, 0), (-0.12, 0.4, 0), (-0.12, 0.0, 0.03)], 0.065, q),
            tube([(0.1, 0.8, 0), (0.12, 0.4, 0), (0.12, 0.0, 0.03)], 0.065, q),
        ]
    )


# silhouette (torso + head + limbs) is merged into the root region `body`
BODY = {
    "body": _body,
    "brain": ell((0, 1.78, 0), (0.07, 0.07, 0.07)),
    "thyroid": ell((0, 1.56, 0.05), (0.03, 0.015, 0.015)),
    "lung_r": ell((-0.11, 1.38, 0), (0.08, 0.17, 0.07)),
    "lung_l": ell((0.11, 1.38, 0), (0.07, 0.17, 0.07)),
    "heart": ell((0.03, 1.33, 0.03), (0.055, 0.065, 0.05)),
    "liver": ell((-0.07, 1.15, 0.02), (0.1, 0.05, 0.07)),
    "stomach": ell((0.08, 1.15, 0.03), (0.055, 0.05, 0.04)),
    "spleen": ell((0.14, 1.17, -0.04), (0.025, 0.04, 0.02)),
    "pancreas": ell((0.0, 1.08, -0.02), (0.08, 0.015, 0.02)),
    "kidney_r": ell((-0.07, 1.05, -0.07), (0.025, 0.04, 0.02)),
    "kidney_l": ell((0.07, 1.05, -0.07), (0.025, 0.04, 0.02)),
    "colon": tb([(-0.1, 0.9, 0.04), (-0.1, 1.0, 0.04), (0.1, 1.0, 0.04), (0.1, 0.9, 0.04)], 0.018),
    "bladder": ell((0, 0.85, 0.03), (0.035, 0.03, 0.03)),
}

HEART = {  # patient's right = -X
    "heart_ra": ell((-0.35, 0.25, 0.1), (0.22, 0.25, 0.2)),
    "heart_la": ell((0.3, 0.45, -0.15), (0.2, 0.2, 0.2)),
    "heart_rv": ell((-0.15, -0.2, 0.25), (0.28, 0.3, 0.22)),
    "heart_lv": ell((0.2, -0.25, 0.0), (0.3, 0.42, 0.28)),
    "heart_septum_ias": ell((0.0, 0.3, -0.02), (0.02, 0.2, 0.15)),
    "heart_septum_ivs": ell((0.02, -0.2, 0.1), (0.03, 0.35, 0.22)),
    "valve_aortic": ell((0.05, 0.12, 0.05), (0.07, 0.015, 0.07)),
    "valve_mitral": ell((0.2, 0.1, -0.05), (0.09, 0.015, 0.09)),
    "valve_tricuspid": ell((-0.25, 0.05, 0.15), (0.09, 0.015, 0.09)),
    "valve_pulmonary": ell((-0.05, 0.1, 0.3), (0.07, 0.015, 0.07)),
    "cor_rca": tb([(-0.1, 0.15, 0.42), (-0.4, 0.0, 0.3), (-0.5, -0.2, 0.1)], 0.025),
    "cor_lmca": tb([(0.1, 0.2, 0.35), (0.25, 0.15, 0.3)], 0.03),
    "cor_lad": tb([(0.25, 0.15, 0.3), (0.12, -0.2, 0.38), (0.05, -0.6, 0.25)], 0.025),
    "cor_lcx": tb([(0.25, 0.15, 0.3), (0.5, 0.0, 0.1), (0.5, -0.2, -0.15)], 0.025),
    "aorta": tb([(0.05, 0.15, 0.05), (0.05, 0.6, 0.0), (0.2, 0.8, -0.1), (0.35, 0.6, -0.25)], 0.09),
    "pulmonary_trunk": tb([(-0.05, 0.12, 0.3), (-0.05, 0.5, 0.2)], 0.08),
    "pulmonary_artery_r": tb([(-0.05, 0.5, 0.2), (-0.4, 0.65, 0.0)], 0.05),
    "pulmonary_artery_l": tb([(-0.05, 0.5, 0.2), (0.3, 0.7, -0.05)], 0.05),
    "pulmonary_veins_r": tb([(-0.55, 0.5, -0.2), (-0.15, 0.45, -0.2)], 0.04),
    "pulmonary_veins_l": tb([(0.7, 0.5, -0.2), (0.4, 0.45, -0.2)], 0.04),
    "vena_cava_superior": tb([(-0.35, 0.45, 0.1), (-0.35, 0.95, 0.05)], 0.07),
    "vena_cava_inferior": tb([(-0.35, 0.05, 0.1), (-0.35, -0.6, 0.0)], 0.07),
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fname, shapes in (("body.glb", BODY), ("heart.glb", HEART)):
        data = build(shapes)
        (OUT / fname).write_bytes(data)
        print(fname, len(data), "bytes")
