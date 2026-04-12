# Expressions and References

PHCL separates two different concepts:

- raw HCL expressions
- structured references

They are related, but they are not the same thing.

## Expression

`Expression` is an opaque raw HCL fragment.

Use it when the value should be emitted exactly as HCL syntax.

```python
from phcl import hcl


value = hcl("var.region")
```

This renders as:

```hcl
value = var.region
```

not:

```hcl
value = "var.region"
```

### When to Use `hcl(...)`

Use `hcl(...)` when you want to keep native HCL syntax as-is.

Typical cases:

- product-native functions
- runtime expressions
- HCL-native loops or conditions
- syntax that should be evaluated by the target system, not by Python

Examples:

```python
hcl("var.region")
hcl("jsonencode(local.config)")
hcl("each.value.name")
```

## Reference

`Reference` is a structured traversal builder.

It is used for paths such as:

```text
aws_instance.web.id
module.network["public"].id
each.value.name
```

A `Reference` is still rendered as HCL syntax, but it is constructed through Python traversal operations rather than raw string injection.

Example:

```python
from phcl.core.expression import Reference


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
Reference("module.network")[hcl("var.key")]
```

## Relationship Between `Expression` and `Reference`

`Reference` can be converted into `Expression`:

```python
ref = Reference("aws_instance.web.id")
value = ref.hcl()
```

This is useful when a path must be treated as a raw expression value.

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

This does not hardcode Terraform or any other product into the core.

A product layer decides what the base reference should be:

- `aws_instance.web`
- `data.aws_ami.ubuntu`
- `module.network`
- or any other product-specific address form

So:

- `Instance` -> declaration
- `Instance._` -> reference to the represented object
- `Instance._.id` -> traversal on that reference

## Rule of Thumb

Use plain Python values when you want plain HCL literals.

Use `Reference` when you want to build a path structurally.

Use `hcl(...)` when you want to inject raw HCL syntax directly.
