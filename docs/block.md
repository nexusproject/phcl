# Block

`Block` is PHCL's representation of an HCL block.

## Structural Context

In the HCL native syntax specification, the structural language is built from:

- body content
- attributes
- blocks

A simplified grammar excerpt looks like:

```text
Body      = (Attribute | Block | OneLineBlock)*
Attribute = Identifier "=" Expression Newline
Block     = Identifier (StringLit|Identifier)* "{" Newline Body "}" Newline
```

This is the important part for PHCL:

- a body contains attributes and blocks
- an attribute binds a name to an expression
- a block has a type, zero or more labels, and a body

PHCL's `Block` is the core structural primitive built around this shape.

## HCL Block Shape

A block has:

- block type
- zero or more labels
- body

Example block:

```hcl
service "api" "v1" {
  ...
}
```

Here:

- block type = `service`
- labels = `"api"`, `"v1"`
- body = `{ ... }`

PHCL maps this structure into Python.

More examples:

No labels:

```hcl
policy {
  ...
}
```

One label:

```hcl
service "api" {
  ...
}
```

Multiple labels:

```hcl
service "api" "v1" {
  ...
}
```

## PHCL Mapping

At the low structural level, `Block` models the HCL block pattern directly:

- block type -> block kind
- labels -> `Block[...]`
- body -> declarative attributes

Minimal structural example:

```python
from phcl import Block


class MyBlock(Block):
    attr1 = ...
    attr2 = ...
```

Here:

- `Block` provides the generic block shape
- class attributes define the block body
- labels are optional and added separately when needed

`Block` is the generic structural primitive.

In practice, it is most useful for:

- nested blocks
- repeated nested blocks
- labelled nested blocks

## Labels

`Block[...]` attaches labels to a block class.

PHCL:

```python
some = Block["network", "block"]()
```

Rendered in nested form as:

```hcl
some "network" "block" {
}
```

Here:

- block type comes from the attribute name in the surrounding body
- labels come from `Block[...]`

This corresponds to the `Identifier (StringLit|Identifier)*` part of the HCL block form: a block type followed by zero or more labels.

## Attributes

An HCL attribute has the shape:

```text
Identifier "=" Expression
```

In PHCL, plain literal attributes can be represented directly on a block instance:

```python
config = Block(port=8080, enabled=True)
```

For plain Python literals, PHCL emits the corresponding HCL literal form.

Constructor keyword arguments are not separate from the declarative model. They are instance-level attribute definitions.

That means they can also override class-defined attributes:

```python
class Config(Block):
    port = 8080
    enabled = True


config = Config(enabled=False)
```

Resulting body:

```python
{
    "port": 8080,
    "enabled": False,
}
```

So a block body can be defined in two ways:

- through class attributes
- through constructor keyword arguments

And constructor keyword arguments can extend or override the inherited declarative body.

## Nested Blocks

HCL nested block fragment:

```hcl
config {
  path = "/srv/app"
}
```

Nested HCL blocks are represented by putting `Block(...)` values inside attributes.

```python
config = Block(path="/srv/app")
```

Repeated nested blocks are represented by lists of blocks:

```hcl
ingress {
  port = 80
}

ingress {
  port = 443
}
```

```python
ingress = [
    Block(port=80),
    Block(port=443),
]
```

When attached to attributes in a surrounding body, these values render as nested blocks.

This corresponds to the `Body` production: a block body may contain both attributes and child blocks.

## Scope

`Block` is the generic structural primitive.

It is not tied to Terraform or any other HCL2-based product.

Product-specific layers can build on top of it, but the block shape itself belongs to the PHCL core.

If you want to understand top-level declarations, continue with:

- [Node](./node.md)
