from fdkeys import FD, closure


def test_composite_lhs_requires_all_attributes() -> None:
    fds = [FD(frozenset({"A", "B"}), "C")]

    assert "C" not in closure({"A"}, fds)
    assert "C" not in closure({"B"}, fds)
    assert "C" in closure({"A", "B"}, fds)
