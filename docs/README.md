# PHCL Documentation

PHCL is a Python-based Infrastructure as Code (IaC) tool for dynamic
infrastructure workflows.

It provides an authoring and generation layer for HCL-based tools such as
Terraform, OpenTofu, and Packer. Declarations are written as Python classes:
the source stays close to the shape of HCL while adding composition, dynamic
generation, and integration with Python data and logic.

PHCL is useful when HCL is derived from project data rather than written
directly: RBAC rules, users, roles, regions, environments, inventories, service
definitions, or other source-of-truth records. It also fits incremental
adoption in existing HCL projects because the output remains plain HCL.

## Contents

Core model:

- [Overview](./index.md)
- [Declarative](./declarative.md)
- [Block](./block.md)
- [Node](./node.md)

Authoring surface:

- [Expressions and References](./expressions.md)
- [Syntax](./syntax.md)
- [Runtime](./runtime.md)
- [Types](./types.md)
- [HCL Identifiers and Python Attribute Syntax](./hcl-python-identifiers.md)

Practical guides:

- [Declarative Modeling, Composition and Reuse](./declarative-modeling-composition-and-reuse.md)
- [Dynamic Generation Tips](./dynamic-generation-tips.md)

Project builds:

- [CLI](./cli.md)
