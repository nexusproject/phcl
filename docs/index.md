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
- `Node` provides top-level declaration behavior

## Generation Cycle

PHCL compiles by executing Python source and collecting declarations.

The cycle is:

1. execute a Python file
2. collect concrete `Node` subclasses in the registry
3. render each collected node as top-level output
4. render any nested `Block(...)` values inside node bodies

This makes `Node` descendants the root units of generation.

That also means:

- direct or indirect concrete `Node` subclasses can become generated top-level blocks
- plain `Block` subclasses are not collected by the registry on their own
- abstract declarations are skipped

At the same time, `Node` still inherits from `Block`, so its body can contain nested blocks, repeated nested blocks, and plain attributes.

So:

- `Node` controls what enters the top-level output
- `Block` controls structure inside generated bodies

## Root and Nested Structure

In practical terms:

- use `Node` for declarations that should be emitted as root blocks
- use `Block` for structural content inside those declarations

Example:

```python
from phcl import Block, Node


class Service(Node):
    config = Block(path="/srv/app")
```

This produces a top-level node:

```hcl
service "service" {
  config {
    path = "/srv/app"
  }
}
```

Here:

- `Service` is collected because it is a concrete `Node`
- `config` is rendered because it is part of the node body
- `config` is not independently registered as a root declaration

## Adoption Depth

PHCL does not require an all-or-nothing workflow.

You can:

- generate a single file
- generate a subtree
- generate a whole repository in place
- generate into another output directory

That makes it possible to adopt PHCL at whatever depth is useful:

- as a small local authoring layer
- as a partial replacement in an existing HCL repository
- or as the main source format for a project

## Contents

- [Declarative](./declarative.md)
- [Block](./block.md)
- [Node](./node.md)
- [Expressions and References](./expressions.md)
- [CLI](./cli.md)
