# File-Backed Blocks Example

This example covers file-backed block composition:

- `yaml_block(...)` loads environment config as a reusable `Block` fragment.
- `json_block(...)` loads shared tag and ingress fragments.
- `at=(...)` selects nested mappings without using dotted-path syntax.
- Declarative inheritance refines loaded fragments.
- `block_dict(...)` turns assembled tag fragments back into object-like values.

Build it with:

```sh
python3 -m phcl build examples/file-backed-blocks
```
