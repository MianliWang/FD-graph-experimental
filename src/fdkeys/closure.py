from __future__ import annotations

from collections.abc import Iterable

from fdkeys.model import FD


def closure(attrs: Iterable[str], fds: Iterable[FD]) -> frozenset[str]:
    """Compute the standard attribute closure under a set of FDs."""

    known = set(attrs)
    rules = tuple(fds)

    changed = True
    while changed:
        changed = False
        for fd in rules:
            if fd.lhs <= known and fd.rhs not in known:
                known.add(fd.rhs)
                changed = True

    return frozenset(known)
