# Expressions and References

PHCL is a structural DSL for authoring HCL bodies and declarations. It does not
try to reimplement the full HCL expression language as Python operators.

Instead, PHCL keeps a clear boundary:

- Python literals and containers are lowered into HCL value syntax.
- `hcl(...)` keeps native HCL expressions as native HCL.
- `Reference` builds HCL traversal paths structurally.
- `hcl_call(...)` and wrapped `hcl_*` helpers build native HCL function calls
  from PHCL/Python values.

This keeps declarations close to the shape of HCL while still allowing Python
to assemble structure around them.

## Structural Values

Normal Python values can be used directly in PHCL attributes.

This includes:

- `None`, `bool`, `int`, `float`, and `str`
- `dict`
- `list` and `tuple`
- generic iterable values such as generators

Example:

```python
tags = {
    "Name": "api",
    "ManagedBy": "PHCL",
}

ports = (port for port in (8080, 8443))
```

Embedded `Expression` and `Reference` values are preserved while surrounding
Python containers are lowered into HCL value syntax.

PHCL rejects cyclic Python container structures during normalization.

## Raw HCL Expressions

Use `hcl(...)` when a value should be emitted as native HCL syntax instead of a
quoted string or lowered Python value.

```python
from phcl.syntax import hcl


name = hcl('var.enabled ? "api" : "worker"')
matching_names = hcl('[for name in var.names : name if startswith(name, "api-")]')
```

The first value renders as:

```hcl
name = var.enabled ? "api" : "worker"
```

not:

```hcl
name = "var.enabled ? \"api\" : \"worker\""
```

Use `hcl(...)` for HCL syntax that should remain fully target-side: conditionals,
`for` expressions, provider-specific expressions, or constructs PHCL does not
model structurally.

## HCL Function Calls

For common HCL functions, prefer wrapped helpers from `phcl.syntax` when one is
available:

```python
from phcl.syntax import hcl_format, hcl_jsonencode, hcl_templatefile
from phcl.terraform import var


container_definitions = hcl_jsonencode(
    [
        {
            "name": "api",
            "image": var.app_image,
            "portMappings": [{"containerPort": 8080}],
        }
    ]
)

asset_path = hcl_format("%s/*", var.asset_prefix)

user_data = hcl_templatefile(
    "${path.module}/templates/user_data.sh.tftpl",
    {
        "app_name": var.app_name,
        "port": 8080,
    },
)
```

These helpers keep arguments structural and still emit native HCL function
calls in the generated output.

Use `hcl_call(...)` when the HCL function name is selected in Python code, or
when PHCL does not provide a dedicated wrapper yet.

```python
from phcl.syntax import hcl_call
from phcl.terraform import var


tags = hcl_call("merge", {"ManagedBy": "PHCL"}, var.extra_tags)
name = hcl_call("coalesce", var.name, "default")
```

`hcl_call(...)` renders arguments as HCL expression values. Python containers,
plain literals, `Expression`, and `Reference` values can be mixed in the same
call.

## References

`Reference` is a structured traversal expression.

It is used for paths such as:

```text
aws_instance.web.id
module.network["public"].id
each.value.name
```

A `Reference` renders as native HCL traversal syntax, but it is constructed
through Python traversal operations rather than raw string injection.

```python
from phcl.core import Reference


ref = Reference("aws_instance.web").id
```

Result:

```text
aws_instance.web.id
```

Attribute access extends the path:

```python
Reference("aws_instance.web").id
```

Index access also extends the path:

```python
Reference("module.network")["public"]
Reference("module.network")[Reference("var.key")]
```

The first form renders a literal string key:

```text
module.network["public"]
```

The second form renders an expression key:

```text
module.network[var.key]
```

`Reference` is a specialized form of `Expression`, so it can be embedded inside
normal PHCL values wherever an expression is expected.

In everyday code, dialect packages usually provide prepared references for
common target-side namespaces. The Terraform dialect exposes references such as
`var`, `local`, `module`, and `each`:

```python
from phcl.syntax import hcl_call
from phcl.terraform import each, local, module, var


image = var.app_image
tags = hcl_call("merge", local.base_tags, var.extra_tags)
subnet_id = module.network["public"].subnet_id
instance_name = each.value.name
```

These are ordinary `Reference` values with convenient starting points.

## Declaration References

`Node` provides `._` as the entrypoint from declaration-space into
reference-space.

The declaration class and a reference to that declaration are different things:

```python
Instance
```

refers to the PHCL declaration class.

```python
Instance._
```

refers to the HCL object represented by that declaration.

Further traversal uses normal reference operations:

```python
Instance._.id
Instance._["primary"].id
```

The base path depends on the product or dialect layer. For example, a Terraform
resource declaration can produce a base path such as:

```text
aws_instance.web
```

Inside attribute values, PHCL can also coerce `Node` subclasses into reference
form automatically as a convenience:

```python
depends_on = [HttpsListener]
depends_on = [HttpsListener._]
```

Both forms are valid in attribute value space. The explicit `._` form remains
the clearest way to show that code has moved into reference-space.
