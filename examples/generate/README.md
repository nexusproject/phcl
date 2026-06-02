# generate(...) Example

These examples cover declaration materialization with `generate(...)`.

Working examples live in `valid/`:

- `mapping.py` shows mapping-driven materialization and references through
  `Bucket._["key"]`.
- `list.py` shows positional list materialization.
- `terraform_for_each.py` shows PHCL-side `generate(...)` combined with
  Terraform-side `for_each`.

Build them with:

```sh
python -m phcl build examples/generate/valid
```

Error examples live in `errors/` and intentionally fail when built one by one:

```sh
python -m phcl build examples/generate/errors/non_string_key.py
python -m phcl build examples/generate/errors/tuple_input.py
python -m phcl build examples/generate/errors/unsafe_key.py
python -m phcl build examples/generate/errors/underscore_key.py
python -m phcl build examples/generate/errors/stacked.py
python -m phcl build examples/generate/errors/bare_reference.py
python -m phcl build examples/generate/errors/subclass_template.py
```
