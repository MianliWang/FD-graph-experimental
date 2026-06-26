from __future__ import annotations

from collections.abc import Iterable

from fdkeys.model import FD


def validate_universe(universe: Iterable[str], fds: Iterable[FD]) -> None:
    """Validate that all FD attributes belong to the declared universe."""

    universe_set = _attribute_set("universe", universe)
    for fd in fds:
        outside = (fd.lhs | frozenset({fd.rhs})) - universe_set
        if outside:
            names = ", ".join(sorted(outside))
            raise ValueError(f"FD mentions attributes outside universe: {names}")


def validate_attrs_subset(universe: Iterable[str], attrs: Iterable[str]) -> None:
    """Validate that a proposed key is contained in the declared universe."""

    universe_set = _attribute_set("universe", universe)
    attrs_set = _attribute_set("attrs", attrs)
    outside = attrs_set - universe_set
    if outside:
        names = ", ".join(sorted(outside))
        raise ValueError(f"attrs contains attributes outside universe: {names}")


def _attribute_set(name: str, attrs: Iterable[str]) -> frozenset[str]:
    attr_set = frozenset(attrs)
    invalid = sorted(
        repr(attr)
        for attr in attr_set
        if not isinstance(attr, str) or not attr
    )
    if invalid:
        names = ", ".join(invalid)
        raise ValueError(f"{name} must contain only non-empty string attributes: {names}")
    return attr_set
