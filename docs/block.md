# Block

`Block` is PHCL's main composition unit.

It can be inherited, nested, repeated, converted, loaded from data, and used as
a declaration body fragment.

`Block` is also PHCL's structural model for an HCL block body.

In the HCL native syntax specification, the structural language is built from
body content, attributes, and blocks. A simplified grammar excerpt looks like:

```text
Body      = (Attribute | Block | OneLineBlock)*
Attribute = Identifier "=" Expression Newline
Block     = Identifier (StringLit|Identifier)* "{" Newline Body "}" Newline
```

This is the part `Block` models: a block has a type, zero or more labels, and a
body containing attributes and nested blocks.

It builds on [`Declarative`](./declarative.md): class attributes, inherited
attributes, properties, and instance overlays form the block body. `Block` adds
the HCL block shape around that body: kind, labels, attributes, and nested
blocks.

For practical composition patterns, see
[Declarative Modeling, Composition and Reuse](./declarative-modeling-composition-and-reuse.md).

## Shape

An HCL block has:

- a block type
- zero or more labels
- a body

Example:

```hcl
service "api" "v1" {
  enabled = true
}
```

At the `Block` level:

- block type comes from the surrounding position or higher-level declaration
  type
- labels come from `Block[...]`
- body comes from declarative attributes

Minimal PHCL shape:

```python
from phcl.core import Block


class Service(Block):
    enabled = True
```

`Block` itself is product-agnostic. Terraform, Packer, Nomad, and other HCL
layers can build product-specific declaration families on top of the same block
shape.

## Labels

`Block[...]` creates a labelled block class.

```python
Block["api"]
Block["api", "v1"]
```

The returned value is a new parameterized class, not an instance. This lets
labels become part of the declaration shape.

When used as a nested block value:

```python
service = Block["api"](enabled=True)
```

it renders in the shape:

```hcl
service "api" {
  enabled = true
}
```

## Attributes and Local Overlays

Block bodies can be defined through class attributes:

```python
from phcl.core import Block


class Config(Block):
    port = 8080
    enabled = True
```

Constructor keyword arguments provide a local overlay:

```python
config = Config(enabled=False, name="api")
```

The resulting body is:

```python
{
    "port": 8080,
    "enabled": False,
    "name": "api",
}
```

The overlay behavior comes from `Declarative`.

HCL body attribute names are not exactly the same as Python attribute names.
For edge cases such as Python keywords or HCL identifiers containing `-`, see
[HCL Identifiers and Python Attribute Syntax](./hcl-python-identifiers.md).

## Nested Blocks

Inline nested blocks can be created with `Block(...)` or the short authoring
alias `B(...)` from [`phcl.syntax`](./syntax.md):

```python
from phcl.syntax import B


validation = B(
    condition=...,
    error_message="value is invalid",
)
```

Reusable block fragments can be defined as `Block` subclasses and used directly
in nested block position:

```python
from phcl.core import Block


class HttpIngress(Block):
    from_port = 80
    to_port = 80


ingress = HttpIngress
```

Repeated nested blocks are represented by lists:

```python
class HttpsIngress(HttpIngress):
    from_port = 443
    to_port = 443


ingress = [
    HttpIngress,
    HttpsIngress,
]
```

PHCL materializes `Block` subclasses in attribute space, so a class value such
as `HttpIngress` becomes `HttpIngress()`.

## Value Normalization

Inside block and declaration attributes, PHCL lowers ordinary Python values into
HCL value space:

- mappings become object-like values
- lists and tuples become lists
- generic iterables are materialized as lists
- `Block` instances become nested blocks
- `Block` classes are materialized into block instances
- `Node` classes can be coerced into references in attribute space

That makes both of these forms valid:

```python
depends_on = [HttpsListener]
depends_on = [HttpsListener._]
```

The first form is a convenience. The explicit `._` form makes reference-space
visible in the source. See [Expressions and References](./expressions.md) for
the full reference model.

## From Block to Node

`Block` describes nested structural content. Top-level renderable declarations
are built with [`Node`](./node.md) and product-specific declaration families
that inherit from it.
