import pytest

from fdkeys import (
    FD,
    decompose_bcnf,
    explain_3nf_synthesis,
    is_lossless_binary_decomposition,
    minimal_cover,
    preserves_dependencies,
    project_fds,
    relation_contains_key,
    synthesize_3nf,
)


def test_minimal_cover_removes_extraneous_lhs_attribute() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [
        FD(frozenset({"A", "B"}), "C"),
        FD(frozenset({"A"}), "B"),
    ]

    assert set(minimal_cover(universe, fds)) == {
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
    }


def test_minimal_cover_removes_extraneous_attributes_from_ternary_lhs() -> None:
    universe = frozenset({"A", "B", "C", "D"})
    fds = [
        FD(frozenset({"A", "B", "C"}), "D"),
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
    ]

    assert set(minimal_cover(universe, fds)) == {
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
        FD(frozenset({"A"}), "D"),
    }


def test_minimal_cover_removes_redundant_fd() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"B"}), "C"),
        FD(frozenset({"A"}), "C"),
    ]

    assert set(minimal_cover(universe, fds)) == {
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"B"}), "C"),
    }


def test_synthesize_3nf_adds_key_relation_when_needed() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [FD(frozenset({"A"}), "B")]

    decomposition = synthesize_3nf(universe, fds)

    assert set(decomposition) == {
        frozenset({"A", "B"}),
        frozenset({"A", "C"}),
    }
    assert relation_contains_key(universe, fds, decomposition)


def test_synthesize_3nf_groups_same_lhs_dependencies() -> None:
    universe = frozenset({"A", "B", "C", "D"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
        FD(frozenset({"A"}), "D"),
    ]

    assert synthesize_3nf(universe, fds) == [
        frozenset({"A", "B", "C", "D"}),
    ]


def test_synthesize_3nf_keeps_ternary_determinant_together() -> None:
    universe = frozenset({"A", "B", "C", "D", "E", "F"})
    fds = [
        FD(frozenset({"A", "B", "C"}), "D"),
        FD(frozenset({"A", "B", "C"}), "E"),
        FD(frozenset({"D"}), "F"),
    ]

    assert set(synthesize_3nf(universe, fds)) == {
        frozenset({"A", "B", "C", "D", "E"}),
        frozenset({"D", "F"}),
    }


def test_synthesize_3nf_chain_example_preserves_cover_dependencies() -> None:
    universe = frozenset({"A", "B", "C", "D"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"B"}), "C"),
        FD(frozenset({"C"}), "D"),
    ]

    cover = minimal_cover(universe, fds)
    decomposition = synthesize_3nf(universe, fds)

    assert set(decomposition) == {
        frozenset({"A", "B"}),
        frozenset({"B", "C"}),
        frozenset({"C", "D"}),
    }
    for fd in cover:
        assert any(fd.lhs | frozenset({fd.rhs}) <= rel for rel in decomposition)


def test_synthesize_3nf_without_fds_returns_universe_relation() -> None:
    universe = frozenset({"A", "B", "C"})

    assert synthesize_3nf(universe, []) == [universe]


def test_synthesize_3nf_validates_fd_attributes() -> None:
    with pytest.raises(ValueError, match="outside universe: Z"):
        synthesize_3nf({"A"}, [FD(frozenset({"A"}), "Z")])


def test_explain_3nf_synthesis_matches_synthesize_3nf() -> None:
    universe = frozenset({"A", "B", "C", "D", "E", "F", "G"})
    fds = [
        FD(frozenset({"A", "B", "C"}), "D"),
        FD(frozenset({"D", "E"}), "F"),
        FD(frozenset({"F"}), "G"),
    ]

    trace = explain_3nf_synthesis(universe, fds)

    assert list(trace.final_relations) == synthesize_3nf(universe, fds)
    assert trace.original_fds == tuple(fds)
    assert trace.minimal_cover == tuple(minimal_cover(universe, fds))


def test_explain_3nf_synthesis_records_added_key_relation() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [FD(frozenset({"A"}), "B")]

    trace = explain_3nf_synthesis(universe, fds)

    assert trace.added_key_relation == frozenset({"A", "C"})
    assert frozenset({"A", "C"}) in trace.final_relations


def test_explain_3nf_synthesis_skips_key_relation_when_one_is_present() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"B"}), "C"),
    ]

    trace = explain_3nf_synthesis(universe, fds)

    assert trace.added_key_relation is None
    assert set(trace.final_relations) == {
        frozenset({"A", "B"}),
        frozenset({"B", "C"}),
    }


def test_explain_3nf_synthesis_records_removed_subsumed_relations() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"B", "C"}), "A"),
    ]

    trace = explain_3nf_synthesis(universe, fds)

    assert trace.removed_subsumed_relations == (frozenset({"A", "B"}),)
    assert trace.relations_after_subsumption == (frozenset({"A", "B", "C"}),)


def test_project_fds_finds_implied_dependencies_inside_relation() -> None:
    universe = frozenset({"A", "B", "C", "D"})
    fds = [
        FD(frozenset({"A", "B"}), "C"),
        FD(frozenset({"C"}), "D"),
    ]

    assert set(project_fds(universe, fds, {"A", "B", "D"})) == {
        FD(frozenset({"A", "B"}), "D"),
    }


def test_bcnf_decomposition_can_lose_dependency_preservation() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [
        FD(frozenset({"A", "B"}), "C"),
        FD(frozenset({"C"}), "B"),
    ]

    bcnf = decompose_bcnf(universe, fds)

    assert set(bcnf) == {
        frozenset({"A", "C"}),
        frozenset({"B", "C"}),
    }
    assert is_lossless_binary_decomposition(
        universe,
        fds,
        frozenset({"A", "C"}),
        frozenset({"B", "C"}),
    )
    assert not preserves_dependencies(universe, fds, bcnf)
    assert preserves_dependencies(universe, fds, synthesize_3nf(universe, fds))


def test_bcnf_keeps_relation_when_every_projected_fd_has_superkey_lhs() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
    ]

    assert decompose_bcnf(universe, fds) == [universe]


def test_lossless_binary_decomposition_rejects_non_covering_relations() -> None:
    with pytest.raises(ValueError, match="must cover universe"):
        is_lossless_binary_decomposition(
            {"A", "B", "C"},
            [FD(frozenset({"A"}), "B")],
            {"A", "B"},
            {"B"},
        )


def test_dependency_preservation_rejects_empty_decomposition() -> None:
    with pytest.raises(ValueError, match="at least one relation"):
        preserves_dependencies({"A", "B"}, [FD(frozenset({"A"}), "B")], [])
