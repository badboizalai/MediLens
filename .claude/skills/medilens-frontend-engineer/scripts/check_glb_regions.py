#!/usr/bin/env python3
"""Check that a GLB model's node/mesh names match a MediLens Unit config.

Usage:
    python check_glb_regions.py model.glb unit-config.json [--max-mb 5] [--allow-extra prefix1,prefix2]

Unit config JSON must contain "regions": [{"region_code": "...", "mesh_id": "..."}].
mesh_id defaults to region_code when absent. Reads the GLB JSON chunk directly
(no dependencies). Exit 1 when regions are missing, unexpected names exist
(not matching --allow-extra prefixes) or the file is larger than --max-mb.
"""
import argparse
import json
import os
import struct
import sys


def read_glb_json(path: str) -> dict:
    with open(path, "rb") as fh:
        magic, version, _length = struct.unpack("<4sII", fh.read(12))
        if magic != b"glTF":
            raise ValueError("not a GLB file")
        if version != 2:
            raise ValueError(f"unsupported glTF version {version}")
        chunk_len, chunk_type = struct.unpack("<I4s", fh.read(8))
        if chunk_type != b"JSON":
            raise ValueError("first chunk is not JSON")
        return json.loads(fh.read(chunk_len).decode("utf-8"))


def names_in(gltf: dict) -> set[str]:
    names = {n.get("name") for n in gltf.get("nodes", []) if n.get("name")}
    names |= {m.get("name") for m in gltf.get("meshes", []) if m.get("name")}
    return names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("glb")
    ap.add_argument("config")
    ap.add_argument("--max-mb", type=float, default=5.0)
    ap.add_argument("--allow-extra", default="root,scene,armature,camera,light,skin_,muscle_,skeleton_,lymph_,vessel_")
    a = ap.parse_args()

    gltf = read_glb_json(a.glb)
    cfg = json.load(open(a.config, encoding="utf-8"))
    expected = {r.get("mesh_id") or r["region_code"] for r in cfg.get("regions", [])}
    present = names_in(gltf)
    allowed_prefixes = tuple(p.strip().lower() for p in a.allow_extra.split(",") if p.strip())

    missing = sorted(expected - present)
    extra = sorted(n for n in present - expected if not n.lower().startswith(allowed_prefixes))
    size_mb = os.path.getsize(a.glb) / (1024 * 1024)
    draco = "KHR_draco_mesh_compression" in gltf.get("extensionsUsed", [])
    meshopt = "EXT_meshopt_compression" in gltf.get("extensionsUsed", [])

    print(f"regions expected: {len(expected)} · names in model: {len(present)} · size: {size_mb:.2f} MB")
    print(f"compression: {'draco' if draco else ''}{' meshopt' if meshopt else ''}{'' if (draco or meshopt) else 'none (warn)'}")
    print(f"missing ({len(missing)}): {', '.join(missing) or '-'}")
    print(f"unexpected ({len(extra)}): {', '.join(extra[:30]) or '-'}{' …' if len(extra) > 30 else ''}")
    fail = bool(missing or extra or size_mb > a.max_mb)
    if size_mb > a.max_mb:
        print(f"FAIL size {size_mb:.2f} MB > {a.max_mb} MB")
    print("RESULT:", "FAIL" if fail else "PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
