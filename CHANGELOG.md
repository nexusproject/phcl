# Changelog

## v0.4.4

- Allowed `dict_block(...)` and file-backed block helpers to use valid HCL identifiers such as Python keywords and names containing `-`
- Limited PHCL-reserved attribute names to `_` and the `_phcl_` prefix so ordinary underscore-prefixed HCL attributes are preserved
- Added documentation explaining HCL identifiers versus Python attribute syntax

## v0.4.3

- Added `path_target()` for accessing the active `phcl build <target>` directory during generation
- Improved `dict_block(...)` validation diagnostics for invalid PHCL block attribute keys
- Clarified `dict_block(...)` documentation for block-shaped mappings versus arbitrary object maps
- Shortened file-backed block diagnostics relative to the active build target when possible

## v0.4.2

- Added `hcl_format(...)` as a typed wrapper for HCL `format(...)` calls
- Improved `json_block(...)` and `yaml_block(...)` diagnostics for `at` selections and invalid block-shaped mappings
- Documented `at=(...)` nested selection for file-backed block helpers

## v0.4.1

- Added `json_block(...)` and `yaml_block(...)` helpers for building `Block` bases from file-backed JSON/YAML mappings
- Added support for external config/resource fragments built on top of the 0.4.0 block/data composition primitives

## v0.4.0

- Added `dict_block(...)` for building generated `Block` bases from mappings
- Added `block_dict(...)` for converting assembled `Block` attributes back into mappings
- Fixed nested block normalization so `Block` subclasses can be used directly as composable fragments, for example `ingress = [TcpIngress, HttpsIngress]`

## v0.3.2

- Added `hcl_call(...)` for building arbitrary HCL function calls from PHCL/Python values
- Added explicit `hcl_jsonencode(...)` and `hcl_yamlencode(...)` wrappers while keeping `jsonencode(...)` as a compatibility alias
- Added explicit `hcl_file(...)` and `hcl_templatefile(...)` wrappers while keeping `file(...)` as a compatibility alias
- Deprecated `jsonencode(...)` and `file(...)` in favor of `hcl_jsonencode(...)` and `hcl_file(...)`
- Added `heredoc(...)` as the preferred runtime helper for HCL heredoc expressions
- Changed `render_file(...)` to return an HCL heredoc expression by default; pass `heredoc=False` for plain text
- Deprecated `multiline(...)` and `render_file(..., multiline=...)` in favor of `heredoc(...)` and `render_file(..., heredoc=...)`
- Updated the CLI build output to report PHCL deprecation warnings with source locations

## v0.3.1

- Fixed block construction so `self` can be used as a normal HCL attribute name
- Fixed node reference accessors for Python 3.13 compatibility
- Added regression coverage for both fixes

## v0.3.0

- Added the new `phcl.runtime` surface for Python-side build-time helpers
- Added `path_module()`, `multiline()`, and `render_file()`
- Added `file(...)` to the `phcl.syntax` authoring surface
- Added runtime-focused examples for the new helpers
- Reorganized tests to separate `syntax` and `runtime` coverage
- Updated docs to document `syntax` and `runtime` as distinct layers
- Simplified expression docs so they focus on the shared `Expression` / `Reference` model

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
