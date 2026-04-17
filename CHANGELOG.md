# Changelog

## v0.1.2 - 2026-04-17

- Improved CLI and build process
- Added structural casting for Python values in PHCL attribute space
- Added `jsonencode(...)` as a core expression helper
- Added automatic `Node` reference coercion in block and resource attribute values

## v0.1.1 - 2026-04-16

- Added module-level `PHCL` file configuration for compile targets
- Defaulted output extension to `.hcl` when `PHCL.extension` is omitted
- Moved generic value normalization into `Block`
- Added `terraform` optional dependency for installing the Terraform dialect as `phcl[terraform]`
- Updated documentation for the new CLI and installation surface

## v0.1.0 - 2026-04-11

- Initial PHCL core release
- Added native HCL2 renderer
- Added `hcl(...)`, `Reference`, `abstract`, and `generate`
- Added `phcl build` CLI
- Added core test suite
- Added initial documentation
