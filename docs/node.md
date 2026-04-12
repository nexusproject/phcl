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
from phcl import Node, abstract


@abstract
class Resource(Node):
    pass


class MainResource(Resource):
    image = "nginx"
```

Here:

- `Node` provides the core top-level declaration behavior
- `Resource` becomes a product-specific root node base
- `MainResource` is a concrete declaration built on top of that base

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

## Relationship to `Block`

`Node` still uses the same body model as `Block`.

That means a node can contain:

- plain attributes
- nested `Block(...)` values
- repeated nested blocks

It also inherits label support from `Block`, so product-specific root node types can use `[...]` as well.

Example:

```python
from phcl import Block, Node, abstract


@abstract
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

Concrete `Node` subclasses are registered automatically.

This is what lets PHCL compile a file without a separate main entrypoint:

1. execute the file
2. collect concrete `Node` subclasses
3. render the registry

## Abstract Nodes

Base declarations that should not be emitted can be marked abstract:

```python
from phcl import Node, abstract


@abstract
class BaseService(Node):
    pass
```

The abstract class itself is not registered, but concrete subclasses still can be.

## References

`Node` also provides the `._` entrypoint for reference-space.

The mechanism itself belongs to the core. The concrete base path is defined by higher-level product layers.
