from collections import Counter

from synth_gen.pages import PER_TYPE, TYPES, generate_pages


def test_nine_types_balanced_split_and_deterministic():
    pages = generate_pages(1)
    assert len(TYPES) == 9 and PER_TYPE >= 30
    assert set(Counter((p["label"], p["split"]) for p in pages).values()) == {PER_TYPE // 2}
    assert pages == generate_pages(1) != generate_pages(2)


def test_fake_identity_only():
    assert all("Nguyen Van Test" in p["text"] and "1900" in p["text"] for p in generate_pages(1))
