from __future__ import annotations

from collections.abc import Iterable
from html import escape

from fdkeys.model import FD


def format_relation(attrs: Iterable[str]) -> str:
    """Format a relation/attribute set with stable ordering."""

    return "{" + ", ".join(sorted(attrs)) + "}"


def format_fd(fd: FD) -> str:
    """Format a single-RHS FD with stable LHS ordering."""

    return f"{format_relation(fd.lhs)} -> {fd.rhs}"


def fd_hypergraph_dot(fds: Iterable[FD]) -> str:
    """Return a Graphviz DOT representation of FDs as rule nodes."""

    rules = tuple(fds)
    lines = [
        "digraph fd_hypergraph {",
        "  rankdir=LR;",
        '  node [fontname="Arial"];',
        '  edge [fontname="Arial"];',
    ]

    attrs = sorted({attr for fd in rules for attr in fd.lhs | frozenset({fd.rhs})})
    for attr in attrs:
        lines.append(f'  "{_dot_escape(attr)}" [shape=ellipse];')

    for index, fd in enumerate(rules, start=1):
        rule_id = f"rule_{index}"
        label = format_fd(fd)
        lines.append(
            f'  "{rule_id}" [shape=box, label="{_dot_escape(label)}"];'
        )
        for attr in sorted(fd.lhs):
            lines.append(f'  "{_dot_escape(attr)}" -> "{rule_id}";')
        lines.append(f'  "{rule_id}" -> "{_dot_escape(fd.rhs)}";')

    lines.append("}")
    return "\n".join(lines)


def fd_hypergraph_svg(fds: Iterable[FD]) -> str:
    """Return a dependency-free SVG sketch of FDs as rule nodes."""

    rules = tuple(fds)
    width = 620
    if not rules:
        return "\n".join(
            [
                '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="120" viewBox="0 0 360 120">',
                "  <style>text { font-family: Arial, sans-serif; font-size: 14px; }</style>",
                '  <text x="30" y="65">No functional dependencies</text>',
                "</svg>",
            ]
        )

    attr_gap = 42
    min_row_height = 120
    row_heights = [
        max(min_row_height, (len(fd.lhs) - 1) * attr_gap + 86)
        for fd in rules
    ]
    height = sum(row_heights) + 40
    lhs_x = 110
    rule_x = 310
    rhs_x = 520
    rule_width = 150
    rule_height = 42

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "  <defs>",
        '    <marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">',
        '      <path d="M0,0 L10,4 L0,8 Z" fill="#334155" />',
        "    </marker>",
        "  </defs>",
        "  <style>",
        "    text { font-family: Arial, sans-serif; font-size: 13px; fill: #0f172a; }",
        "    .attr { fill: #ecfeff; stroke: #0891b2; stroke-width: 1.5; }",
        "    .rule { fill: #f8fafc; stroke: #475569; stroke-width: 1.5; }",
        "    .edge { stroke: #334155; stroke-width: 1.4; fill: none; marker-end: url(#arrow); }",
        "    .caption { font-size: 12px; fill: #475569; }",
        "  </style>",
    ]

    y_cursor = 20
    for index, fd in enumerate(rules, start=1):
        row_height = row_heights[index - 1]
        row_y = y_cursor + row_height / 2
        rule_id = f"rule-{index}"
        lhs_attrs = sorted(fd.lhs)
        lhs_start_y = row_y - ((len(lhs_attrs) - 1) * attr_gap / 2)

        lines.append(f'  <g id="{rule_id}">')
        lines.append(
            f'    <text class="caption" x="24" y="{row_y - row_height / 2 + 18:.1f}">FD {index}: {_xml_escape(format_fd(fd))}</text>'
        )
        lines.append(
            f'    <rect class="rule" x="{rule_x - rule_width / 2}" y="{row_y - rule_height / 2:.1f}" width="{rule_width}" height="{rule_height}" rx="6" />'
        )
        lines.append(
            f'    <text text-anchor="middle" dominant-baseline="middle" x="{rule_x}" y="{row_y:.1f}">{_xml_escape(format_fd(fd))}</text>'
        )

        for lhs_index, attr in enumerate(lhs_attrs):
            lhs_y = lhs_start_y + lhs_index * attr_gap
            lines.append(
                f'    <line class="edge" data-from="{_xml_escape(attr)}" data-to="{rule_id}" x1="{lhs_x + 30}" y1="{lhs_y:.1f}" x2="{rule_x - rule_width / 2 - 8}" y2="{row_y:.1f}" />'
            )
            _append_attr_node(lines, lhs_x, lhs_y, attr)

        lines.append(
            f'    <line class="edge" data-from="{rule_id}" data-to="{_xml_escape(fd.rhs)}" x1="{rule_x + rule_width / 2 + 8}" y1="{row_y:.1f}" x2="{rhs_x - 30}" y2="{row_y:.1f}" />'
        )
        _append_attr_node(lines, rhs_x, row_y, fd.rhs)
        lines.append("  </g>")
        y_cursor += row_height

    lines.append("</svg>")
    return "\n".join(lines)


def _dot_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _xml_escape(text: str) -> str:
    return escape(text, quote=True)


def _append_attr_node(lines: list[str], x: float, y: float, label: str) -> None:
    lines.append(f'    <circle class="attr" cx="{x}" cy="{y:.1f}" r="28" />')
    lines.append(
        f'    <text text-anchor="middle" dominant-baseline="middle" x="{x}" y="{y:.1f}">{_xml_escape(label)}</text>'
    )
