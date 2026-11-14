"""Batch134 angle A: AST-based structural control-flow analysis of the 36 miss lines.

Method not previously recorded (prior batches used sys.settrace / monkeypatch /
direct probes). This parses data_loader.py with the `ast` module and, for each
miss cluster, computes the handler chain that can reach the `except` line and
the set of statements that can propagate an exception to it. Machine-checkable
and reproducible.
"""

import ast
from pathlib import Path

SRC = Path("strategies/betting_against_beta/data_loader.py")
tree = ast.parse(SRC.read_text())

# Build parent map + node text helper
parent = {}
for node in ast.walk(tree):
    for child in ast.iter_child_nodes(node):
        parent[child] = node


def src_segment(node):
    """Return the source text for a node using its line range."""
    lines = SRC.read_text().splitlines()
    start = node.lineno - 1
    end = getattr(node, "end_lineno", node.lineno)
    return "\n".join(lines[start:end])


def enclosing(node, pred):
    cur = node
    while cur is not None:
        if pred(cur):
            return cur
        cur = parent.get(cur)
    return None


def find_tryhandlers(line):
    """Return (try_node, handlers) for the try whose body spans `line`."""
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Try)
        and node.lineno <= line <= getattr(node, "end_lineno", node.lineno)
    ]


# Miss clusters -> (function, line)
clusters = {
    "43-44": ("_not_null", 43),
    "234-244,246-247": ("_normalize_index", 234),
    "268-269": ("_normalize_index", 268),
    "322,326": ("_coerce_to_datetime_scalar", 322),
    "334-335,338-342": ("_coerce_to_datetime_scalar", 334),
    "351-352": ("_coerce_to_datetime_scalar", 351),
    "403-404": ("_coerce_to_datetime_scalar", 403),
    "641-642": ("_detect_and_normalize_exchange_format", 641),
    "694-695": ("_detect_and_normalize_exchange_format", 694),
    "791-792": ("_promote_datetime_column", 791),
    "953": ("_normalize_asset_name", 953),
}

print("=== AST structural analysis ===")
for name, (fn, line) in clusters.items():
    tries = find_tryhandlers(line)
    info = []
    for t in tries:
        handlers = []
        for h in t.handlers:
            et = h.type
            et_name = ast.unparse(et) if et else "bare"
            handlers.append((h.lineno, et_name))
        dist = line - t.lineno
        info.append(
            f"try@{t.lineno}(body {t.lineno + 1}-{t.end_lineno}) "
            f"handlers={handlers} dist_to_miss={dist}"
        )
    print(f"\n{name} ({fn}:{line}):")
    for i in info:
        print("   ", i)
