# Syntax

`phcl.syntax` is the everyday authoring surface for PHCL.

It collects the helpers that are usually needed while writing declarations,
without forcing you to remember whether something is technically a decorator,
an expression helper, or a structural alias.

Typical imports:

```python
from phcl.syntax import B, abstract, file, generate, hcl, jsonencode
from phcl.core import Node
```

In practice:

- use `phcl.syntax` for common authoring helpers
- use `phcl.core` for foundational types such as `Declarative`, `Block`, and `Node`

## Included Helpers

`phcl.syntax` currently exposes:

- `B` as the short alias for `Block`
- `abstract`
- `generate`
- `file(...)`
- `hcl(...)`
- `jsonencode(...)`

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
- syntax that should be evaluated by the target system, not by Python

Examples:

```python
from phcl.syntax import hcl


region = hcl("var.region")
config = hcl("jsonencode(local.config)")
name = hcl("each.value.name")
```

## `jsonencode(...)`

`jsonencode(...)` is a wrapped HCL function for fields that still want a JSON
string boundary even when the authoring side stays structural and Python-first.

Example:

```python
from phcl.syntax import hcl, jsonencode


container_definitions = jsonencode(
    [
        {
            "name": "api",
            "image": hcl("var.app_image"),
            "ports": (port for port in (8080, 8443)),
        }
    ]
)
```

This keeps the authoring side structural while still emitting a JSON-encoded
value at the HCL boundary.

## `file(...)`

`file(...)` is a wrapped HCL function for cases where the target system should
read a file at HCL evaluation time.

Example:

```python
from phcl.syntax import file


user_data = file("${path.module}/scripts/bootstrap.sh")
```

This differs from helpers in [`phcl.runtime`](./runtime.md), which read files
on the Python side during PHCL generation.

## What Belongs Here

`phcl.syntax` is for helpers that stay on the HCL side of the language.

That includes:

- structural aliases such as `B`
- declaration decorators such as `abstract` and `generate`
- native HCL expression helpers such as `hcl(...)`
- wrapped HCL functions such as `jsonencode(...)` and `file(...)`

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
