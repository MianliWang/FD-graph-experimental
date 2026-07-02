import random

import pytest

from fdkeys import FD, find_candidate_keys, find_candidate_keys_unary_scc


def test_unary_scc_reasoning_agrees_with_baseline() -> None:
    universe = frozenset({"A", "B", "C", "D"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"B"}), "A"),
        FD(frozenset({"C"}), "D"),
    ]

    expected = {frozenset({"A", "C"}), frozenset({"B", "C"})}

    assert set(find_candidate_keys_unary_scc(universe, fds)) == expected
    assert set(find_candidate_keys_unary_scc(universe, fds)) == set(
        find_candidate_keys(universe, fds)
    )


def test_unary_scc_complex_condensation_dag_sources() -> None:
    universe = frozenset({"A", "B", "C", "D", "E", "F", "G", "H", "I"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"B"}), "A"),
        FD(frozenset({"C"}), "D"),
        FD(frozenset({"D"}), "C"),
        FD(frozenset({"A"}), "E"),
        FD(frozenset({"C"}), "E"),
        FD(frozenset({"E"}), "F"),
        FD(frozenset({"F"}), "E"),
        FD(frozenset({"F"}), "G"),
        FD(frozenset({"G"}), "I"),
        FD(frozenset({"H"}), "I"),
    ]

    expected = {
        frozenset({"A", "C", "H"}),
        frozenset({"A", "D", "H"}),
        frozenset({"B", "C", "H"}),
        frozenset({"B", "D", "H"}),
    }

    assert set(find_candidate_keys_unary_scc(universe, fds)) == expected
    assert set(find_candidate_keys_unary_scc(universe, fds)) == set(
        find_candidate_keys(universe, fds)
    )


def test_unary_scc_rejects_non_unary_fds() -> None:
    with pytest.raises(ValueError):
        find_candidate_keys_unary_scc(
            {"A", "B", "C"},
            [FD(frozenset({"A", "B"}), "C")],
        )


def test_randomized_small_unary_examples_match_baseline() -> None:
    rng = random.Random(2026)

    for _ in range(40):
        attrs = [chr(ord("A") + index) for index in range(rng.randint(1, 5))]
        universe = frozenset(attrs)
        fds = {
            FD(frozenset({rng.choice(attrs)}), rng.choice(attrs))
            for _ in range(rng.randint(0, len(attrs) * 3))
        }

        assert set(find_candidate_keys_unary_scc(universe, fds)) == set(
            find_candidate_keys(universe, fds)
        )
