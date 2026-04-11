# Declarative

`Declarative` is the base composition model in PHCL.

It gives the DSL one important property:

- class attributes participate in a declarative body
- subclasses extend that body
- subclasses can override inherited values
- instance attributes are merged on top

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
- instance over class

### Subclass Override

Given:

```python
from phcl.core.declarative import Declarative


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

- parent attributes are inherited
- child attributes override parent attributes
- subclasses extend an existing declaration instead of replacing it

Changing the child does not mutate the parent declaration.

That is what makes this style useful for reusable authoring:

- define a stable base declaration once
- derive specialized declarations from it
- override only the parts that need to change

This is the basis for abstract reusable building blocks in PHCL.

### Instance Override

Instance attributes are merged on top of class attributes.

```python
from phcl.core.declarative import Declarative


class Config(Declarative):
    region = "us-east-1"
    enabled = True


cfg = Config()
cfg.enabled = False
cfg.name = "api"
```

Result:

```python
{
    "region": "us-east-1",
    "enabled": False,
    "name": "api",
}
```

This follows the same rule:

- the class declaration stays unchanged
- the instance can extend or override its resulting body

## Included and Ignored Members

`Declarative` includes:

- plain attributes
- properties
- nested classes

`Declarative` ignores:

- private names
- methods

## Why It Exists

Without `Declarative`, PHCL would only be a renderer.

`Declarative` is what makes reuse possible through normal Python mechanisms:

- inheritance
- composition through classes
- reusable templates
- specialization through subclasses

Everything above `Declarative` in PHCL depends on this behavior.
