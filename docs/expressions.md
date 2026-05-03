# Expressions and References

PHCL separates two different concepts:

- raw HCL expressions
- structured references
- structural Python values lowered into HCL value space

`Reference` is also an expression, but a more specific one: it represents traversal syntax built structurally rather than written as raw HCL text.

## Expression

`Expression` is an opaque raw HCL fragment.

Use it when the value should be emitted exactly as HCL syntax.

```python
from phcl.syntax import hcl


value = hcl('var.enabled ? "api" : "worker"')
```

This renders as:

```hcl
value = var.enabled ? "api" : "worker"
```

not:

```hcl
value = "var.enabled ? \"api\" : \"worker\""
```

User-facing helpers such as `hcl(...)`, `hcl_call(...)`,
`hcl_jsonencode(...)`, and `hcl_file(...)` are documented in
[`phcl.syntax`](./syntax.md). This page focuses on the common expression model
underneath them.

## Structural Value Casting

PHCL can lower normal Python structures into HCL value space automatically inside attribute values.

This includes:

- `dict`
- `list`
- `tuple`
- generic `Iterable` values such as generators

Embedded `Expression` and `Reference` values are preserved during that lowering step.

Example:

```python
config = {
    "name": "api",
    "image": "registry.example.com/api:latest",
    "ports": (port for port in (8080, 8443)),
}
```

PHCL also rejects cyclic Python container structures during normalization.

## Reference

`Reference` is a structured traversal expression.

It is used for paths such as:

```text
aws_instance.web.id
module.network["public"].id
each.value.name
```

A `Reference` still renders as native HCL syntax, but it is constructed through Python traversal operations rather than raw string injection.

Example:

```python
from phcl.core import Reference


ref = Reference("aws_instance.web").id
```

Result:

```text
aws_instance.web.id
```

### Traversal

Attribute access extends the path:

```python
Reference("aws_instance.web").id
```

Index access also extends the path:

```python
Reference("module.network")["public"]
Reference("module.network")[Reference("var.key")]
```

## Relationship Between `Expression` and `Reference`

`Reference` is a specialized form of `Expression`.

Use `Expression` when you want to write native HCL syntax directly:

```python
hcl("a ? b : c")
hcl("[for item in var.items : item.name]")
```

Use `Reference` when the value is a traversal path that can be built structurally:

```python
Reference("aws_instance.web").id
Reference("module.network")["public"].id
```

`Reference` already renders as native HCL traversal syntax:

Example:

```python
Reference("aws_instance.web.id")
```

Result:

```text
aws_instance.web.id
```

## Boundary

PHCL intentionally keeps a clean boundary here.

- `Reference` covers structured traversal
- raw `Expression` covers native expression syntax

PHCL does not try to replace the full HCL expression language with a parallel Python operator DSL.

## `Node._`

`Node` provides a reference-space entrypoint through `._`.

The declaration class and a reference to that declaration are not the same thing.

Given:

```python
Instance
```

the class itself is still the declaration.

It describes an object.

Given:

```python
Instance._
```

you are no longer talking about the declaration itself.

You are talking about the HCL object represented by that declaration.

So `._` is the point where PHCL switches from declaration-space to reference-space.

```python
SomeNode._
```

The `._` mechanism belongs to the core.

What it means depends on the higher-level layer using it.

The core only defines:

- `._` enters reference-space
- the base path comes from the declaration type
- further traversal uses normal Python access

Example shape:

```python
Instance._.id
```

Practical example:

```python
class WebInstance(Node):
    pass


value = WebInstance._.id
```

This reads as:

- `WebInstance` -> declaration
- `WebInstance._` -> reference to the represented object
- `WebInstance._.id` -> traversal on that reference

This does not hardcode Terraform or any other product into the core.

A product layer decides what the base reference should be, for example:

- `aws_instance.web`
- `data.aws_ami.ubuntu`

The core itself stays product-agnostic.
- `module.network`
- or any other product-specific address form

So:

- `Instance` -> declaration
- `Instance._` -> reference to the represented object
- `Instance._.id` -> traversal on that reference

Inside block and resource attribute values, PHCL can also coerce `Node` subclasses into reference form automatically during attribute normalization.

That means both of these can be valid in attribute space:

```python
depends_on = [HttpsListener]
depends_on = [HttpsListener._]
```

The automatic form is only a convenience in attribute value space. It does not change the general meaning of `Node` as a declaration class elsewhere in PHCL.

## Rule of Thumb

Use plain Python values when you want plain HCL literals.

Use `Reference` when you want to build a path structurally.

Use `hcl(...)` when you want to inject raw HCL syntax directly.
