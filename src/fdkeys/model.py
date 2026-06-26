from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FD:
    """A single-RHS functional dependency."""

    lhs: frozenset[str]
    rhs: str

    def __post_init__(self) -> None:
        lhs = frozenset(self.lhs)
        if not lhs:
            raise ValueError("FD left-hand side must be non-empty")
        if any(not isinstance(attr, str) or not attr for attr in lhs):
            raise ValueError("FD left-hand side attributes must be non-empty strings")
        if not isinstance(self.rhs, str) or not self.rhs:
            raise ValueError("FD right-hand side must be a non-empty string")
        object.__setattr__(self, "lhs", lhs)


def make_fd(lhs: Iterable[str], rhs: str) -> FD:
    """Construct an FD from any iterable of left-hand-side attributes."""

    return FD(frozenset(lhs), rhs)
