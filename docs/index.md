# PHCL Docs

## Overview

PHCL has a small core model:

```text
Declarative
└── Block
    └── Node
```

- `Declarative` provides inheritance, merge, and override behavior
- `Block` provides generic HCL block structure
- `Node` provides top-level declaration behavior and serves as the base for product-specific root nodes

## HCL Generation

PHCL generates HCL from one PHCL source file at a time.

1. execute a Python file
2. collect concrete `Node` subclasses in the registry
3. render each collected node into top-level output
4. render any nested `Block(...)` values inside node bodies

Rules:

- files are generation units
- imports do not create additional output units
- direct or indirect concrete `Node` subclasses can become generated top-level blocks
- plain `Block` subclasses are not collected by the registry on their own
- abstract declarations are skipped
- `Node` controls what enters top-level output
- `Block` controls structure inside generated bodies

PHCL can compile:

- a single file
- a directory subtree
- a repository in place
- a repository into another output directory

## Contents

- [Declarative](./declarative.md)
- [Block](./block.md)
- [Node](./node.md)
- [Expressions and References](./expressions.md)
- [CLI](./cli.md)
