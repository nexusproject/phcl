<h1>
  <img src="https://raw.githubusercontent.com/nexusproject/phcl/main/assets/phcl-logo-dashed.svg" width="70" align="absmiddle"
       style="margin-right: 8px;">
  PHCL
  <img src="https://codecov.io/gh/nexusproject/phcl/branch/main/graph/badge.svg"
       align="right">
</h1>

PHCL is a Python-based Infrastructure as Code (IaC) tool for dynamic infrastructure workflows.

It provides an authoring and generation layer for HCL-based tools such as
Terraform, OpenTofu, and Packer.

Declarations are written as Python classes. The source stays close to the shape
of HCL while adding composition, dynamic generation, and integration with
Python data and logic.

## Example

```python
class Logs(Resource["aws_s3_bucket"]):
    bucket = "app-logs"
    force_destroy = True
    tags = {
        "Name": "logs",
        "ManagedBy": "PHCL",
    }


class BucketId(Output):
    value = Logs._.id
```

renders as native HCL:

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "app-logs"
  force_destroy = true
  tags = {
    Name = "logs"
    ManagedBy = "PHCL"
  }
}

output "bucket_id" {
  value = aws_s3_bucket.logs.id
}
```

## Use Cases

PHCL is useful when HCL is derived from project data rather than written
directly: RBAC rules, users, roles, regions, environments, inventories, service
definitions, or other source-of-truth records. When used alongside an existing
Python project, PHCL can share data, constants, validation, and project logic,
adapting generated configuration to the application it belongs to.

For example, repeated declarations can be generated from normal Python data:

```python
BUCKETS = {
    "logs": {"bucket": "app-logs"},
    "assets": {"bucket": "app-assets"},
}


@generate(BUCKETS)
class Bucket(Resource["aws_s3_bucket"]):
    bucket = this.value["bucket"]
    tags = {"Name": this.key}
```

PHCL also fits incremental adoption in existing HCL projects: generate one
file, one subtree, or one environment at a time, while the output remains plain
HCL that can live next to hand-written configuration.

## CLI

Install PHCL:

```bash
pip install phcl
```

Install PHCL with the Terraform dialect:

```bash
pip install 'phcl[terraform]'
```

Build one file or a source tree:

```bash
ENV=dev phcl build src --out-dir envs/dev/
```

Example output:

```text
==> build src
  write src/backend.py -> envs/dev/backend.tf
  write src/database.py -> envs/dev/database.tf
  write src/network.py -> envs/dev/network.tf
  write src/security.py -> envs/dev/security.tf

==> done in 0.06s
  13 written, 0 skipped, 0 failed
```

## Documentation

- [Docs](https://github.com/nexusproject/phcl/blob/main/docs/index.md)
- [CLI](https://github.com/nexusproject/phcl/blob/main/docs/cli.md)
- [Runtime helpers](https://github.com/nexusproject/phcl/blob/main/docs/runtime.md)
- [HCL identifiers and Python attribute syntax](https://github.com/nexusproject/phcl/blob/main/docs/hcl-python-identifiers.md)
