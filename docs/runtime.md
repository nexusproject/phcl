# Runtime

`phcl.runtime` contains Python-side helpers that execute during PHCL
generation.

Unlike [`phcl.syntax`](./syntax.md), these helpers do not stay as HCL syntax in
the generated output. They run while PHCL is building the final HCL.

Typical imports:

```python
from phcl.runtime import (
    block_dict,
    dict_block,
    heredoc,
    json_block,
    path_module,
    path_target,
    render_file,
    yaml_block,
)
```

## Included Helpers

`phcl.runtime` currently exposes:

- `path_module()`
- `path_target()`
- `heredoc(...)`
- `dict_block(...)`
- `json_block(...)`
- `yaml_block(...)`
- `block_dict(...)`
- `render_file(...)`

The older `multiline(...)` name remains available as a deprecated
compatibility alias and will be removed in a future release.
The older `render_file(..., multiline=...)` option is also deprecated; use
`render_file(..., heredoc=...)` instead.

## `path_module()`

`path_module()` returns the directory of the calling PHCL source file as a
Python `Path`.

It is analogous in spirit to Terraform's `path.module`, but it is resolved on
the Python side during PHCL generation.

Example:

```python
from phcl.runtime import path_module


MODULE_DIR = path_module()
```

## `path_target()`

`path_target()` returns the current `phcl build <target>` directory as a Python
`Path`.

Use `path_module()` for paths relative to the current source file. Use
`path_target()` only when code intentionally needs the active build target.

Example:

```python
from phcl.runtime import path_target


TARGET_DIR = path_target()
```

## `heredoc(...)`

`heredoc(...)` turns a Python string into an HCL heredoc expression.

Example:

```python
from phcl.runtime import heredoc


script = heredoc("echo hello\necho world")
```

This is useful when content already exists on the Python side but should be
emitted as an HCL heredoc instead of a quoted string.

## `dict_block(...)`

`dict_block(...)` turns an existing mapping into a generated `Block` base class.

It is a bridge from plain Python data into PHCL's composable declaration
fragment model.

Use it when Python-side data already has the shape of PHCL attributes and local
class declarations should be able to override or extend it.
Mapping keys must be valid Python identifiers and cannot start with `_`.

Example:

```python
from phcl.runtime import dict_block


class SubnetDefaults(dict_block({"cidr_block": "10.0.1.0/24"})):
    map_public_ip_on_launch = True
```

Local class attributes override values from the mapping through normal Python
inheritance.

`dict_block(...)` is for block-shaped data, not arbitrary map construction.
Its keys become PHCL/HCL block attributes, so they must be valid declaration
attribute names. If a value needs map/object keys that are not valid attributes,
keep that value as a normal Python `dict` instead.

Example:

```python
policy_condition = {
    "AWS:SourceArn": topic_arn,
}
```

## `block_dict(...)`

`block_dict(...)` converts assembled `Block` attributes back into a normal
mapping.

This is useful when a `Block` is authored as a composable declaration fragment
but the surrounding HCL attribute expects an object-like value rather than a
nested block.

Example:

```python
from phcl.core import Block
from phcl.runtime import block_dict


class Tags(Block):
    Project = "phcl"
    ManagedBy = "PHCL"


tags = block_dict(Tags(Name="api"))
```

The first version is shallow: it returns PHCL attributes as-is, preserving
embedded `Expression`, `Reference`, and nested `Block` values.

## File-Backed Block Helpers

`json_block(...)` and `yaml_block(...)` build on top of `dict_block(...)`: they
read a JSON/YAML mapping, optionally select a nested mapping with `at=...`, and
return a generated `Block` base class.

When the loaded fragment can be used as-is, assign it directly:

```python
CONFIG = path_module().parent / "config" / "envs.yaml"

Config = yaml_block(CONFIG, at=ENV)
```

For nested data, pass a tuple or list of mapping keys:

```python
PublicSubnetConfig = yaml_block(
    CONFIG,
    at=(ENV, "network", "public", "subnet"),
)
```

A string `at` value is one literal mapping key. Dotted strings are not split
into nested paths; use a tuple or list when selecting nested data.

When the loaded fragment needs local defaults or overrides, refine it through
normal declarative inheritance:

```python
class Config(yaml_block(CONFIG, at=ENV)):
    backend_ami_id = ""
    key_pair_name = ""
```

Both forms treat file-backed data as a composable declaration fragment.

## `render_file(...)`

`render_file(...)` reads a file, optionally applies `string.Template`
substitution, and returns either:

- an HCL heredoc expression by default
- or a normal Python string when `heredoc=False`

Template placeholders use Python's `string.Template` syntax: `$name` or
`${name}`.

Example:

```text
#!/usr/bin/env bash
echo "deploying ${db_name} in ${aws_region}"
```

```python
from phcl.runtime import path_module, render_file


MODULE_DIR = path_module()

commands = render_file(
    MODULE_DIR / "scripts" / "backend-deploy.sh.tmpl",
    context={
        "aws_region": "us-east-1",
        "db_name": "app",
    },
)
```

This keeps template loading and rendering on the Python side while still
allowing the result to be emitted naturally into HCL.
