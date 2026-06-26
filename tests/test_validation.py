import pytest

from fdkeys import (
    FD,
    find_candidate_keys,
    find_candidate_keys_unary_scc,
    is_candidate_key,
    is_superkey,
)


def test_fd_rhs_outside_universe_raises_value_error() -> None:
    with pytest.raises(ValueError, match="outside universe: Z"):
        find_candidate_keys({"A"}, [FD(frozenset({"A"}), "Z")])


def test_fd_lhs_outside_universe_raises_value_error() -> None:
    with pytest.raises(ValueError, match="outside universe: Z"):
        find_candidate_keys({"A"}, [FD(frozenset({"Z"}), "A")])


@pytest.mark.parametrize("function", [is_superkey, is_candidate_key])
def test_attrs_outside_universe_raise_value_error(function) -> None:
    with pytest.raises(ValueError, match="attrs contains attributes outside universe: Z"):
        function({"A", "B"}, [FD(frozenset({"A"}), "B")], {"A", "Z"})


def test_unary_scc_validates_fd_attributes_against_universe() -> None:
    with pytest.raises(ValueError, match="outside universe: Z"):
        find_candidate_keys_unary_scc({"A"}, [FD(frozenset({"A"}), "Z")])
