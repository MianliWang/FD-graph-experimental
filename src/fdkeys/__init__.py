"""Small helpers for functional-dependency closure and candidate keys."""

from fdkeys.closure import closure
from fdkeys.decomposition import (
    GeneratedRelation,
    SynthesisTrace,
    decompose_bcnf,
    explain_3nf_synthesis,
    is_lossless_binary_decomposition,
    minimal_cover,
    preserves_dependencies,
    project_fds,
    relation_contains_key,
    synthesize_3nf,
)
from fdkeys.keys import (
    find_candidate_keys,
    find_candidate_keys_pruned,
    is_candidate_key,
    is_superkey,
)
from fdkeys.model import FD, make_fd
from fdkeys.storage import estimate_storage_bytes, relation_width
from fdkeys.unary_graph import (
    build_unary_graph,
    find_candidate_keys_unary_scc,
    is_unary_fds,
)
from fdkeys.visualization import (
    fd_hypergraph_dot,
    fd_hypergraph_svg,
    format_fd,
    format_relation,
)

__all__ = [
    "FD",
    "GeneratedRelation",
    "SynthesisTrace",
    "build_unary_graph",
    "closure",
    "decompose_bcnf",
    "estimate_storage_bytes",
    "explain_3nf_synthesis",
    "fd_hypergraph_dot",
    "fd_hypergraph_svg",
    "find_candidate_keys",
    "find_candidate_keys_pruned",
    "find_candidate_keys_unary_scc",
    "format_fd",
    "format_relation",
    "is_lossless_binary_decomposition",
    "is_candidate_key",
    "is_superkey",
    "is_unary_fds",
    "make_fd",
    "minimal_cover",
    "preserves_dependencies",
    "project_fds",
    "relation_contains_key",
    "relation_width",
    "synthesize_3nf",
]
