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
    generate,
    heredoc,
    json_block,
    path_module,
    path_target,
    render_file,
    this,
    yaml_block,
    derive,
)
```

## Included Helpers

`phcl.runtime` currently exposes:

- `path_module()`
- `path_target()`
- `heredoc(...)`
- `generate(...)`
- `this`
- `derive(...)`
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

This differs from HCL/Terraform `path.module`: PHCL resolves `path_module()`
from the PHCL source module, while HCL resolves `path.module` from the generated
HCL module. Those locations can differ when generated files are written to a
separate output directory or a different layout.

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
It is not a stable PHCL project root helper.

The value depends on how generation is invoked. For example, `phcl build src`
and running `phcl build .` from inside `src` can load the same PHCL files while
producing different `path_target()` values. Use this helper only for rare cases
that specifically need the current build target.

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

## `generate(...)` and `this`

`generate(...)` materializes multiple concrete declarations from one
class-first declaration template.

`generate(...)` accepts a mapping or a list. Mapping keys become generation
identity suffixes. List items use positional string keys such as `"0"` and
`"1"`. Values remain the original Python values.

Example:

```python
from phcl.runtime import generate, this
from phcl.terraform import Resource


@generate({
    "dev": {"bucket": "app-dev"},
    "prod": {"bucket": "app-prod"},
})
class Bucket(Resource["aws_s3_bucket"]):
    bucket = this.value["bucket"]
    tags = {
        "Env": this.key,
        "Index": this.index,
    }
```

This materializes declarations with labels such as `bucket_dev` and
`bucket_prod`: the normal class-derived trailing label is preserved, and the
generation key is appended with `_`.

The decorated class becomes a generation template and is not rendered directly.
Concrete declaration classes are materialized as soon as Python applies the
decorator, so the renderer still receives ordinary declaration classes.

Use `Template._["key"]` to reference a generated declaration by generation key:

```python
class BucketArn(Output):
    value = Bucket._["dev"].arn
```

This renders as a reference to the materialized declaration label, such as
`aws_s3_bucket.bucket_dev.arn`. Bare traversal from the template, such as
`Bucket._.arn`, is rejected because the template itself is not rendered.

If a generated declaration also uses Terraform `for_each`, select the generated
declaration first and then use normal HCL index traversal:

```python
Bucket._["dev"]["primary"].id
```

Inside the generated class body:

- `this.key` is the mapping key or list position as a string.
- `this.index` is the integer position in input order.
- `this.value` is the original input value.

`this` is only valid inside a class decorated with `@generate(...)`. Using it
in a normal declaration is an error because there is no current generation
item to resolve.

Apply `@generate(...)` only once per declaration class. Use `derive(...)` when
custom generation code needs to build declarations across multiple dimensions
or naming rules.

Mapping keys must be non-empty strings matching `[A-Za-z][A-Za-z0-9_]*`.
Use a mapping when declaration identity matters. Lists are positional, so
inserting or reordering items can rename materialized declarations.

Use list input carefully. The list should already have a stable, intentional
order. Avoid feeding `generate(...)` a list produced from unordered data such
as `list(set(...))`, because positional keys can shift between runs and rename
stateful declarations.

Unordered collections such as sets are not accepted.

## `derive(...)`

`derive(...)` materializes one concrete declaration class from an ancestor
class, an explicit trailing label, and ordinary HCL body attributes.

Most data-driven declaration materialization should use `generate(...)`.
Use `derive(...)` for special cases where code needs to produce a single
declaration functionally while still staying inside PHCL's class-first model.

Example:

```python
from phcl.core.decorators import abstract
from phcl.runtime import derive
from phcl.terraform import Resource


@abstract
class RegionalApi(Resource["aws_api_gateway_rest_api"]):
    endpoint_configuration = {"types": ["REGIONAL"]}


PublicApi = derive(
    RegionalApi,
    "public",
    description="Public API",
)
```

This is equivalent in shape to declaring a concrete subclass with the explicit
label `public`; keyword arguments become normal declaration attributes.

## `dict_block(...)`

`dict_block(...)` turns an existing mapping into a generated `Block` base class.

It serves as a bridge from plain Python data into PHCL's composable declaration
fragment model.

Use it when Python-side data already has the shape of a PHCL block body and
local class declarations should be able to override or extend it.

Example:

```python
from phcl.runtime import dict_block


class SubnetDefaults(dict_block({"cidr_block": "10.0.1.0/24"})):
    map_public_ip_on_launch = True
```

Local class attributes override values from the mapping through normal Python
inheritance.

Because mapping keys become HCL body attributes, each key must be a valid HCL
identifier. Unlike class-first PHCL attributes, `dict_block(...)` can carry
valid HCL names that cannot be written as normal Python class attributes, such
as names containing `-`.

Keyword conflicts are uncommon but real in provider schemas. Dashed HCL
identifiers are supported here mainly for HCL-spec compatibility and
portability across dialects/providers.

Keys such as `"AWS:SourceArn"` are valid object/map keys in some target
configurations, but they are not valid HCL identifiers for block body
attributes. A mapping containing those keys will be rejected by
`dict_block(...)`.

Examples:

```python
dict_block({"cidr_block": "10.0.1.0/24"})  # valid
dict_block({"app-name": "api"})            # valid: HCL allows "-"
dict_block({"from": "noreply@example.com"})  # valid: Python keyword, HCL identifier
dict_block({"_secret": "ok"})              # valid: HCL identifier
dict_block({"AWS:SourceArn": "x"})         # invalid: not an HCL identifier
dict_block({"_": "nope"})                  # invalid: reserved PHCL accessor
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
