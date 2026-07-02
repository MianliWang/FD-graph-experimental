from __future__ import annotations

from collections.abc import Iterable, Mapping


def relation_width(
    relation: Iterable[str],
    attribute_widths: Mapping[str, int],
) -> int:
    """Estimate one tuple width as the sum of attribute widths."""

    relation_set = frozenset(relation)
    missing = sorted(attr for attr in relation_set if attr not in attribute_widths)
    if missing:
        raise ValueError(f"missing attribute widths for: {', '.join(missing)}")

    widths = {attr: attribute_widths[attr] for attr in relation_set}
    invalid = sorted(attr for attr, width in widths.items() if width < 0)
    if invalid:
        raise ValueError(f"attribute widths must be non-negative for: {', '.join(invalid)}")

    return sum(widths.values())


def estimate_storage_bytes(
    relations: Iterable[Iterable[str]],
    row_counts: Mapping[Iterable[str], int],
    attribute_widths: Mapping[str, int],
) -> int:
    """Estimate total bytes for a decomposition from widths and row counts."""

    relation_sets = tuple(frozenset(relation) for relation in relations)
    counts = {frozenset(relation): count for relation, count in row_counts.items()}
    total = 0

    for relation in relation_sets:
        if relation not in counts:
            raise ValueError(
                "missing row count for relation: "
                + "{" + ", ".join(sorted(relation)) + "}"
            )
        count = counts[relation]
        if count < 0:
            raise ValueError("row counts must be non-negative")
        total += count * relation_width(relation, attribute_widths)

    return total
