# Changelog

## v0.2.3

- Added native HCL type expressions in `phcl.types`
- Added documentation for HCL type expressions and their use in Terraform `Variable.type`

## v0.2.2

- Added PHCL version reporting in the CLI and core API
- Added `_phcl_auto_label` for controlling automatic class-name labels during HCL rendering
- Documented `class _(...)` as a local helper declaration pattern
- Updated `phcl[terraform]` to require the compatible patched dialect release

## v0.2.1

- Fixed module-aware compilation so imported declarations do not materialize into a sibling file's output just because they were loaded for `PHCL` config or shared references
- Added a CLI regression test covering imported declaration leakage during per-file compilation

## v0.2.0

- Split the public API into `phcl.core` and `phcl.syntax`
- Treat `phcl` as a namespace for core and dialect packages
- Changed the CLI compiler loading model to resolve source files as modules when possible, including `build <path>` and `build .` flows
- Added support for stable relative imports in multi-file PHCL project trees
- Aligned `PHCL` file config loading with `Declarative` inheritance and overrides
- Decomposed the CLI into dedicated loading, config, build, UI, and entrypoint modules
- Refreshed README and docs for the new loading and import surfaces
- This release changes module-loading and import behavior and may require updates to older PHCL projects

## v0.1.2

- Improved CLI and build process
- Added structural casting for Python values in PHCL attribute space
- Added `jsonencode(...)` as a core expression helper
- Added automatic `Node` reference coercion in block and resource attribute values

## v0.1.1

- Added module-level `PHCL` file configuration for compile targets
- Defaulted output extension to `.hcl` when `PHCL.extension` is omitted
- Moved generic value normalization into `Block`
- Added `terraform` optional dependency for installing the Terraform dialect as `phcl[terraform]`
- Updated documentation for the new CLI and installation surface

## v0.1.0

- Initial PHCL core release
- Added native HCL2 renderer
- Added `hcl(...)`, `Reference`, `abstract`, and `generate`
- Added `phcl build` CLI
- Added core test suite
- Added initial documentation
