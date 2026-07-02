# fd-key-graph-experiments

Small Python experiments and proof notes about general functional dependencies,
candidate keys, and graph or hypergraph interpretations of FD closure.

This repository is not claiming a new algorithmic result. The goal is to make
the ideas concrete with readable code, focused tests, and short notes suitable
for discussion or teaching.

For a compact professor-facing overview, see
[docs/professor_note.md](docs/professor_note.md).
For an executable walkthrough, see
[notebooks/general_fd_decomposition_walkthrough.ipynb](notebooks/general_fd_decomposition_walkthrough.ipynb).
For normalization tradeoffs, see
[notebooks/normalization_tradeoffs.ipynb](notebooks/normalization_tradeoffs.ipynb).

## Core question

Can candidate-key discovery be understood as finding an inclusion-minimal
initial set of attributes whose functional-dependency closure derives all
attributes in the schema?

In this repo, a candidate key is treated as a minimal seed set `K` such that
`closure(K, fds)` contains the whole universe of attributes.

Universe-aware public functions validate that FDs, and proposed key attributes
where applicable, mention only attributes in the declared universe.

The package also includes small 3NF and BCNF teaching helpers to show how
candidate keys connect to schema decomposition.

## Why general FDs are not ordinary graph reachability

For a dependency such as `AB -> C`, both `A` and `B` are required together.
Replacing it with ordinary graph edges `A -> C` and `B -> C` would be unsound:
it would incorrectly let either `A` alone or `B` alone derive `C`.

General functional dependencies are the main focus of this repository. They
are better viewed as Horn rules or directed hyperedges: a set of prerequisites
on the left derives one attribute on the right.

## Unary-FD special case

When every FD has a singleton left-hand side, for example `A -> B`, closure is
ordinary directed graph reachability. In that special case, strongly connected
components matter: candidate keys can be formed by choosing one representative
attribute from each source SCC in the condensation DAG.

## Running tests

Use Python 3.12 in this checkout:

```bash
py -3.12 -m pytest
```

The default `python` on a given machine may point to another interpreter. In
this workspace, `python -m pytest` fails only because that interpreter does not
have `pytest` installed.

## Reference

A classic reference is Ausiello, D'Atri, and Sacca, "Graph Algorithms for
Functional Dependency Manipulation," JACM 1983.

That paper covers broader FD-graph manipulation, including closure, minimal
covers, and 3NF synthesis. This repository focuses more narrowly on
candidate-key experiments and the distinction between general FD closure and
the unary-FD graph case.
