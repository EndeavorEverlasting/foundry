"""Monkey-patch SQLModel's get_relationship_to to handle PEP-563 string annotations.

SQLModel 0.0.x doesn't parse string annotations like ``"list['Branch']"``
that arise from ``from __future__ import annotations`` in Python 3.13.
This conftest applies the patch before any test imports ``foundry_core.models``.
"""

from __future__ import annotations

import ast
from typing import Any

import sqlmodel.main as _sqlmodel_main


_original_get_relationship_to = _sqlmodel_main.get_relationship_to


def _patched_get_relationship_to(
    name: str,
    rel_info: Any,
    annotation: Any,
) -> Any:
    """Resolve string annotations that contain generic types (list[...], Optional[...])."""
    if isinstance(annotation, str):
        try:
            parsed = ast.parse(annotation, mode="eval")
        except SyntaxError:
            return annotation
        node = parsed.body
        if isinstance(node, ast.Subscript):
            value = node.value
            if isinstance(value, ast.Name) and value.id == "list":
                slice_node = node.slice
                if isinstance(slice_node, ast.Constant) and isinstance(
                    slice_node.value, str
                ):
                    return slice_node.value
                if isinstance(slice_node, ast.Name):
                    return slice_node.id
        # Also handle Union / Optional forms if they appear as strings
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            # X | None
            if isinstance(node.right, ast.Constant) and node.right.value is None:
                left = node.left
                if isinstance(left, ast.Name):
                    return left.id
                if isinstance(left, ast.Constant) and isinstance(left.value, str):
                    return left.value
    return _original_get_relationship_to(name, rel_info, annotation)


_sqlmodel_main.get_relationship_to = _patched_get_relationship_to
