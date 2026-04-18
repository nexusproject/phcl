# Syntax

`phcl.syntax` is the everyday authoring surface for PHCL.

It collects the helpers that are usually needed while writing declarations,
without forcing you to remember whether something is technically a decorator,
an expression helper, or a structural alias.

Typical imports:

```python
from phcl.syntax import B, abstract, generate, hcl, jsonencode
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
- `hcl(...)`
- `jsonencode(...)`

This keeps the common writing surface compact without turning `phcl.core` into
another convenience barrel.

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
