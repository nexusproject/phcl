# Types

`phcl.types` exposes HCL type expressions as first-class PHCL values.

Use them when you want to write native HCL type syntax structurally instead of
falling back to raw `hcl("...")` strings.

Typical import:

```python
from phcl.types import ANY, BOOL, LIST, NUMBER, OBJECT, OPTIONAL, STRING, TUPLE
```

## Available Type Expressions

Primitive tokens:

- `STRING`
- `NUMBER`
- `BOOL`
- `ANY`

Constructors:

- `LIST(...)`
- `MAP(...)`
- `SET(...)`
- `OBJECT({...})`
- `TUPLE([...])`
- `OPTIONAL(...)`

These are HCL type expressions, not Python typing objects.

For example:

```python
from phcl.types import BOOL, LIST, NUMBER, OBJECT, OPTIONAL, STRING, TUPLE


name_type = STRING
ports_type = LIST(NUMBER)
settings_type = OBJECT(
    {
        "name": STRING,
        "enabled": OPTIONAL(BOOL),
    }
)
pair_type = TUPLE([STRING, NUMBER])
```

They render as native HCL type syntax:

```hcl
string
list(number)
object({name = string, enabled = optional(bool)})
tuple([string, number])
```

## Terraform Variable Types

One practical use is `Variable.type` in `phcl.terraform`:

```python
from phcl.terraform import Variable
from phcl.types import BOOL, LIST, NUMBER, OBJECT, OPTIONAL, STRING


class Region(Variable):
    type = STRING
    default = "us-east-1"


class Ports(Variable):
    type = LIST(NUMBER)
    default = [80, 443]


class Settings(Variable):
    type = OBJECT(
        {
            "name": STRING,
            "enabled": OPTIONAL(BOOL),
        }
    )
```

This renders to:

```hcl
variable "region" {
  type = string
  default = "us-east-1"
}

variable "ports" {
  type = list(number)
  default = [80, 443]
}

variable "settings" {
  type = object({name = string, enabled = optional(bool)})
}
```

## Types Alongside Other Variable Attributes

Type expressions only cover the `type` value itself.

Neighboring variable attributes such as `default`, `description`, `nullable`,
and `sensitive` still work as ordinary declaration attributes, while nested
`validation` remains a block value:

```python
from phcl.syntax import B, hcl
from phcl.terraform import Variable
from phcl.types import STRING


class Region(Variable):
    type = STRING
    description = "AWS region"
    nullable = False
    validation = B(
        condition=hcl('can(regex("^us-", var.region))'),
        error_message="Region must start with us-",
    )
```

This keeps the model consistent:

- type syntax stays structural and unquoted
- regular attributes stay regular Python values
- nested HCL blocks still use `B(...)`
- raw HCL expressions still use `hcl(...)` when needed

## When To Use `hcl(...)` Instead

Use `phcl.types` when the value is specifically an HCL type expression.

Use `hcl(...)` when you need arbitrary native HCL expression syntax that does
not fit one of the provided structural constructors.
