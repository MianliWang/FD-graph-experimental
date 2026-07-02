import pytest

from fdkeys import estimate_storage_bytes, relation_width


def test_relation_width_sums_attribute_widths() -> None:
    assert relation_width({"B", "A"}, {"A": 8, "B": 20, "C": 40}) == 28


def test_relation_width_rejects_missing_width() -> None:
    with pytest.raises(ValueError, match="missing attribute widths for: C"):
        relation_width({"A", "C"}, {"A": 8})


def test_estimate_storage_bytes_uses_relation_specific_row_counts() -> None:
    relations = [
        frozenset({"A", "B"}),
        frozenset({"B", "C"}),
    ]
    row_counts = {
        frozenset({"A", "B"}): 1_000,
        frozenset({"B", "C"}): 100,
    }
    widths = {"A": 8, "B": 20, "C": 40}

    assert estimate_storage_bytes(relations, row_counts, widths) == 34_000


def test_estimate_storage_bytes_rejects_missing_row_count() -> None:
    with pytest.raises(ValueError, match="missing row count"):
        estimate_storage_bytes(
            [frozenset({"A", "B"})],
            {},
            {"A": 8, "B": 20},
        )
