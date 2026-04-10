# PHCL

## Idea

A Python DSL that compiles to native HCL2

PHCL lets you write HCL2 using Python while keeping the result close to real HCL2.
It doesn’t hide HCL2 behind abstractions — it preserves its shape, but adds Python’s power for generation, composition, and transformation.

## Why

In Terraform, HCL works well for describing infrastructure, but is not really designed for dynamic infrastructure generation.

As systems grow, configuration often becomes a mix of concerns: teams, roles, environments, regions, products. This quickly turns into a cartesian explosion, and expressing that logic directly in HCL becomes hard to maintain and awkward to write.

The same happens when infrastructure depends on external data. You may need to read YAML, JSON, databases, or APIs, transform and combine that data, and turn it into resources. HCL can describe the final result, but it is not built for this kind of logic.

PHCL solves this by moving generation, composition, and transformation into Python while still producing valid native HCL2. It keeps HCL familiar, but uses a language that is actually suited to building it.

PHCL is a Python authoring layer over HCL2. You can keep native HCL where it works, replace only the painful parts, or move everything into Python — the output stays valid HCL2 either way.

## Architecture

This repository contains the core PHCL layer. Terraform-specific primitives are implemented separately in `phcl-terraform`.

PHCL is split into three parts:

- `core` — declarative model
- `render` — HCL2 generation
- `cli` — executes files and writes output

Design boundaries:

- Python handles declaration, reuse, generation, and transformation
- HCL remains the output format
- HCL expressions stay native when needed
- Product-specific semantics live above the core DSL

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
