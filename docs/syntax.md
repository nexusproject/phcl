# Syntax

`phcl.syntax` is the everyday authoring surface for PHCL.

It collects the helpers that are usually needed while writing declarations,
without forcing you to remember whether something is technically a decorator,
an expression helper, or a structural alias.

Typical imports:

```python
from phcl.syntax import B, abstract, hcl, hcl_call, hcl_file, hcl_jsonencode, hcl_templatefile, hcl_yamlencode
from phcl.core import Node
```

In practice:

- use `phcl.syntax` for common authoring helpers
- use `phcl.core` for foundational types such as `Declarative`, `Block`, and `Node`

## Included Helpers

`phcl.syntax` currently exposes:

- `B` as the short alias for `Block`
- `abstract`
- `hcl(...)`
- `hcl_call(...)`
- `hcl_file(...)`
- `hcl_jsonencode(...)`
- `hcl_templatefile(...)`
- `hcl_yamlencode(...)`

The older `file(...)` and `jsonencode(...)` names remain available as
deprecated compatibility aliases and will be removed in a future release.

This keeps the common writing surface compact without turning `phcl.core` into
another convenience barrel.

## `hcl(...)`

`hcl(...)` is the escape hatch back into native HCL syntax.

Use it when the value should be emitted exactly as HCL instead of as a quoted
string or lowered structural value.

Typical cases:

- product-native functions
- runtime expressions
- HCL-native loops or conditions
- syntax that does not have a structured PHCL helper yet

Examples:

```python
from phcl.syntax import hcl


enabled_name = hcl('var.enabled ? "api" : "worker"')
matching_names = hcl('[for name in var.names : name if startswith(name, "api-")]')
```

## `hcl_call(...)`

`hcl_call(...)` builds a native HCL function call from normal PHCL/Python
arguments.

Use it when the HCL function name should be selected in code, or when PHCL does
not provide a dedicated wrapper for that function.

Example:

```python
from phcl.syntax import hcl, hcl_call
from phcl.terraform import var


tags = hcl_call("merge", {"managed_by": "phcl"}, var.extra_tags)
name = hcl_call("coalesce", var.name, "default")
```

This keeps arguments structural while still emitting a target-side HCL function
call.

## `hcl_jsonencode(...)`

`hcl_jsonencode(...)` is a wrapped HCL function for fields that still want a
JSON string boundary even when the authoring side stays structural and
Python-first.

Example:

```python
from phcl.syntax import hcl_jsonencode


container_definitions = hcl_jsonencode(
    [
        {
            "name": "api",
            "image": "registry.example.com/api:latest",
            "ports": (port for port in (8080, 8443)),
        }
    ]
)
```

This keeps the authoring side structural while still emitting a JSON-encoded
value at the HCL boundary.

## `hcl_yamlencode(...)`

`hcl_yamlencode(...)` is the YAML sibling of `hcl_jsonencode(...)`: it keeps
the authoring side structural while emitting a target-side YAML string.

Example:

```python
from phcl.syntax import hcl_yamlencode


manifest = hcl_yamlencode(
    {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": "app-config"},
    }
)
```

## `hcl_file(...)`

`hcl_file(...)` is a wrapped HCL function for cases where the target system
should read a file at HCL evaluation time.

Example:

```python
from phcl.syntax import hcl_file


user_data = hcl_file("${path.module}/scripts/bootstrap.sh")
```

This differs from helpers in [`phcl.runtime`](./runtime.md), which read files
on the Python side during PHCL generation.

## `hcl_format(...)`

`hcl_format(...)` is a wrapped HCL `format(...)` call for building target-side
strings from structural PHCL/Python arguments.

Example:

```python
from phcl.syntax import hcl, hcl_format


resource_arn = hcl_format("%s/*", hcl("aws_s3_bucket.frontend.arn"))
```

## `hcl_templatefile(...)`

`hcl_templatefile(...)` is a wrapped HCL function for target-side template
rendering with structural PHCL/Python variables.

Example:

```python
from phcl.syntax import hcl_templatefile
from phcl.terraform import var


user_data = hcl_templatefile(
    "${path.module}/templates/user_data.sh.tftpl",
    {
        "app_name": var.app_name,
        "port": 8080,
        "enable_metrics": True,
    },
)
```

This differs from [`phcl.runtime.render_file(...)`](./runtime.md), which reads
and optionally templates files on the Python side during PHCL generation.

## What Belongs Here

`phcl.syntax` is for helpers that stay on the HCL side of the language.

That includes:

- structural aliases such as `B`
- declaration decorators such as `abstract` and `generate`
- native HCL expression helpers such as `hcl(...)`
- generic HCL function calls through `hcl_call(...)`
- wrapped HCL functions such as `hcl_jsonencode(...)`, `hcl_yamlencode(...)`, `hcl_file(...)`, and `hcl_templatefile(...)`

If a helper executes in Python during PHCL generation instead of becoming HCL
syntax in the output, it belongs in [`phcl.runtime`](./runtime.md) instead.

## Local Module Imports

In multi-file PHCL projects, prefer relative imports for local modules:

```python
from .config import BASE_TAGS
from .network import Vpc
```

instead of:

```python
from config import BASE_TAGS
from network import Vpc
```

This makes it explicit that the imported modules belong to the same local PHCL
project tree, rather than relying on top-level Python import resolution.
