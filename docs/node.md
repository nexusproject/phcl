# Node

`Node` is PHCL's top-level declaration type.

`Block` models generic HCL structure. `Node` adds PHCL-specific top-level behavior.

In core PHCL, `Node` is primarily a declaration base.

It is usually not the final user-facing abstraction in a product layer. Product-specific packages typically build more concrete node types on top of it, such as resource-like or provider-like declarations.

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

```python
from phcl import Node


class Service(Node):
    pass
```

This renders as:

```hcl
service "service" {}
```

Rules:

- direct subclasses of `Node` derive their block kind from the class name by default
- the final top-level label is also derived from the class name

This uses PHCL's normal class-to-label conversion.

Example:

- `Service` -> `service`
- `WebAPI` -> `web_api`
- `InstanceId` -> `instance_id`

So:

- the block kind for a direct `Node` subclass defaults from the class name
- the generated top-level logical label also defaults from the class name

## Relationship to `Block`

`Node` still uses the same body model as `Block`.

That means a node can contain:

- plain attributes
- nested `Block(...)` values
- repeated nested blocks

Example:

```python
from phcl import Block, Node


class Service(Node):
    config = Block(path="/srv/app")
```

This renders as:

```hcl
service "service" {
  config {
    path = "/srv/app"
  }
}
```

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
