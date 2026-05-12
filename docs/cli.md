# CLI

PHCL's CLI compiles Python-authored PHCL source files into native HCL output.

The main command is:

```bash
phcl build <target>
```

The same entrypoint is also available as:

```bash
python3 -m phcl build <target>
```

## Example Build

Build one source tree into a separate environment directory:

```bash
ENV=dev phcl build src --out-dir envs/dev/
```

Example output:

```text
==> build src
  write src/backend.py -> envs/dev/backend.tf
  write src/database.py -> envs/dev/database.tf
  write src/network.py -> envs/dev/network.tf
  write src/security.py -> envs/dev/security.tf

==> done in 0.06s
  13 written, 0 skipped, 0 failed
```

This is the common shape for incremental adoption: keep PHCL sources in one
tree, write generated HCL into another tree, and let the generated files live
next to existing hand-written configuration.

## Loading Model

The CLI compiles by loading Python source files as modules when possible.
When a proper module identity cannot be resolved, it falls back to direct file
loading.

For each file:

1. the file is loaded into an isolated compilation context
2. the module-level `PHCL` config is read
3. concrete `Node` subclasses are collected in the registry
4. the registry is rendered into HCL output

If a file does not expose `PHCL`, it is skipped.

If loading succeeds but the registry is empty, the file is also skipped.

Source files are compiled independently. Imported modules can provide shared
configuration, helpers, fragments, and references, but importing a module does
not emit output by itself.

## Targets

`build` accepts either:

- a single file
- a directory

Single-file compilation:

```bash
phcl build src/network.py
```

Directory compilation:

```bash
phcl build src
```

When the target is a directory, PHCL discovers all `*.py` files under it,
excluding `__pycache__`.

## Output Modes

PHCL supports three output modes.

### In-Place Output

By default, generated files are written next to the source file.

Example:

```bash
phcl build src/network.py
```

This produces:

```text
src/network.tf
```

### Alternate Output Directory

Generated files can be written into another directory:

```bash
phcl build src --out-dir envs/dev
```

This preserves relative structure under the new root.

For example:

```text
src/network.py -> envs/dev/network.tf
src/security.py -> envs/dev/security.tf
```

### Standard Output

For a single file, output can be written to standard output:

```bash
phcl build src/network.py --stdout
```

`--stdout` is only valid for a single file target.

## Build Output

Build output reports per-file actions and a final summary.

Status words:

- `write` — HCL was rendered and written to an output file.
- `skip` — the source file was recognized but did not produce output.
- `fail` — the source file failed to load, configure, render, or write.
- `warn` — PHCL captured a build-time warning with source location.
- `stdout` — a single-file build wrote rendered HCL to standard output.

Deprecation warnings are shown with file and line number:

```text
==> build src
  warn src/policy.py:18 (`jsonencode(...)` is deprecated and will be removed in a future release; use `hcl_jsonencode(...)` instead.)
  write src/policy.py -> envs/dev/policy.tf

==> done in 0.03s
  1 written, 0 skipped, 0 failed, 1 warnings
```

Use `--quiet` to hide successful `write` and `skip` lines while keeping failures
and the final summary:

```bash
phcl build src --out-dir envs/dev --quiet
```

Use `--no-color` or the standard `NO_COLOR` environment variable when plain
output is preferred:

```bash
phcl build src --no-color
```

## File Configuration

Each renderable source file must expose a module-level `PHCL` object.

Minimal example:

```python
class PHCL:
    extension = "tf"
```

Supported fields today:

- `extension` — output extension, for example `"tf"` or `".pkr.hcl"`; defaults
  to `".hcl"` when omitted
- `skip` — skip compilation for this file when true
- `indentation` — indentation string used by the HCL renderer, for example
  `" " * 4`

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

`--ext` remains available as a CLI override and takes precedence over
`PHCL.extension`:

```bash
phcl build service.py --ext .tf
```

## Version

Print the installed PHCL version:

```bash
phcl --version
```

The short form is also available:

```bash
phcl -V
```
