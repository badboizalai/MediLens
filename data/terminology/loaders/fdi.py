"""Generate the FDI two-digit tooth table (public notation, no licence issue)."""

from __future__ import annotations

import csv
from pathlib import Path

FDI_CSV = Path(__file__).resolve().parent.parent / "fdi.csv"
FIELDS = [
    "fdi", "dentition", "quadrant", "position", "arch", "laterality",
    "name_en", "name_vi",
]  # fmt: skip

# quadrant -> (dentition, arch, laterality); patient's own side.
QUADRANTS = {
    1: ("permanent", "upper", "right"),
    2: ("permanent", "upper", "left"),
    3: ("permanent", "lower", "left"),
    4: ("permanent", "lower", "right"),
    5: ("deciduous", "upper", "right"),
    6: ("deciduous", "upper", "left"),
    7: ("deciduous", "lower", "left"),
    8: ("deciduous", "lower", "right"),
}
PERMANENT = {
    1: ("central incisor", "răng cửa giữa"),
    2: ("lateral incisor", "răng cửa bên"),
    3: ("canine", "răng nanh"),
    4: ("first premolar", "răng cối nhỏ thứ nhất"),
    5: ("second premolar", "răng cối nhỏ thứ hai"),
    6: ("first molar", "răng cối lớn thứ nhất"),
    7: ("second molar", "răng cối lớn thứ hai"),
    8: ("third molar", "răng cối lớn thứ ba"),
}
DECIDUOUS = {
    1: ("central incisor", "răng cửa giữa"),
    2: ("lateral incisor", "răng cửa bên"),
    3: ("canine", "răng nanh"),
    4: ("first molar", "răng cối sữa thứ nhất"),
    5: ("second molar", "răng cối sữa thứ hai"),
}
ARCH_VI = {"upper": "hàm trên", "lower": "hàm dưới"}
SIDE_VI = {"right": "bên phải", "left": "bên trái"}


def rows() -> list[dict[str, str]]:
    out = []
    for q, (dentition, arch, side) in QUADRANTS.items():
        names = PERMANENT if dentition == "permanent" else DECIDUOUS
        for pos, (en, vi) in names.items():
            prefix = "deciduous " if dentition == "deciduous" else ""
            out.append(
                {
                    "fdi": f"{q}{pos}",
                    "dentition": dentition,
                    "quadrant": str(q),
                    "position": str(pos),
                    "arch": arch,
                    "laterality": side,
                    "name_en": f"{prefix}{arch} {side} {en}".capitalize(),
                    "name_vi": f"{vi.capitalize()} {ARCH_VI[arch]} {SIDE_VI[side]}",
                }
            )
    return sorted(out, key=lambda r: (r["dentition"] != "permanent", r["fdi"]))


def write(path: Path = FDI_CSV) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows())


if __name__ == "__main__":
    write()
