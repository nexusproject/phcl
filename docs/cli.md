# CLI

PHCL provides a single compilation command:

```bash
phcl build <target>
```

The same entrypoint is also available as:

```bash
python3 -m phcl build <target>
```

## Execution Model

The CLI compiles by executing Python source files.

For each file:

1. the file is executed in isolation
2. concrete `Node` subclasses are collected in the registry
3. the registry is rendered into HCL output

If execution succeeds but the registry is empty, the file is skipped.

## Targets

`build` accepts either:

- a single file
- a directory

Single-file compilation:

```bash
phcl build path/to/service.tf.py
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

## Output Extension

By default, PHCL infers the output extension from the source filename.

Examples:

```text
main.tf.py      -> main.tf
image.pkr.hcl.py -> image.pkr.hcl
```

If the source filename does not contain an output extension, pass one explicitly:

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
