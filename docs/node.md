# Node

`Node` is PHCL's base layer for top-level declarations.

It extends [`Block`](./block.md) with registry participation, logical naming,
and reference-space access. Product or dialect packages usually build concrete
declaration families on top of it, such as Terraform `Resource`, `Data`,
`Variable`, `Output`, `Provider`, `Locals`, or `Module`.

Most PHCL projects use those product-specific families directly. `Node` is the
core mechanism behind them.

## What Node Adds

Compared to `Block`, `Node` adds:

- top-level declaration behavior
- automatic registry participation
- class-name based logical names
- default block kind for direct `Node` subclasses
- reference entrypoint through `._`

`Node` still uses the same declarative body model as `Block`: class attributes,
inheritance, nested blocks, and local overlays all work the same way.

## Declaration Families

Direct subclasses of `Node` are treated as declaration families, not concrete
project declarations.

```python
from phcl.core import Node


class Resource(Node):
    pass
```

`Resource` becomes a root declaration family. It is not registered for output
by itself.

Concrete declarations start one level deeper:

```python
class Web(Resource):
    image = "nginx"
```

With core defaults, this renders as:

```hcl
resource "web" {
  image = "nginx"
}
```

Product dialects usually add more semantics to their declaration families, but
the registration pattern is the same: direct `Node` children define families;
their descendants are project declarations.

## Kind and Labels

When a class directly extends `Node`, PHCL derives its default block kind from
the class name:

```python
class Resource(Node):
    pass
```

uses:

```text
resource
```

Concrete declaration labels are also derived from class names:

```python
class WebAPI(Resource):
    pass
```

uses:

```text
web_api
```

The conversion is PHCL's normal class-to-label conversion:

- `Resource` -> `resource`
- `WebAPI` -> `web_api`
- `InstanceId` -> `instance_id`

Set `_phcl_kind` when a declaration family needs a kind that does not match the
class name.

`Node` also inherits `Block[...]` label support. Product-specific declaration
families can use labels to represent target-side block labels:

```python
from phcl.core import Block, Node


class Resource(Node):
    pass


class MainService(Resource["web"]):
    config = Block(path="/srv/app")
```

renders as:

```hcl
resource "web" "main_service" {
  config {
    path = "/srv/app"
  }
}
```

Here:

- `resource` comes from the declaration family
- `"web"` comes from `Resource["web"]`
- `"main_service"` comes from the concrete class name

Declaration families that should not add the class-name label can set
`_phcl_auto_label = False`. Terraform `Provider`, `Locals`, and `Terraform`
use this shape.

## Registry

Project declaration classes are registered automatically when they are defined.

`Node` itself and direct subclasses of `Node` are not renderable declarations.
Descendants below the declaration family level are collected by the registry.

This is why a PHCL source file does not need a separate main entrypoint:

1. the source module is loaded
2. concrete `Node` descendants are collected
3. the registry is rendered into top-level HCL output

For CLI compilation behavior, see [CLI](./cli.md).

## Abstract Declarations

Reusable declaration bases that should not be rendered can be marked
`abstract`:

```python
from phcl.syntax import abstract
from phcl.terraform import Resource


@abstract
class ManagedBucket(Resource["aws_s3_bucket"]):
    force_destroy = True
```

Abstract declarations are skipped by renderable selection, while concrete
subclasses can still be emitted.

For practical reuse patterns, see
[Declarative Modeling, Composition and Reuse](./declarative-modeling-composition-and-reuse.md).

## References

`Node` provides `._` as the entrypoint from declaration-space into
reference-space.

The base reference path is defined by the concrete product or dialect layer.
For example, Terraform resources use paths such as:

```text
aws_instance.web
```

Further traversal uses normal `Reference` behavior:

```python
WebInstance._.id
WebInstance._["primary"].arn
```

Inside attribute values, PHCL may also coerce `Node` subclasses into reference
form automatically:

```python
depends_on = [HttpsListener]
depends_on = [HttpsListener._]
```

For the full expression and reference model, see
[Expressions and References](./expressions.md).
