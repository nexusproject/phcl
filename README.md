<h1>
  <img src="assets/phcl-logo-dashed.svg" width="70" align="absmiddle"
       style="margin-right: 8px;">
  PHCL
  <img src="https://codecov.io/gh/nexusproject/phcl/branch/main/graph/badge.svg"
       align="right">
</h1>

## Idea

PHCL is a Python DSL that compiles to native HCL2.

HCL is great for describing infrastructure, but not for generating it. As complexity grows, configuration turns into a combinatorial explosion and becomes hard to maintain.

It also struggles when infrastructure depends on external data — YAML, JSON, databases, APIs — where data needs to be loaded, transformed, and combined before turning into resources.

PHCL moves generation, composition, and data processing into Python while keeping the output as clean, readable HCL2.

## Architecture

This repository contains the PHCL core.

Product-specific layers are expected to live above it in separate packages.

PHCL is split into three parts:

- `core` — declarative model
- `render` — HCL2 generation
- `cli` — compiles source files and writes output

Generation cycle:

1. execute a PHCL source file
2. collect concrete `Node` subclasses in the registry
3. render them as top-level output
4. render nested `Block(...)` values as part of node bodies

- `Node` descendants are the root units of generation
- plain `Block` values are structural content, not top-level declarations
- abstract declarations are skipped

Boundaries:

- Python handles declaration, reuse, generation, and transformation
- HCL remains the output format
- HCL expressions stay native when needed
- product-specific semantics live above the core DSL

See also:

- [Docs Index](./docs/index.md)
- [Declarative](./docs/declarative.md)
- [Block](./docs/block.md)
- [Node](./docs/node.md)
- [Expressions and References](./docs/expressions.md)

## CLI

The CLI supports:

- compile a single Python file into HCL output
- walk a directory and compile each file independently
- emit generated files next to sources, into another directory, or to stdout
- infer output suffix from the source filename, or override it explicitly

This makes PHCL easy to adopt incrementally:

- generate one file beside existing HCL
- generate one subtree into a separate output directory
- generate an entire repository in place
- generate an entire repository into another target tree

See also:

- [CLI Docs](./docs/cli.md)

## Installation

The package exposes a `phcl` CLI entrypoint:

```bash
pip install .
```

or:

```bash
uv sync
```

Then:

```bash
phcl build test.py --ext .tf
```
