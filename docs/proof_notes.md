# Proof Notes

These are proof sketches for the small implementations in `src/fdkeys`.

## 1. Closure

The closure algorithm starts with a seed set of attributes and repeatedly
applies any FD whose left-hand side is already known. It only adds an attribute
when an FD justifies it, so every added attribute is derivable from the seed.

The loop stops because there are only finitely many FD right-hand-side
attributes to add. At the fixed point, no FD can add anything new. Therefore
the result is closed under the given FDs. Any valid derivation from the seed can
be replayed step by step by the loop, so the computed set contains exactly the
attributes implied by the FDs from that starting set.

## 2. Baseline Candidate-Key Enumeration

An attribute that never appears on the right-hand side of an FD cannot be
derived from other attributes in this finite rule system. Therefore every
candidate key must contain all attributes in `universe - RHS`.

The baseline search starts with those mandatory attributes and enumerates
subsets of the remaining optional attributes in increasing size. A set is kept
only when its closure is the whole universe. Once a key is found, every superset
of it is skipped, because supersets cannot be inclusion-minimal.

Every returned set is therefore a superkey and has no previously found subset
that is also a superkey. Every inclusion-minimal superkey contains the mandatory
attributes, so it appears somewhere in this enumeration before any of its
proper supersets. Thus the algorithm returns exactly the inclusion-minimal
superkeys.

## 3. Unary-FD SCC Rule

When every FD has one attribute on the left, each FD is an ordinary directed
edge. Closure from a seed set is graph reachability from those seed vertices.

Inside one strongly connected component, every attribute reaches every other
attribute. Choosing one representative from a source SCC is enough to derive
the whole SCC. It is also necessary: because a source SCC has no incoming edge
from another SCC, no seed outside it can reach it.

The condensation graph of SCCs is a DAG, and every node in a finite DAG is
reachable from at least one source. Therefore choosing one attribute from each
source SCC reaches every SCC, hence every attribute. Choosing fewer cannot
reach at least one source SCC, and choosing more than one from the same source
SCC is not minimal. The candidate keys are exactly the sets formed by one
representative from each source SCC.
