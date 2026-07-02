from fdkeys import (
    FD,
    fd_hypergraph_dot,
    fd_hypergraph_svg,
    format_fd,
    format_relation,
)


def test_format_relation_sorts_attributes() -> None:
    assert format_relation({"C", "A", "B"}) == "{A, B, C}"


def test_format_fd_sorts_lhs_attributes() -> None:
    fd = FD(frozenset({"C", "A", "B"}), "D")

    assert format_fd(fd) == "{A, B, C} -> D"


def test_fd_hypergraph_dot_represents_ternary_lhs_with_one_rule_node() -> None:
    dot = fd_hypergraph_dot([FD(frozenset({"A", "B", "C"}), "D")])

    assert '"rule_1" [shape=box, label="{A, B, C} -> D"];' in dot
    assert '"A" -> "rule_1";' in dot
    assert '"B" -> "rule_1";' in dot
    assert '"C" -> "rule_1";' in dot
    assert '"rule_1" -> "D";' in dot


def test_fd_hypergraph_dot_output_is_stable() -> None:
    fds = [
        FD(frozenset({"D", "E"}), "F"),
        FD(frozenset({"A", "B", "C"}), "D"),
    ]

    assert fd_hypergraph_dot(fds) == "\n".join(
        [
            "digraph fd_hypergraph {",
            "  rankdir=LR;",
            '  node [fontname="Arial"];',
            '  edge [fontname="Arial"];',
            '  "A" [shape=ellipse];',
            '  "B" [shape=ellipse];',
            '  "C" [shape=ellipse];',
            '  "D" [shape=ellipse];',
            '  "E" [shape=ellipse];',
            '  "F" [shape=ellipse];',
            '  "rule_1" [shape=box, label="{D, E} -> F"];',
            '  "D" -> "rule_1";',
            '  "E" -> "rule_1";',
            '  "rule_1" -> "F";',
            '  "rule_2" [shape=box, label="{A, B, C} -> D"];',
            '  "A" -> "rule_2";',
            '  "B" -> "rule_2";',
            '  "C" -> "rule_2";',
            '  "rule_2" -> "D";',
            "}",
        ]
    )


def test_fd_hypergraph_svg_represents_ternary_lhs_with_one_rule_node() -> None:
    svg = fd_hypergraph_svg([FD(frozenset({"A", "B", "C"}), "D")])

    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert '<g id="rule-1">' in svg
    assert "FD 1: {A, B, C} -&gt; D" in svg
    assert 'data-from="A" data-to="rule-1"' in svg
    assert 'data-from="B" data-to="rule-1"' in svg
    assert 'data-from="C" data-to="rule-1"' in svg
    assert 'data-from="rule-1" data-to="D"' in svg


def test_fd_hypergraph_svg_handles_empty_fd_set() -> None:
    svg = fd_hypergraph_svg([])

    assert "No functional dependencies" in svg
