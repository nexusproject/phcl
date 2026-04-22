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

At the same time, PHCL keeps declaration code highly recognizable and as close as possible to native HCL2.
Blocks, attributes, references, and nested structure still read in a familiar way.
You gain Python's expressive power without giving up the familiar shape of HCL-style authoring.

## HCL Generation

PHCL generates HCL from one source file at a time.

1. load the source file into a compilation context
2. resolve a Python module identity for the source when possible
3. collect concrete `Node` subclasses in the registry
4. render each collected node into top-level output
5. render any nested `Block(...)` values inside node bodies

In practice:

- files are generation units
- imports do not emit output by themselves
- concrete `Node` subclasses become top-level declarations
- `Block` values stay nested structural content

## Dialects

`phcl` is the core language layer.

Product-specific surfaces live in separate dialect packages built on top of it.

At the moment, PHCL includes a Terraform dialect in the
[`phcl-terraform`](https://github.com/nexusproject/phcl-terraform) repository.

Install it with:

```bash
pip install 'phcl[terraform]'
```

This installs the compatible Terraform dialect package alongside the PHCL core.

## Contents

- [Declarative](./declarative.md)
- [Block](./block.md)
- [Node](./node.md)
- [Syntax](./syntax.md)
- [Runtime](./runtime.md)
- [Expressions and References](./expressions.md)
- [Types](./types.md)
- [CLI](./cli.md)
