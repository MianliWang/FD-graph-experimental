from fdkeys import FD, find_candidate_keys, is_candidate_key, is_superkey


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
