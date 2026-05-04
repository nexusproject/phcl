# Runtime

`phcl.runtime` contains Python-side helpers that execute during PHCL
generation.

Unlike [`phcl.syntax`](./syntax.md), these helpers do not stay as HCL syntax in
the generated output. They run while PHCL is building the final HCL.

Typical imports:

```python
from phcl.runtime import heredoc, path_module, render_file
```

## Included Helpers

`phcl.runtime` currently exposes:

- `path_module()`
- `heredoc(...)`
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

## `heredoc(...)`

`heredoc(...)` turns a Python string into an HCL heredoc expression.

Example:

```python
from phcl.runtime import heredoc


script = heredoc("echo hello\necho world")
```

This is useful when content already exists on the Python side but should be
emitted as an HCL heredoc instead of a quoted string.

## `render_file(...)`

`render_file(...)` reads a file, optionally applies `string.Template`
substitution, and returns either:

- an HCL heredoc expression by default
- or a normal Python string when `heredoc=False`

Example:

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
