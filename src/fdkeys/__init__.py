"""Small helpers for functional-dependency closure and candidate keys."""

from fdkeys.closure import closure
from fdkeys.keys import find_candidate_keys, is_candidate_key, is_superkey
from fdkeys.model import FD, make_fd
from fdkeys.unary_graph import (
    build_unary_graph,
    find_candidate_keys_unary_scc,
    is_unary_fds,
)

__all__ = [
    "FD",
    "build_unary_graph",
    "closure",
    "find_candidate_keys",
    "find_candidate_keys_unary_scc",
    "is_candidate_key",
    "is_superkey",
    "is_unary_fds",
    "make_fd",
]
