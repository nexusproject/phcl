# Node

`Node` is PHCL's top-level declaration type.

`Block` models generic HCL structure. `Node` adds PHCL-specific top-level behavior.

In core PHCL, `Node` is primarily a declaration base.

It is usually not the final user-facing abstraction in a product layer.

Product-specific packages typically build more concrete root node types on top of it, such as resource-like, provider-like, or output-like declarations.

So the main role of `Node` is:

- provide top-level generation behavior in the core
- act as the base class from which product-specific root nodes are built

## What `Node` Adds

Compared to `Block`, `Node` adds:

- top-level declaration semantics
- registry participation
- logical naming
- automatic default kind for direct subclasses
- reference entrypoint through `._`

## Top-Level Declaration

`Node` is the core top-level declaration primitive.

At this level, the important part is not a particular product-specific block type, but the top-level generation behavior that higher-level declaration types inherit.

Typical usage is to define a product-specific root node type on top of `Node`:

```python
from phcl import Node


class Resource(Node):
    pass


class MainResource(Resource):
    image = "nginx"
```

Here:

- `Node` provides the core top-level declaration behavior
- `Resource` becomes a product-specific root node base
- `MainResource` is a concrete declaration built on top of that base

`abstract` is not required in this specific pattern because `Node` itself and its direct subclasses are not registered as renderable project declarations.
Concrete project declarations begin one level deeper.

With the core defaults shown above, this renders as:

```hcl
resource "main_resource" {
  image = "nginx"
}
```

In real product layers, classes such as `Resource` usually define more semantics than this, but the inheritance pattern is the important part.

Rules:

- direct subclasses of `Node` derive their block kind from the class name by default
- the final top-level label is also derived from the class name

This uses PHCL's normal class-to-label conversion.

Example:

- `Resource` -> `resource`
- `MainResource` -> `main_resource`
- `WebAPI` -> `web_api`
- `InstanceId` -> `instance_id`

So:

- the block kind for a direct `Node` subclass defaults from the class name
- concrete subclasses inherit that kind unless a higher-level layer changes it
- the generated top-level logical label defaults from the concrete class name
- `_phcl_kind` can still be set explicitly when a root declaration type needs to force a different kind

For product or dialect root classes, this means:

- if the desired block kind already matches the canonical class name, it is fine to rely on the default
- explicit `_phcl_kind` is only needed when the desired kind differs from that default

Example:

- `class Resource(Node)` can rely on the default kind `resource`
- `class Data(Node)` can rely on the default kind `data`
- `class Provider(Node)` can rely on the default kind `provider`

## Relationship to `Block`

`Node` still uses the same body model as `Block`.

That means a node can contain:

- plain attributes
- nested `Block(...)` values
- repeated nested blocks

It also inherits label support from `Block`, so product-specific root node types can use `[...]` as well.

Example:

```python
from phcl import Block, Node


class Resource(Node):
    pass


class MainService(Resource["web"]):
    config = Block(path="/srv/app")
```

This renders as:

```hcl
resource "web" "main_service" {
  config {
    path = "/srv/app"
  }
}
```

Here:

- `resource` comes from the direct `Node` subclass `Resource`
- `"web"` comes from `Resource["web"]`
- `"main_service"` comes from the concrete class name `MainService`

## Registry

Project declaration classes are registered automatically.

`Node` itself and direct subclasses of `Node` are treated as root declaration types rather than concrete project declarations, so registration begins one level deeper.

This is what lets PHCL compile a file without a separate main entrypoint:

1. execute the file
2. collect declaration classes through the registry
3. render the concrete subset

## Abstract Nodes

Base declarations that should not be emitted can be marked abstract:

```python
from phcl import Node, abstract


@abstract
class BaseService(Node):
    pass
```

Abstract classes are skipped by renderable selection, while concrete subclasses can still become output declarations.

## References

`Node` also provides the `._` entrypoint for reference-space.

The mechanism itself belongs to the core. The concrete base path is defined by higher-level product layers.

`._` remains the explicit reference form.

Inside block and resource attribute values, PHCL may also coerce `Node` subclasses into reference form automatically during attribute normalization as a convenience.
