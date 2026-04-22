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
