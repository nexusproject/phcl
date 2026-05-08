# HCL Identifiers and Python Attribute Syntax

PHCL deliberately uses Python classes and attributes to author HCL-shaped
configuration. That gives the common case a clean, structural form:

```python
class Config(Block):
    region = "eu-central-1"
    instance_type = "t3.micro"
```

For most Terraform-style schemas this works naturally, because HCL attribute
names are usually also valid Python attribute names. The edge cases matter,
though, because PHCL aims to author native HCL configuration rather than only
the subset of HCL that happens to fit Python syntax.

This document is about that compatibility edge, not the everyday authoring
style. These cases are expected to be rare. Most PHCL users will probably never
write an attribute name that collides with Python syntax. PHCL still needs a
clear answer for them so the model remains fully compatible with HCL when a
provider, dialect, generated schema, or migrated configuration happens to use
one.

## The Two Identifier Spaces

HCL body attributes use HCL identifiers:

```hcl
cidr_block = "10.0.0.0/16"
```

Python class declarations use Python identifiers:

```python
class Vpc(Block):
    cidr_block = "10.0.0.0/16"
```

Those two spaces overlap heavily, but they are not identical.

Two differences are relevant for PHCL compatibility:

- HCL identifiers can use words that are keywords in Python.
- HCL identifiers can contain `-`, while Python identifiers cannot.

That does not make those HCL attributes invalid. It only means PHCL needs a
small compatibility path beyond ordinary Python class attributes.

## The Normal Path

The normal PHCL path remains class-first and Python-shaped:

```python
class Config(Block):
    region = "eu-central-1"
    enabled = True
```

This is the form PHCL optimizes for. It is readable, type-checkable, easy to
inherit from, and fits Python tooling.

The compatibility problem should not make the common case worse.

## Two Compatibility Cases

There are two different compatibility cases.

The first case is a Python keyword used as an HCL attribute name. This is rare,
but it can happen in real schemas. The most plausible collisions are ordinary
configuration words that Python reserves for syntax, such as `from`, `return`,
`lambda`, `global`, `in`, `is`, `not`, `or`, `and`, `as`, `with`, `class`, `for`,
or `if`.

PHCL can support this in class-first syntax with a trailing underscore alias:

```python
class Config(Block):
    from_ = "noreply@example.com"
```

This can render as:

```hcl
from = "noreply@example.com"
```

The second case is an HCL identifier containing `-`:

```hcl
app-name = "api"
```

Python reads `app-name` as an expression, not as an attribute name. This is
expected to be extremely uncommon in practice, but HCL allows it, so PHCL keeps
a compatibility path for it. Since Python cannot spell such a name as a class
attribute, use a data-backed block base:

```python
class Config(dict_block({"app-name": "api"})):
    pass
```

Access to such names follows the same split between HCL/reference traversal and
Python-side object access. See the reference section below.

This is intentionally not raw HCL text. The attribute name is supplied as data,
but the body is still a PHCL `Block` and values still flow through PHCL's normal
normalization and renderer.

That distinction matters: `dict_block({"app-name": "api"})` is structured
configuration, while `hcl('app-name = "api"')` is raw syntax. The first keeps
PHCL in control of the model. The second bypasses the model.

This is not intended to become the common style for PHCL declarations. It is a
small compatibility path for the tail of HCL identifiers that Python cannot
spell directly.

## References

The same distinction appears on the reference side.

Python-compatible HCL attributes can use dot-style traversal:

```python
Bucket._.arn
```

Attributes that are not Python-compatible need a string-key traversal form on
the HCL/reference tier:

```python
Resource._["app-name"]
```

That keeps the meaning explicit: dot access is Python syntax; item access
carries an HCL attribute or key name as data.

For Python-side object access, use Python's normal dynamic attribute access when
a name cannot be written with dot syntax:

```python
getattr(Config, "app-name")
```

## Reserved Names

PHCL needs a small internal namespace for its own machinery.

The single `_` name is used for PHCL reference accessors:

```python
Bucket._
```

Names beginning with `_phcl_` are reserved for PHCL metadata and hooks.

## Design Rule

The class-first syntax should be the best path for the common case.

The data-backed syntax should preserve full HCL compatibility for rare edge
cases.

Raw HCL should remain the last resort.

This keeps PHCL Pythonic without shrinking HCL to Python's identifier grammar.
