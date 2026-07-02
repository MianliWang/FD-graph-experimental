from __future__ import annotations

from collections.abc import Iterable
from itertools import combinations

from fdkeys.closure import closure
from fdkeys.model import FD
from fdkeys.validation import validate_attrs_subset, validate_universe


def is_superkey(universe: Iterable[str], fds: Iterable[FD], attrs: Iterable[str]) -> bool:
    """Return whether attrs determines exactly the schema universe."""

    universe_set = frozenset(universe)
    rules = tuple(fds)
    attrs_set = frozenset(attrs)
    validate_universe(universe_set, rules)
    validate_attrs_subset(universe_set, attrs_set)
    return closure(attrs_set, rules) == universe_set


def is_candidate_key(
    universe: Iterable[str], fds: Iterable[FD], attrs: Iterable[str]
) -> bool:
    """Return whether attrs is an inclusion-minimal superkey."""

    universe_set = frozenset(universe)
    attrs_set = frozenset(attrs)
    rules = tuple(fds)

    validate_universe(universe_set, rules)
    validate_attrs_subset(universe_set, attrs_set)
    if closure(attrs_set, rules) != universe_set:
        return False

    return all(
        closure(attrs_set - {attr}, rules) != universe_set
        for attr in attrs_set
    )


def find_candidate_keys(
    universe: Iterable[str], fds: Iterable[FD]
) -> list[frozenset[str]]:
    """Enumerate all inclusion-minimal superkeys."""

    universe_set = frozenset(universe)
    rules = tuple(fds)
    validate_universe(universe_set, rules)
    rhs_attrs = {fd.rhs for fd in rules}
    mandatory = universe_set - rhs_attrs
    optional = sorted(universe_set - mandatory)

    keys: list[frozenset[str]] = []
    for size in range(len(optional) + 1):
        for combo in combinations(optional, size):
            candidate = mandatory | frozenset(combo)
            if any(key <= candidate for key in keys):
                continue
            if closure(candidate, rules) == universe_set:
                keys.append(candidate)

    return keys


def find_candidate_keys_pruned(
    universe: Iterable[str], fds: Iterable[FD]
) -> list[frozenset[str]]:
    """Find candidate keys with closure-based DFS pruning.

    This is still an exhaustive search in the worst case, but it avoids adding
    attributes that are already derivable from the current seed set.
    """

    universe_set = frozenset(universe)
    rules = tuple(fds)
    validate_universe(universe_set, rules)
    rhs_attrs = {fd.rhs for fd in rules}
    mandatory = universe_set - rhs_attrs
    optional = tuple(sorted(universe_set - mandatory))

    keys: list[frozenset[str]] = []

    def visit(candidate: frozenset[str], remaining: tuple[str, ...]) -> None:
        if any(key <= candidate for key in keys):
            return

        known = closure(candidate, rules)
        if known == universe_set:
            keys[:] = [key for key in keys if not candidate < key]
            keys.append(candidate)
            return

        for index, attr in enumerate(remaining):
            if attr in known:
                continue
            visit(candidate | frozenset({attr}), remaining[index + 1 :])

    visit(mandatory, optional)
    return sorted(keys, key=lambda key: (len(key), tuple(sorted(key))))
