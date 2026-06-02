# Block Data Example

This example covers the 0.4.x block/data composition helpers:

- `dict_block(...)` builds reusable `Block` bases from mapping-shaped data.
- Declarative inheritance refines those fragments.
- `block_dict(...)` converts assembled block attributes back into object-like
  values for attributes such as `tags`.

Build it with:

```sh
python -m phcl build examples/block-data
```
