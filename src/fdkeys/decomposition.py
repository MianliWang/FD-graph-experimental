from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations

from fdkeys.closure import closure
from fdkeys.keys import find_candidate_keys_pruned
from fdkeys.model import FD
from fdkeys.validation import validate_attrs_subset, validate_universe


@dataclass(frozen=True, slots=True)
class GeneratedRelation:
    """A relation produced from one determinant in a 3NF synthesis trace."""

    determinant: frozenset[str]
    rhs_attrs: tuple[str, ...]
    relation: frozenset[str]
    source_fds: tuple[FD, ...]


@dataclass(frozen=True, slots=True)
class SynthesisTrace:
    """Readable trace of the compact 3NF synthesis process."""

    universe: frozenset[str]
    original_fds: tuple[FD, ...]
    minimal_cover: tuple[FD, ...]
    generated_relations: tuple[GeneratedRelation, ...]
    removed_subsumed_relations: tuple[frozenset[str], ...]
    relations_after_subsumption: tuple[frozenset[str], ...]
    added_key_relation: frozenset[str] | None
    final_relations: tuple[frozenset[str], ...]


def minimal_cover(universe: Iterable[str], fds: Iterable[FD]) -> list[FD]:
    """Compute a small canonical-cover style FD set.

    The project represents only non-empty LHS, single-RHS FDs, so this helper
    does not produce empty-determinant dependencies.
    """

    universe_set = frozenset(universe)
    cover = _unique_fds(tuple(fds))
    validate_universe(universe_set, cover)
    cover = _minimize_lhs(cover)
    cover = _remove_redundant_fds(cover)
    return _sort_fds(cover)


def synthesize_3nf(universe: Iterable[str], fds: Iterable[FD]) -> list[frozenset[str]]:
    """Synthesize a small dependency-preserving 3NF decomposition."""

    return list(explain_3nf_synthesis(universe, fds).final_relations)


def decompose_bcnf(universe: Iterable[str], fds: Iterable[FD]) -> list[frozenset[str]]:
    """Return a deterministic teaching BCNF decomposition.

    This uses exhaustive FD projection on each relation, so it is meant for
    small examples rather than large schemas.
    """

    universe_set = frozenset(universe)
    rules = tuple(fds)
    validate_universe(universe_set, rules)
    relations: list[frozenset[str]] = []

    def visit(relation: frozenset[str]) -> None:
        projected = project_fds(universe_set, rules, relation)
        for fd in projected:
            determined = closure(fd.lhs, projected) & relation
            if relation <= determined:
                continue

            dependent_relation = determined
            remainder_relation = relation - (determined - fd.lhs)
            visit(dependent_relation)
            visit(remainder_relation)
            return

        relations.append(relation)

    visit(universe_set)
    return _sort_relations(relations)


def explain_3nf_synthesis(
    universe: Iterable[str], fds: Iterable[FD]
) -> SynthesisTrace:
    """Return a teaching trace for the compact 3NF synthesis algorithm."""

    universe_set = frozenset(universe)
    original_fds = tuple(fds)
    cover = tuple(minimal_cover(universe_set, original_fds))
    grouped: dict[frozenset[str], list[FD]] = {}

    for fd in cover:
        grouped.setdefault(fd.lhs, []).append(fd)

    generated = tuple(
        GeneratedRelation(
            determinant=lhs,
            rhs_attrs=tuple(sorted(fd.rhs for fd in source_fds)),
            relation=lhs | frozenset(fd.rhs for fd in source_fds),
            source_fds=tuple(source_fds),
        )
        for lhs, source_fds in sorted(
            grouped.items(), key=lambda item: (tuple(sorted(item[0])), len(item[1]))
        )
    )

    generated_relations = [step.relation for step in generated]
    relations = _remove_subsumed_relations(generated_relations)
    removed = tuple(
        sorted(
            set(generated_relations) - set(relations),
            key=lambda rel: (len(rel), tuple(sorted(rel))),
        )
    )
    after_subsumption = tuple(relations)
    added_key: frozenset[str] | None = None

    if not relation_contains_key(universe_set, cover, relations):
        key = find_candidate_keys_pruned(universe_set, cover)[0]
        added_key = key
        relations.append(key)
        relations = _remove_subsumed_relations(relations)

    final_relations = tuple(sorted(relations, key=lambda rel: (len(rel), tuple(sorted(rel)))))
    return SynthesisTrace(
        universe=universe_set,
        original_fds=original_fds,
        minimal_cover=cover,
        generated_relations=generated,
        removed_subsumed_relations=removed,
        relations_after_subsumption=after_subsumption,
        added_key_relation=added_key,
        final_relations=final_relations,
    )


def relation_contains_key(
    universe: Iterable[str],
    fds: Iterable[FD],
    relations: Iterable[Iterable[str]],
) -> bool:
    """Return whether any relation contains a candidate key for universe."""

    universe_set = frozenset(universe)
    rules = tuple(fds)
    validate_universe(universe_set, rules)
    keys = find_candidate_keys_pruned(universe_set, rules)
    relation_sets = [frozenset(relation) for relation in relations]
    return any(key <= relation for key in keys for relation in relation_sets)


def is_lossless_binary_decomposition(
    universe: Iterable[str],
    fds: Iterable[FD],
    left: Iterable[str],
    right: Iterable[str],
) -> bool:
    """Return whether a binary decomposition is lossless under FDs.

    For R decomposed into R1 and R2, the test is lossless iff
    (R1 intersection R2)+ contains R1 or R2.
    """

    universe_set = frozenset(universe)
    rules = tuple(fds)
    left_set = frozenset(left)
    right_set = frozenset(right)
    validate_universe(universe_set, rules)
    validate_attrs_subset(universe_set, left_set)
    validate_attrs_subset(universe_set, right_set)
    if left_set | right_set != universe_set:
        raise ValueError("binary decomposition relations must cover universe")

    shared = left_set & right_set
    if not shared:
        return False

    shared_closure = closure(shared, rules)
    return left_set <= shared_closure or right_set <= shared_closure


def project_fds(
    universe: Iterable[str],
    fds: Iterable[FD],
    relation: Iterable[str],
) -> list[FD]:
    """Project F+ onto one relation by exhaustive small-schema enumeration."""

    universe_set = frozenset(universe)
    rules = tuple(fds)
    relation_set = frozenset(relation)
    validate_universe(universe_set, rules)
    validate_attrs_subset(universe_set, relation_set)

    projected: list[FD] = []
    attrs = tuple(sorted(relation_set))
    for size in range(1, len(attrs) + 1):
        for lhs in combinations(attrs, size):
            lhs_set = frozenset(lhs)
            inferred = closure(lhs_set, rules) & relation_set
            for rhs in sorted(inferred - lhs_set):
                projected.append(FD(lhs_set, rhs))

    if not projected:
        return []
    return minimal_cover(relation_set, projected)


def preserves_dependencies(
    universe: Iterable[str],
    fds: Iterable[FD],
    relations: Iterable[Iterable[str]],
) -> bool:
    """Return whether a decomposition preserves the given FD set.

    The check computes exact projections by enumeration, so it is intentionally
    limited to small teaching examples.
    """

    universe_set = frozenset(universe)
    rules = tuple(fds)
    relation_sets = tuple(frozenset(relation) for relation in relations)
    validate_universe(universe_set, rules)
    for relation in relation_sets:
        validate_attrs_subset(universe_set, relation)
    if not relation_sets:
        raise ValueError("decomposition must contain at least one relation")
    if frozenset().union(*relation_sets) != universe_set:
        raise ValueError("decomposition relations must cover universe")

    projected: list[FD] = []
    for relation in relation_sets:
        projected.extend(project_fds(universe_set, rules, relation))

    return all(fd.rhs in closure(fd.lhs, projected) for fd in rules)


def _minimize_lhs(fds: list[FD]) -> list[FD]:
    cover = list(fds)
    changed = True
    while changed:
        changed = False
        for index, fd in enumerate(tuple(cover)):
            for attr in sorted(fd.lhs):
                reduced_lhs = fd.lhs - {attr}
                if not reduced_lhs:
                    continue
                if fd.rhs in closure(reduced_lhs, cover):
                    cover[index] = FD(frozenset(reduced_lhs), fd.rhs)
                    cover = _unique_fds(cover)
                    changed = True
                    break
            if changed:
                break
    return cover


def _remove_redundant_fds(fds: list[FD]) -> list[FD]:
    cover = list(fds)
    changed = True
    while changed:
        changed = False
        for index, fd in enumerate(tuple(cover)):
            others = cover[:index] + cover[index + 1 :]
            if fd.rhs in closure(fd.lhs, others):
                del cover[index]
                changed = True
                break
    return cover


def _remove_subsumed_relations(
    relations: Iterable[frozenset[str]],
) -> list[frozenset[str]]:
    relation_sets = sorted(
        set(relations),
        key=lambda rel: (len(rel), tuple(sorted(rel))),
    )
    return [
        relation
        for relation in relation_sets
        if not any(relation < other for other in relation_sets)
    ]


def _unique_fds(fds: Iterable[FD]) -> list[FD]:
    return list(dict.fromkeys(fds))


def _sort_fds(fds: Iterable[FD]) -> list[FD]:
    return sorted(fds, key=lambda fd: (tuple(sorted(fd.lhs)), fd.rhs))


def _sort_relations(relations: Iterable[frozenset[str]]) -> list[frozenset[str]]:
    return sorted(set(relations), key=lambda rel: (len(rel), tuple(sorted(rel))))
