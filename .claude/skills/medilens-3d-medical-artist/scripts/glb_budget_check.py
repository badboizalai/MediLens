#!/usr/bin/env python3
"""Check a GLB against MediLens asset budgets and region names.

Usage: python glb_budget_check.py model.glb [--regions regions.csv] [--max-mb 5]
       [--max-tris 150000] [--max-mesh-tris 20000]

Reads the GLB JSON chunk (no dependencies). Triangles are counted from index
accessors (or POSITION count / 3 when non-indexed), for TRIANGLES mode
primitives. Reports file size, meshes, triangles per mesh, unnamed meshes,
names that are not region codes (except aux_/device_ prefixes) and, with
--regions, regions that have no mesh. Exit 1 on budget or naming errors.
"""
import argparse
import csv
import json
import os
import re
import struct
import sys

NAME_RX = re.compile(r"^[a-z][a-z0-9_]*$")


def read_json(path):
    with open(path, "rb") as fh:
        magic, version, _length = struct.unpack("<4sII", fh.read(12))
        if magic != b"glTF" or version != 2:
            raise ValueError("not a glTF 2.0 binary")
        clen, ctype = struct.unpack("<I4s", fh.read(8))
        if ctype != b"JSON":
            raise ValueError("first chunk is not JSON")
        return json.loads(fh.read(clen))


def mesh_triangles(gltf, mesh):
    acc = gltf.get("accessors", [])
    tris = 0
    for prim in mesh.get("primitives", []):
        if prim.get("mode", 4) != 4:
            continue
        if "indices" in prim:
            tris += acc[prim["indices"]]["count"] // 3
        elif "POSITION" in prim.get("attributes", {}):
            tris += acc[prim["attributes"]["POSITION"]]["count"] // 3
    return tris


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("glb")
    ap.add_argument("--regions")
    ap.add_argument("--max-mb", type=float, default=5.0)
    ap.add_argument("--max-tris", type=int, default=150000)
    ap.add_argument("--max-mesh-tris", type=int, default=20000)
    a = ap.parse_args()
    gltf = read_json(a.glb)
    size_mb = os.path.getsize(a.glb) / 1e6
    errors, warns = [], []
    if size_mb > a.max_mb:
        errors.append(f"file {size_mb:.2f} MB > {a.max_mb} MB")
    exts = gltf.get("extensionsUsed", [])
    if not any(e in exts for e in ("KHR_draco_mesh_compression", "EXT_meshopt_compression")):
        warns.append("no Draco/meshopt compression declared")
    nodes = gltf.get("nodes", [])
    meshes = gltf.get("meshes", [])
    # name used for a mesh = node name referencing it, else mesh name
    names = {}
    for n in nodes:
        if "mesh" in n:
            names[n["mesh"]] = n.get("name") or meshes[n["mesh"]].get("name")
    total = 0
    found = set()
    for i, m in enumerate(meshes):
        name = names.get(i) or m.get("name")
        t = mesh_triangles(gltf, m)
        total += t
        if not name:
            errors.append(f"mesh #{i} has no name")
            continue
        if not NAME_RX.match(name):
            errors.append(f"mesh '{name}' is not snake_case ascii")
        if not name.startswith(("aux_", "device_")):
            found.add(name)
            if t > a.max_mesh_tris:
                warns.append(f"mesh '{name}' has {t} triangles (> {a.max_mesh_tris})")
    if total > a.max_tris:
        errors.append(f"total triangles {total} > {a.max_tris}")
    if a.regions:
        with open(a.regions, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        required = {r["region_code"] for r in rows if (r.get("mesh_required") or "yes").lower() == "yes"}
        allowed = {r["region_code"] for r in rows}
        for name in sorted(found - allowed):
            errors.append(f"mesh '{name}' is not a known region_code")
        for code in sorted(required - found):
            errors.append(f"region '{code}' has no mesh")
    print(f"{os.path.basename(a.glb)}: {size_mb:.2f} MB, {len(meshes)} meshes, {total} triangles")
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print("RESULT:", "FAIL" if errors else "PASS")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
