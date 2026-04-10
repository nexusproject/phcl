from phcl.core.expression import Expression
from phcl.core.nodes import Block


INDENT = "  "


def walk_block(block: Block):
    attrs = []
    nested = []

    for name, value in block._phcl_attributes.items():
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
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_value(value, level: int = 0) -> str:
    if isinstance(value, Expression):
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
                f"{INDENT * (level + 1)}{key} = {render_value(item, level + 1)}"
            )
        lines.append(f"{INDENT * level}" + "}")
        return "\n".join(lines)

    raise TypeError(f"Unsupported HCL value: {type(value)!r}")


def render_block(block: Block, *, kind=None, level: int = 0) -> str:
    block_type = kind or block._phcl_kind
    if not block_type:
        raise ValueError(f"Block type is not set for {block.__class__.__name__}")

    labels = list(getattr(block.__class__, "_phcl_label", []) or [])
    header = " ".join([block_type] + [quote_string(label) for label in labels]) + " {"

    attrs, nested = walk_block(block)
    lines = [f"{INDENT * level}{header}"]

    for name, value in attrs:
        rendered = render_value(value, level + 1)
        if "\n" in rendered:
            lines.append(f"{INDENT * (level + 1)}{name} = {rendered}")
        else:
            lines.append(f"{INDENT * (level + 1)}{name} = {rendered}")

    if attrs and nested:
        lines.append("")

    for index, (name, child) in enumerate(nested):
        lines.append(render_block(child, kind=name, level=level + 1))
        if index != len(nested) - 1:
            lines.append("")

    lines.append(f"{INDENT * level}" + "}")
    return "\n".join(lines)


def build_hcl(registry: list[type]) -> str:
    rendered = [render_block(cls()) for cls in registry]
    return "\n\n".join(rendered) + ("\n" if rendered else "")
