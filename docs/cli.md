# CLI

PHCL provides a single compilation command:

```bash
phcl build <target>
```

The same entrypoint is also available as:

```bash
python3 -m phcl build <target>
```

## Loading Model

The CLI compiles by loading Python source files as modules when possible.
When a proper module identity cannot be resolved, it falls back to direct file loading.

For each file:

1. the file is loaded into an isolated compilation context
2. the module-level `PHCL` config is read
3. concrete `Node` subclasses are collected in the registry
4. the registry is rendered into HCL output

If a file does not expose `PHCL`, it is skipped.

If loading succeeds but the registry is empty, the file is also skipped.

## Targets

`build` accepts either:

- a single file
- a directory

Single-file compilation:

```bash
phcl build path/to/service.py
```

Directory compilation:

```bash
phcl build path/to/repo
```

When the target is a directory, PHCL discovers all `*.py` files under it, excluding `__pycache__`.

## Output Modes

PHCL supports three output modes.

### In-Place Output

By default, generated files are written next to the source file.

Example:

```bash
phcl build examples/aws.tf.py
```

This produces:

```text
examples/aws.tf
```

### Alternate Output Directory

Generated files can be written into another directory:

```bash
phcl build examples --out-dir outdir
```

This preserves relative structure under the new root.

### Standard Output

For a single file, output can be written to standard output:

```bash
phcl build examples/aws.tf.py --stdout
```

`--stdout` is only valid for a single file target.

## File Configuration

Each renderable source file must expose a module-level `PHCL` object.

Minimal example:

```python
class PHCL:
    extension = "tf"
```

Supported fields today:

- `extension` — output extension, for example `"tf"` or `".pkr.hcl"`; defaults to `".hcl"` when omitted
- `skip` — skip compilation for this file when true
- `indentation` — indentation string used by the HCL renderer, for example `" " * 4`

Shared configuration can be imported and aliased:

```python
from .config import GlobalSettings as PHCL
```

And locally refined through normal Python inheritance:

```python
from .config import GlobalSettings


class PHCL(GlobalSettings):
    indentation = " " * 4
```

`--ext` remains available as a CLI override and takes precedence over `PHCL.extension`:

```bash
phcl build service.py --ext .tf
```

## Integration Depth

PHCL can be introduced at different levels of a repository.

Common patterns:

- compile a single file beside existing HCL
- compile one subtree into a generated output directory
- compile a whole repository in place
- compile a whole repository into a separate target tree

This allows gradual adoption. PHCL does not require the entire repository to move at once.
