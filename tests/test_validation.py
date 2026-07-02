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


def test_fd_validation_reports_all_outside_attributes() -> None:
    with pytest.raises(ValueError, match="outside universe: Y, Z"):
        find_candidate_keys(
            {"A", "B"},
            [FD(frozenset({"A", "Z"}), "Y")],
        )


@pytest.mark.parametrize("function", [find_candidate_keys, is_superkey, is_candidate_key])
def test_candidate_key_entry_points_validate_fd_attributes(function) -> None:
    universe = {"A", "B"}
    fds = [FD(frozenset({"A"}), "Z")]

    with pytest.raises(ValueError, match="outside universe: Z"):
        if function is find_candidate_keys:
            function(universe, fds)
        else:
            function(universe, fds, {"A"})


@pytest.mark.parametrize("function", [is_superkey, is_candidate_key])
def test_attrs_outside_universe_raise_value_error(function) -> None:
    with pytest.raises(ValueError, match="attrs contains attributes outside universe: Z"):
        function({"A", "B"}, [FD(frozenset({"A"}), "B")], {"A", "Z"})


def test_universe_must_contain_only_non_empty_strings() -> None:
    with pytest.raises(
        ValueError,
        match="universe must contain only non-empty string attributes",
    ):
        find_candidate_keys({"A", ""}, [])


def test_unary_scc_validates_fd_attributes_against_universe() -> None:
    with pytest.raises(ValueError, match="outside universe: Z"):
        find_candidate_keys_unary_scc({"A"}, [FD(frozenset({"A"}), "Z")])


def test_unary_scc_validates_universe_before_unary_shape() -> None:
    with pytest.raises(ValueError, match="outside universe: Z"):
        find_candidate_keys_unary_scc({"A"}, [FD(frozenset({"A", "Z"}), "A")])
