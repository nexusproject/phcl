"""
Minimal native HCL2 text renderer for PHCL blocks.

This backend is intentionally small and purpose-built:
- it renders PHCL's structural model directly to HCL2 text;
- it does not attempt to parse or normalize expressions;
- `Expression` values are treated as opaque HCL fragments.
"""

from phcl.core.expression import Expression, Reference
from phcl.core.nodes import Block, Node, class_to_label


def walk_block(block: Block):
    """
    Split a block body into scalar attributes and nested blocks.

    PHCL allows lists to contain either plain values or nested blocks.
    This pass normalizes that mixed representation into two ordered
    sequences the printer can render directly.
    """
    attrs = []
    nested = []

    for name, raw_value in block._phcl_attributes.items():
        value = block._phcl_normalize_attr(name, raw_value)
        if isinstance(value, Block):
            nested.append((name, value))
            continue

        if isinstance(value, list):
            items = []
            for item in value:
                if isinstance(item, Block):
                    nested.append((name, item))
                else:
                    items.append(item)
            if items:
                attrs.append((name, items))
            continue

        attrs.append((name, value))

    return attrs, nested


def quote_string(value: str) -> str:
    """Render a Python string as an HCL double-quoted string literal."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_value(value, level: int = 0, *, indent: str = "  ") -> str:
    """
    Render a Python value into HCL2 expression syntax.

    Supported values intentionally match the current PHCL core surface:
    scalars, lists, dicts, and raw `Expression` fragments.
    """
    if isinstance(value, Expression):
        # Expressions are already authored in HCL syntax and must not
        # be quoted or transformed by the text backend.
        return value.source

    if isinstance(value, Reference):
        # Expressions are already authored in HCL syntax and must not
        # be quoted or transformed by the text backend.
        return value.source

    if value is None:
        return "null"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, str):
        return quote_string(value)

    if isinstance(value, list):
        if not value:
            return "[]"
        rendered = ", ".join(render_value(item, level) for item in value)
        return f"[{rendered}]"

    if isinstance(value, dict):
        if not value:
            return "{}"

        lines = ["{"]
        for key, item in value.items():
            lines.append(
                f"{indent * (level + 1)}{key} = {render_value(item, level + 1, indent=indent)}"
            )
        lines.append(f"{indent * level}" + "}")
        return "\n".join(lines)

    raise TypeError(f"Unsupported HCL value: {type(value)!r}")


def render_block(block: Block, *, kind=None, level: int = 0, indent: str = "  ") -> str:
    """
    Render a single block and its body recursively.

    `kind` is used for nested blocks, where the attribute name becomes the
    emitted block type.
    """
    block_type = kind or block._phcl_kind
    if not block_type:
        raise ValueError(f"Block type is not set for {block.__class__.__name__}")

    labels = list(getattr(block.__class__, "_phcl_label", []) or [])
    if isinstance(block, Node):
        labels = labels + [class_to_label(block.__class__.__name__)]
    header = " ".join([block_type] + [quote_string(label) for label in labels]) + " {"

    attrs, nested = walk_block(block)
    lines = [f"{indent * level}{header}"]

    for name, value in attrs:
        rendered = render_value(value, level + 1, indent=indent)
        lines.append(f"{indent * (level + 1)}{name} = {rendered}")

    # Insert a visual separator between simple attributes and nested blocks.
    if attrs and nested:
        lines.append("")

    for index, (name, child) in enumerate(nested):
        lines.append(render_block(child, kind=name, level=level + 1, indent=indent))
        if index != len(nested) - 1:
            lines.append("")

    lines.append(f"{indent * level}" + "}")
    return "\n".join(lines)


def build_hcl(registry: list[type], *, indent: str = "  ") -> str:
    """
    Render a registry of concrete top-level declarations into HCL2 text.

    The input is a list of classes rather than instances, matching the current
    PHCL registry model where top-level declarations are collected as classes.
    """
    rendered = [render_block(cls(), indent=indent) for cls in registry]
    return "\n\n".join(rendered) + ("\n" if rendered else "")
