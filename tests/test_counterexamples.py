from fdkeys import FD, closure


def test_composite_lhs_requires_all_attributes() -> None:
    fds = [FD(frozenset({"A", "B"}), "C")]

    assert "C" not in closure({"A"}, fds)
    assert "C" not in closure({"B"}, fds)
    assert "C" in closure({"A", "B"}, fds)


def test_ternary_lhs_requires_all_three_attributes() -> None:
    fds = [FD(frozenset({"A", "B", "C"}), "D")]

    assert "D" not in closure({"A", "B"}, fds)
    assert "D" not in closure({"A", "C"}, fds)
    assert "D" not in closure({"B", "C"}, fds)
    assert "D" in closure({"A", "B", "C"}, fds)
