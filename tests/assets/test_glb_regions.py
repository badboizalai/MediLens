"""GLB meshes must be named by region_code (optional `__lod1` suffix) and fit the size budget.

Run: uv run --with pytest --with pyyaml pytest -q tests/assets
"""

import json
import struct
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
GLB = ROOT / "packages/anatomy-assets/glb"
TREE = ROOT / "data/terminology/region-tree.v1.yaml"
BUDGET = {"body.glb": 1_500_000, "heart.glb": 1_000_000}
HEART_REQUIRED = {
    "heart_ra", "heart_la", "heart_rv", "heart_lv", "heart_septum_ias", "heart_septum_ivs",
    "valve_aortic", "valve_mitral", "valve_tricuspid", "valve_pulmonary",
    "cor_rca", "cor_lmca", "cor_lad", "cor_lcx", "aorta", "pulmonary_trunk",
}  # fmt: skip


def mesh_names(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data)
    assert (magic, version, length) == (b"glTF", 2, len(data))
    clen, ctype = struct.unpack_from("<I4s", data, 12)
    assert ctype == b"JSON"
    return [m["name"] for m in json.loads(data[20 : 20 + clen])["meshes"]]


def test_glb_meshes_are_region_codes_with_lod_and_budget():
    codes = {r["region_code"] for r in yaml.safe_load(TREE.read_text(encoding="utf-8"))}
    for fname, limit in BUDGET.items():
        path = GLB / fname
        assert path.stat().st_size <= limit, f"{fname} over budget"
        names = mesh_names(path)
        assert len(names) == len(set(names)), f"duplicate mesh names in {fname}"
        base = {n.removesuffix("__lod1") for n in names}
        assert base <= codes, f"{fname}: unknown {base - codes}"
        no_lod = sorted(b for b in base if b not in names or b + "__lod1" not in names)
        assert not no_lod, f"{fname}: missing LOD level {no_lod}"
        if fname == "heart.glb":
            assert HEART_REQUIRED <= base, f"missing {HEART_REQUIRED - base}"
        else:
            assert {
                "body",
                "heart",
                "lung_l",
                "lung_r",
                "liver",
                "kidney_l",
                "kidney_r",
                "brain",
            } <= base
