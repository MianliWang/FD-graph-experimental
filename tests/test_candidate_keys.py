import random

from fdkeys import (
    FD,
    find_candidate_keys,
    find_candidate_keys_pruned,
    is_candidate_key,
    is_superkey,
)


def test_candidate_keys_for_closure_example() -> None:
    universe = frozenset({"A", "B", "C", "G", "H", "I"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
        FD(frozenset({"C", "G"}), "H"),
        FD(frozenset({"C", "G"}), "I"),
        FD(frozenset({"B"}), "H"),
    ]

    assert find_candidate_keys(universe, fds) == [frozenset({"A", "G"})]


def test_superkey_that_is_not_minimal_is_not_candidate_key() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"B"}), "C"),
    ]

    assert is_superkey(universe, fds, {"A", "B"})
    assert not is_candidate_key(universe, fds, {"A", "B"})
    assert is_candidate_key(universe, fds, {"A"})


def test_finds_all_inclusion_minimal_keys_not_only_smallest_keys() -> None:
    universe = frozenset({"A", "B", "C"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
        FD(frozenset({"B", "C"}), "A"),
    ]

    assert set(find_candidate_keys(universe, fds)) == {
        frozenset({"A"}),
        frozenset({"B", "C"}),
    }


def test_pruned_search_matches_baseline_on_composite_lhs_example() -> None:
    universe = frozenset({"A", "B", "C", "D", "E", "F", "G", "H"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"C"}), "D"),
        FD(frozenset({"B", "D"}), "E"),
        FD(frozenset({"E"}), "F"),
        FD(frozenset({"G"}), "H"),
        FD(frozenset({"H"}), "G"),
    ]

    expected = {frozenset({"A", "C", "G"}), frozenset({"A", "C", "H"})}

    assert set(find_candidate_keys(universe, fds)) == expected
    assert set(find_candidate_keys_pruned(universe, fds)) == expected


def test_candidate_keys_with_ternary_lhs_horn_rule() -> None:
    universe = frozenset({"A", "B", "C", "D", "E", "F", "G"})
    fds = [
        FD(frozenset({"A", "B", "C"}), "D"),
        FD(frozenset({"D", "E"}), "F"),
        FD(frozenset({"F"}), "G"),
    ]

    expected = {frozenset({"A", "B", "C", "E"})}

    assert set(find_candidate_keys(universe, fds)) == expected
    assert set(find_candidate_keys_pruned(universe, fds)) == expected
    assert is_candidate_key(universe, fds, {"A", "B", "C", "E"})
    assert not is_candidate_key(universe, fds, {"A", "B", "E"})


def test_candidate_keys_with_quaternary_lhs_horn_rule() -> None:
    universe = frozenset({"A", "B", "C", "D", "E", "F", "G"})
    fds = [
        FD(frozenset({"A", "B", "C", "D"}), "E"),
        FD(frozenset({"E"}), "F"),
        FD(frozenset({"F"}), "G"),
    ]

    expected = {frozenset({"A", "B", "C", "D"})}

    assert set(find_candidate_keys(universe, fds)) == expected
    assert set(find_candidate_keys_pruned(universe, fds)) == expected


def test_pruned_search_handles_minimal_keys_of_different_sizes() -> None:
    universe = frozenset({"A", "B", "C", "D"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
        FD(frozenset({"A"}), "D"),
        FD(frozenset({"B", "D"}), "A"),
    ]

    assert set(find_candidate_keys_pruned(universe, fds)) == {
        frozenset({"A"}),
        frozenset({"B", "D"}),
    }


def test_pruned_search_matches_baseline_on_random_small_fd_sets() -> None:
    rng = random.Random(2027)

    for _ in range(60):
        attrs = [chr(ord("A") + index) for index in range(rng.randint(1, 6))]
        universe = frozenset(attrs)
        fds = []
        for _ in range(rng.randint(0, len(attrs) * 3)):
            lhs_size = rng.randint(1, min(4, len(attrs)))
            lhs = frozenset(rng.sample(attrs, lhs_size))
            rhs = rng.choice(attrs)
            fds.append(FD(lhs, rhs))

        assert set(find_candidate_keys_pruned(universe, fds)) == set(
            find_candidate_keys(universe, fds)
        )
