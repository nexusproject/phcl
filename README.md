# PHCL

## Idea

Python-powered structural DSL for authoring native HCL2.

PHCL is an attempt to replace HCL2 with Python as transparently and seamlessly as possible: keeping the code recognizable, direct, and close enough to native HCL2 that it still reads like infrastructure configuration rather than an unrelated framework, while at the same time opening access to the full expressive power of Python for composing, generating, transforming, and scaling HCL2 code. The goal is not to hide HCL behind abstractions for their own sake, but to preserve its familiar shape and extend it with everything a powerful high-level language makes possible, pushing infrastructure as code toward something more dynamic, more flexible, and genuinely code-driven.

## Why

In Terraform, HCL works well for describing infrastructure, but not for dynamically generating it.

A common example is role-based access-control or platform configuration spread across teams, roles, groups, environments, regions, and product-specific settings. As soon as the system grows, the logic often turns into a kind of cartesian product of concerns, and writing that logic directly in HCL becomes hard to maintain and sometimes almost impossible to express cleanly.

The same problem appears when infrastructure has to be derived from external sources of data. You may want to read YAML, JSON, database records, APIs, or any other source of truth, transform that data, combine it, and turn it into resources. HCL2 can describe the final result, but it is not a comfortable language for complex transformation logic.

PHCL solves this by letting you write that logic in Python while still producing valid native HCL2 output. The goal is to keep the shape of HCL familiar, but move generation, transformation, and composition into a language that is actually built for it.

At the same time, PHCL stays disciplined about its boundaries:

- Python is used for declaration, reuse, generation, and transformation.
- HCL stays the output format.
- HCL expressions stay HCL expressions when needed.
- Product-specific semantics should live above the core DSL.

You can think of PHCL as a Python-native authoring layer over HCL2: it keeps the shape of HCL familiar, but compiles it from a more expressive language. The transition is meant to be gradual. You can keep native HCL2 expressions where they still make sense, replace only the parts that become painful, or move the whole structure into Python and still end up with relevant native HCL2 output either way.

## Architecture
This repository contains the base PHCL layer. Terraform-specific primitives and semantics are intended to live in a separate `phcl-terraform` package built on top of it.

PHCL is split into three parts:

- `core` defines the declarative model
- `render` turns that model into HCL2 text
- `cli` executes files in isolation and writes generated outputs

## CLI

PHCL includes a small compiler-style CLI.

The workflow is file-oriented and intentionally simple:

- compile a single Python file into HCL output
- walk a directory and compile each file independently
- emit generated files next to sources, into another directory, or to stdout
- infer output suffix from the source filename, or override it explicitly

Each file is executed in isolation. If execution leaves materializable declarations in the registry, PHCL emits one output file for that source file. This keeps the model closer to HCL's "many independent files" workflow than to a traditional Python application with a single entrypoint.

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

## Direction

The intended long-term shape is:

- `phcl` as a general HCL-oriented structural DSL
- `phcl-terraform` as a Terraform-specific layer
- potentially other product-specific layers later

That split matters.
The core should stay small and structural.
Terraform-specific concepts like `resource`, `data`, `for_each`, `count`, addressing, and product rules belong in the layer above, not in the core itself.

## Status

PHCL is still early, but the direction is already clear:

- declarative Python classes
- native HCL2 output
- fast direct rendering
- product-specific integrations on top of a smaller core

If your problem is "I still want HCL, but I do not want to hand-author every repeated shape in HCL", then this project is aimed exactly at that tension.
