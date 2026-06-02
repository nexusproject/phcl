# Examples

This directory contains small PHCL examples and their generated HCL output.

Run commands from the repository root.

## Setup

Install PHCL with the Terraform dialect:

```sh
python3 -m pip install -e '.[terraform]'
```

If PHCL is already installed, the `phcl` command can be used directly. The same
entrypoint is also available as `python3 -m phcl`.

## Compile One Example

Build a single source file:

```sh
phcl build examples/aws/aws.py
```

By default, PHCL writes the generated file next to the source file:

```text
examples/aws/aws.py -> examples/aws/aws.tf
```

To preview the generated HCL without writing a file:

```sh
phcl build examples/aws/aws.py --stdout
```

To write generated output somewhere else:

```sh
phcl build examples/aws --out-dir /tmp/phcl-examples
```

## Compile Valid Example Cases

These example directories are expected to build successfully:

```sh
phcl build examples/aws
phcl build examples/databricks
phcl build examples/derive
phcl build examples/block-data
phcl build examples/file-backed-blocks
phcl build examples/generate/valid
phcl build examples/hcl-types
phcl build examples/runtime
```

Avoid building the whole `examples/` tree for a normal compile check. Some
subdirectories intentionally contain invalid PHCL to demonstrate error output.

## Error Examples

These directories are meant to fail when built:

```sh
phcl build examples/block-validation-errors
phcl build examples/generate/errors/non_string_key.py
phcl build examples/generate/errors/tuple_input.py
phcl build examples/generate/errors/unsafe_key.py
phcl build examples/generate/errors/underscore_key.py
phcl build examples/generate/errors/stacked.py
phcl build examples/generate/errors/bare_reference.py
phcl build examples/generate/errors/subclass_template.py
```

They are useful for checking validation messages and failure behavior.
