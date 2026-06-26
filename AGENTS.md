# Project Instructions

- This is an exploratory/teaching repository about functional dependencies, candidate keys, and graph or hypergraph interpretations of FD closure.
- Use Python 3.11+.
- Use `pytest` for tests.
- Avoid heavy dependencies.
- Represent attributes as strings.
- Represent a single-RHS FD as a small typed object, for example `FD(lhs=frozenset({"A", "B"}), rhs="C")`.
- Keep code simple and readable.
- Do not claim novelty; this repo makes known ideas concrete with code, tests, and proof notes.
- Always run `py -3.12 -m pytest` before reporting completion in this repo.
