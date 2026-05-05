# Roadmap

This roadmap describes PHCL's development direction. It is not a release
contract. Future version ranges are provisional and may change.

## Release Lines

### Completed / Current

#### 0.1.x: Core HCL Rendering and Basic PHCL Declarations

- Block / Node model
- Native HCL2 renderer
- Basic CLI build
- Initial expression/reference helpers

#### 0.2.x: Project Loading, Module Boundaries, and Dialect Packaging

- `phcl.core` / `phcl.syntax` split
- Namespace/dialect package model
- Module-aware CLI loading
- Relative imports
- PHCL file config

#### 0.3.x: Expression and Runtime Authoring Helpers

- `hcl_call(...)`
- `hcl_jsonencode(...)` / `hcl_yamlencode(...)`
- `hcl_file(...)` / `hcl_templatefile(...)`
- `heredoc(...)` / `render_file(...)`
- Deprecation warning reporting

#### 0.4.x: Block/Data Composition

- `dict_block(...)`
- `block_dict(...)`
- `json_block(...)` / `yaml_block(...)`
- Mapping-backed `Block` bases
- External config/resource fragments

### Planned

#### 0.5.x: Declaration Generation and Materialization

Focus:

- Strengthen `generate(...)`
- Generated context model
- `.derive(...)`
- Class-first materialization flows
- Scoped multi-file generation from one PHCL source

### Later Directions

Potential later work:

#### JSON Output and Renderer Backends

- JSON renderer
- `.tf.json` / dialect JSON output
- Output format config
- Possible JSON-first generation mode

#### Migration, Porting, and HCL Fidelity

- Port existing HCL into PHCL-shaped declarations
- Description/comment preservation
- Generated HCL readability/fidelity
- Migration tooling

#### Higher-Level Stacks and Infrastructure Primitives

- First-class stacks
- Reusable cloud primitives
- Stack catalogs/docs/schema
- Architecture-level composition
