# Declarative

`Declarative` is the base composition model in PHCL.

It gives the DSL one important property:

- class attributes participate in a declarative body
- subclasses extend that body
- subclasses can override inherited values
- instance attributes can be merged on top as a local overlay

This lets Python classes behave like reusable configuration declarations rather than ordinary stateful objects.

Python classes are used intentionally in PHCL.

The DSL needs:

- inheritance
- overriding
- reusable structure
- stable composition rules

Classes provide exactly that in a natural way, which makes them a good fit for declarative authoring.

## Inheritance and Override

`Declarative` has two override layers:

- subclass over base class
- instance over class as a local variation

### Subclass Override

Given:

```python
from phcl.core import Declarative


class Base(Declarative):
    region = "us-east-1"
    enabled = True


class Child(Base):
    size = "small"
    enabled = False
```

The resulting declarative body is:

```python
{
    "region": "us-east-1",
    "enabled": False,
    "size": "small",
}
```

Rules:

- a child declaration starts with the parent attributes
- inherited attributes can be overridden locally in the child
- subclasses extend an existing declaration instead of replacing it

Changing the child does not mutate the parent declaration.

That is what makes this style useful for reusable authoring:

- define a stable base declaration once
- derive specialized declarations from it
- override only the parts that need to change

This is the basis for abstract reusable building blocks in PHCL.

### Instance Override

Instance attributes are merged on top of class attributes as a local overlay.

```python
from phcl.core import Declarative


class Config(Declarative):
    region = "us-east-1"
    enabled = True


default_cfg = Config()

api_cfg = Config()
api_cfg.enabled = False
api_cfg.name = "api"
```

Here the class still defines the shared declaration shape:

```python
{
    "region": "us-east-1",
    "enabled": True,
}
```

And the instance adds a local variation on top:

```python
{
    "region": "us-east-1",
    "enabled": False,
    "name": "api",
}
```

This follows the same rule:

- the class declaration stays unchanged
- the instance provides a local variation of the resulting body

## Included and Ignored Members

`Declarative` includes:

- plain attributes
- properties
- nested classes

Properties are evaluated against the current declaration instance.

That means a property can compute derived declarative values from the local declaration context, including any instance-level overlay.

`Declarative` ignores:

- the single `_` name used by PHCL reference accessors
- PHCL metadata names starting with `_phcl_`
- Python dunder names such as `__module__`
- methods

## Why It Exists

Without `Declarative`, PHCL would only be a renderer.

`Declarative` is what makes reuse possible through normal Python mechanisms:

- inheritance
- composition through classes
- reusable templates
- specialization through subclasses

Everything above `Declarative` in PHCL depends on this behavior.
