<h1>
  <img src="https://raw.githubusercontent.com/nexusproject/phcl/main/assets/phcl-logo-dashed.svg" width="70" align="absmiddle"
       style="margin-right: 8px;">
  PHCL
  <img src="https://codecov.io/gh/nexusproject/phcl/branch/main/graph/badge.svg"
       align="right">
</h1>
PHCL is a Python DSL that compiles to native HCL2 and enables dynamic infrastructure generation.

## Idea

In Terraform, HCL is great for describing infrastructure, but not for generating it dynamically. As complexity grows, configuration turns into a combinatorial explosion and becomes hard to maintain.

It also struggles when infrastructure depends on external data — YAML, JSON, databases, APIs — where data needs to be loaded, transformed, and combined before turning into resources.

PHCL moves generation, composition, and data processing into Python while keeping the output as clean, readable HCL2.

At the same time, PHCL keeps declaration code highly recognizable and as close as possible to native HCL2: you gain Python's expressive power without giving up the familiar shape of HCL-style authoring.

## Architecture

PHCL is built around a small declarative core that treats Python classes as reusable HCL declaration shapes.

- `Classes as declarations` — class bodies describe HCL structures directly instead of building an intermediate runtime config format.
- `Inheritance as refinement` — subclasses extend and override existing declaration shapes, making reuse and specialization native to the model.
- `Registry and rendering` — concrete top-level declarations are collected and emitted as plain HCL2.
- `Shared core, thin dialects` — Terraform-, Packer-, and other HCL2-oriented layers can stay thin on top of the same PHCL foundation.

For example, instead of writing Terraform like this:

```hcl
resource "aws_instance" "web" {
  ami           = "ami-123"
  instance_type = "t3.small"
}
```

PHCL aims to let you express the same declaration shape like this:

```python
class Web(Resource["aws_instance"]):
    ami = "ami-123"
    instance_type = "t3.small"
```

See also:

- [Docs Index](https://github.com/nexusproject/phcl/blob/main/docs/index.md)
- [Declarative](https://github.com/nexusproject/phcl/blob/main/docs/declarative.md)
- [Block](https://github.com/nexusproject/phcl/blob/main/docs/block.md)
- [Node](https://github.com/nexusproject/phcl/blob/main/docs/node.md)
- [Syntax](https://github.com/nexusproject/phcl/blob/main/docs/syntax.md)
- [Expressions and References](https://github.com/nexusproject/phcl/blob/main/docs/expressions.md)

## CLI

The CLI supports:

- compile a single Python file into HCL output
- walk a directory and compile each file independently
- emit generated files next to sources, into another directory, or to stdout
- read per-file output settings from a module-level `PHCL` config, defaulting output to `.hcl`

This makes PHCL easy to adopt incrementally:

- generate one file beside existing HCL
- generate one subtree into a separate output directory
- generate an entire repository in place
- generate an entire repository into another target tree

See also:

- [CLI Docs](https://github.com/nexusproject/phcl/blob/main/docs/cli.md)

## Installation

The package exposes a `phcl` CLI entrypoint:

```bash
pip install phcl
```

To install the Terraform dialect layer together with PHCL:

```bash
pip install 'phcl[terraform]'
```

Then:

```bash
phcl build <target>
```
