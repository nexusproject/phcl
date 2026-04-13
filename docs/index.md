# PHCL Docs

## Overview

PHCL is a small declarative core for building native HCL2 with Python.

Its model is intentionally compact:

```text
Declarative
└── Block
    └── Node
```

- `Declarative` provides inheritance, merge, and override behavior
- `Block` provides generic HCL block structure
- `Node` provides top-level declaration behavior and serves as the base for product-specific root nodes

## Python as Declaration Syntax

PHCL treats Python classes not as runtime types, but as declaration forms.

A class body defines an HCL structure.  
Inheritance refines it.  
Instances represent variations of that structure.

PHCL does not change Python semantics.  
It repurposes them for building declarations.

This allows PHCL to keep HCL-like structure while using Python for:

- inheritance and reuse
- abstraction and composition
- dynamic declaration generation
- integration with arbitrary code and external data

The result is not an object wrapper around HCL.  
It is Python used as a language for building declarations.

## HCL Generation

PHCL generates HCL from one source file at a time.

1. execute a Python file
2. collect concrete `Node` subclasses in the registry
3. render each collected node into top-level output
4. render any nested `Block(...)` values inside node bodies

In practice:

- files are generation units
- imports do not emit output by themselves
- concrete `Node` subclasses become top-level declarations
- `Block` values stay nested structural content

## Contents

- [Declarative](./declarative.md)
- [Block](./block.md)
- [Node](./node.md)
- [Python as Declaration Syntax](../PYTHON-TURNED-DECLARATIVE.md)
- [Expressions and References](./expressions.md)
- [CLI](./cli.md)
