# Experiment Notes

## 1. Why `AB -> C` is not ordinary graph reachability

The dependency `AB -> C` has AND-semantics: `C` follows only after both `A` and
`B` are present. If we replaced it with ordinary graph edges `A -> C` and
`B -> C`, then either `A` alone or `B` alone would reach `C`, which changes the
meaning of the dependency.

This is the key counterexample for treating general FDs as a plain directed
graph.

## 2. General FDs as Horn Rules or Hyperedges

A general FD such as `AB -> C` is naturally a Horn rule:

```text
A and B imply C
```

Equivalently, it can be viewed as a directed hyperedge from the set `{A, B}` to
the attribute `C`. The whole left-hand side must be available before the rule
fires.

## 3. Why Unary FDs Collapse to Graph Reachability

For unary FDs, every rule has one prerequisite, such as `A -> B`. There is no
AND condition left to encode, so each FD is just a directed edge. Attribute
closure becomes the set of vertices reachable from the seed attributes.

That is why SCC reasoning applies only in this special case: source SCCs in the
condensation DAG are exactly the components that must receive an initial seed.
