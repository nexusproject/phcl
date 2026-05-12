# Declarative

`Declarative` is PHCL's abstract body collection layer.

It is not an authoring primitive for normal HCL configuration and does not
represent an HCL block by itself. In everyday PHCL code, these rules are used
through higher-level types such as [`Block`](./block.md), [`Node`](./node.md),
and product-specific declaration families such as Terraform `Resource`,
`Variable`, or `Output`.

## What It Provides

`Declarative` gives PHCL a stable rule for treating Python class bodies as
configuration bodies:

- class attributes become declarative body attributes
- subclasses inherit and override body attributes
- instance attributes act as a local overlay
- properties are evaluated against the current instance
- methods and PHCL metadata are ignored

This is the mechanism that lets a `Block` or `Node` behave like a reusable
declaration body instead of an ordinary stateful Python object.

For practical inheritance and reuse patterns built on this behavior, see
[Declarative Modeling, Composition and Reuse](./declarative-modeling-composition-and-reuse.md).

## Attribute Precedence

The resulting body is assembled in layers:

1. inherited class attributes
2. subclass attributes
3. instance attributes

Later layers override earlier layers by name. With multiple inheritance,
attribute precedence follows normal Python class lookup: the leftmost base wins
over bases to the right, and the final class wins over inherited values.

PHCL does not perform implicit deep merges. If a mapping or list should be
extended, merge it explicitly in the declaration.

See [Declarative Modeling, Composition and Reuse](./declarative-modeling-composition-and-reuse.md)
for examples of explicit extension and reusable declaration fragments.

## Included and Ignored Members

Included:

- plain class attributes
- properties
- nested classes
- instance attributes

Ignored:

- the single `_` name used by PHCL reference accessors
- PHCL metadata names beginning with `_phcl_`
- Python dunder names such as `__module__`
- methods

Other underscore-prefixed names are preserved.

For HCL attribute names that do not fit Python attribute syntax, see
[HCL Identifiers and Python Attribute Syntax](./hcl-python-identifiers.md).
