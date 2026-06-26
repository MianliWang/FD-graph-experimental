from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import product

from fdkeys.model import FD
from fdkeys.validation import validate_universe


def is_unary_fds(fds: Iterable[FD]) -> bool:
    """Return whether every FD has a singleton left-hand side."""

    return all(len(fd.lhs) == 1 for fd in fds)


def build_unary_graph(
    universe: Iterable[str], fds: Iterable[FD]
) -> dict[str, set[str]]:
    """Build the directed graph induced by unary FDs."""

    graph = {attr: set() for attr in universe}
    for fd in fds:
        if len(fd.lhs) != 1:
            raise ValueError("unary graph reasoning requires singleton LHS FDs")
        lhs = next(iter(fd.lhs))
        graph.setdefault(lhs, set()).add(fd.rhs)
        graph.setdefault(fd.rhs, set())
    return graph


def find_candidate_keys_unary_scc(
    universe: Iterable[str], fds: Iterable[FD]
) -> list[frozenset[str]]:
    """Find candidate keys for unary FDs using source SCCs."""

    universe_set = frozenset(universe)
    rules = tuple(fds)
    validate_universe(universe_set, rules)
    if not is_unary_fds(rules):
        raise ValueError("unary SCC reasoning requires singleton LHS FDs")

    graph = build_unary_graph(universe_set, rules)
    components = _strongly_connected_components(graph)
    component_index = {
        attr: index for index, component in enumerate(components) for attr in component
    }
    has_incoming = [False] * len(components)

    for source, targets in graph.items():
        source_index = component_index[source]
        for target in targets:
            target_index = component_index[target]
            if source_index != target_index:
                has_incoming[target_index] = True

    source_components = [
        sorted(component)
        for index, component in enumerate(components)
        if not has_incoming[index]
    ]

    keys = [
        frozenset(choice)
        for choice in product(*source_components)
    ]
    return sorted(keys, key=lambda key: (len(key), tuple(sorted(key))))


def _strongly_connected_components(
    graph: Mapping[str, set[str]]
) -> list[frozenset[str]]:
    """Tarjan SCC decomposition for a small directed graph."""

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[frozenset[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in sorted(graph[node]):
            if neighbor not in indices:
                visit(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[neighbor])

        if lowlinks[node] == indices[node]:
            component = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            components.append(frozenset(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)

    return components
