from fdkeys import FD, closure


def test_closure_example_derives_all_attributes() -> None:
    universe = frozenset({"A", "B", "C", "G", "H", "I"})
    fds = [
        FD(frozenset({"A"}), "B"),
        FD(frozenset({"A"}), "C"),
        FD(frozenset({"C", "G"}), "H"),
        FD(frozenset({"C", "G"}), "I"),
        FD(frozenset({"B"}), "H"),
    ]

    assert closure({"A", "G"}, fds) == universe
