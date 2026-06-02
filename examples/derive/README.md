# derive(...) Example

This example covers the 0.5.x declaration materialization helper:

- `@abstract` keeps a reusable declaration base out of the rendered output.
- `derive(...)` creates concrete declarations from that base with explicit
  trailing labels.
- Generated classes can still be inherited in normal class-first PHCL style.
- Keyword arguments passed to `derive(...)` become ordinary HCL body
  attributes on the generated declaration.

Build it with:

```sh
python -m phcl build examples/derive
```
