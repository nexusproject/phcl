# Dynamic Generation Tips

PHCL has two different generation layers:

- PHCL-side declaration materialization with `generate(...)` and `derive(...)`.
- Target-side iteration in generated HCL, such as Terraform `for_each` and
  `each`.

Use PHCL-side generation when Python should decide which declarations exist.
Use target-side iteration when the target tool should keep one declaration and
expand its instances during its own evaluation.

These layers can be used separately or together.

## `generate(...)`

`generate(...)` materializes multiple concrete declarations from one
class-first template.

```python
from phcl.runtime import generate, this
from phcl.terraform import Output, Resource


BUCKETS = {
    "logs": {
        "bucket": "app-logs",
        "purpose": "logs",
    },
    "assets": {
        "bucket": "app-assets",
        "purpose": "assets",
    },
}


@generate(BUCKETS)
class Bucket(Resource["aws_s3_bucket"]):
    bucket = this.value["bucket"]
    tags = {
        "Name": this.key,
        "Purpose": this.value["purpose"],
        "Label": this.label,
        "Order": this.index,
    }


class BucketIds(Output):
    value = {
        key: Bucket._[key].id
        for key in BUCKETS
    }
```

The decorated class is a template. It is not rendered directly. PHCL creates
concrete declaration classes such as `Bucket_logs` and `Bucket_assets` before
rendering.

Inside the template:

- `this.key` is the generation key.
- `this.index` is the integer position in input order.
- `this.value` is the original Python value for the item.
- `this.label` is the generated declaration identity, or `None` for declaration
  kinds without one.

See [`generate(...)` and `this`](./runtime.md#generate-and-this) in the runtime
docs for the full helper contract and validation rules.

Use mapping input when declaration identity matters. Mapping keys become stable
identity suffixes. List input is positional, so inserting or reordering items
can rename generated declarations.

## Inheritance and Generation

Use inheritance before `@generate(...)` when generated declarations share a
common body.

```python
from phcl.syntax import abstract
from phcl.runtime import generate, this
from phcl.terraform import Resource


@abstract
class ManagedBucket(Resource["aws_s3_bucket"]):
    force_destroy = True
    tags = {"ManagedBy": "PHCL"}


@generate(BUCKETS)
class Bucket(ManagedBucket):
    bucket = this.value["bucket"]
    tags = ManagedBucket.tags | {"Name": this.key}
```

The generated template itself should be the last step in the declaration
chain. Subclassing it afterwards is rejected because the class has template
semantics rather than ordinary declaration-base semantics.

When a one-off declaration should share the same base, inherit from the base
directly:

```python
class AuditBucket(ManagedBucket):
    bucket = "audit"
    tags = ManagedBucket.tags | {"Name": "audit"}
```

## Any Declaration Family

`generate(...)` is not limited to Terraform resources. It materializes PHCL
declarations, so the same mechanism works with any declaration family:
resources, data sources, variables, outputs, providers, locals, modules, or
dialect-specific declarations.

```python
from phcl.runtime import generate, this
from phcl.terraform import Locals, Provider, Variable


VARIABLES = {
    "region": {
        "type": "string",
        "description": "AWS region",
    },
    "environment": {
        "type": "string",
        "description": "Deployment environment",
    },
}


@generate(VARIABLES)
class ConfigVariable(Variable):
    type = this.value["type"]
    description = this.value["description"]


@generate({
    "primary": {"region": "us-east-1"},
    "replica": {"region": "eu-central-1"},
})
class Aws(Provider["aws"]):
    alias = this.key
    region = this.value["region"]


@generate({
    "build": {"component": "api"},
    "deploy": {"component": "worker"},
})
class ComponentLocals(Locals):
    scope = this.key
    component = this.value["component"]
```

For declaration families without a unique declaration identity, such as
`Locals`, `Provider`, or `Terraform`, `this.label` is `None`.

## Prepare Values Before Generation

`this.*` values are selectors resolved while PHCL materializes declarations.
Use them directly as attribute values or inside lists and mappings.

Prepare transformed values before passing data to `generate(...)`.

```python
BUCKETS = {
    env: {
        "bucket": f"app-{env}",
        "name": env.upper(),
    }
    for env in ["dev", "prod"]
}


@generate(BUCKETS)
class Bucket(Resource["aws_s3_bucket"]):
    bucket = this.value["bucket"]
    tags = {
        "Name": this.value["name"],
    }
```

## References to Generated Declarations

Select a generated declaration by generation key:

```python
class LogsBucketId(Output):
    value = Bucket._["logs"].id
```

If a list or mapping of references is needed, build it from the same Python
data used by `generate(...)`:

```python
class BucketArns(Output):
    value = {
        key: Bucket._[key].arn
        for key in BUCKETS
    }
```

`Bucket._` is not a reference to a rendered declaration by itself. The template
must be selected with `Bucket._["key"]`.

## Terraform `for_each` and `each`

Terraform `for_each` is target-side iteration. PHCL emits the declaration, and
Terraform expands instances later.

The Terraform dialect provides `each` as a reference to Terraform's `each`
object. It works the same whether the `for_each` value is assembled from Python
data or written as a native HCL expression.

Python-authored mapping:

```python
from phcl.terraform import Resource, each


INSTANCES = {
    "a": {
        "name": "jobs-a",
        "instance_type": "t3.micro",
    },
    "b": {
        "name": "jobs-b",
        "instance_type": "t3.small",
    },
}


class FleetInstance(Resource["aws_instance"]):
    for_each = INSTANCES
    ami = "ami-1234567890abcdef0"
    instance_type = each.value.instance_type
    tags = {
        "Name": each.value.name,
        "Key": each.key,
    }
```

If the source data starts as a Python list, turn it into a mapping with stable
keys before assigning it to Terraform `for_each`:

```python
from phcl.terraform import Resource, each


INSTANCE_SPECS = [
    ("a", "jobs-a", "t3.micro"),
    ("b", "jobs-b", "t3.small"),
]

INSTANCES = {
    key: {
        "name": name,
        "instance_type": instance_type,
    }
    for key, name, instance_type in INSTANCE_SPECS
}


class FleetFromPython(Resource["aws_instance"]):
    for_each = INSTANCES
    ami = "ami-1234567890abcdef0"
    instance_type = each.value.instance_type
    tags = {
        "Name": each.value.name,
    }
```

For Terraform resources, mappings are the practical Python-authored shape
because they provide stable instance keys.

HCL-authored value:

```python
from phcl.syntax import hcl
from phcl.terraform import Resource, each


class FleetInstance(Resource["aws_instance"]):
    for_each = hcl("toset(var.instance_names)")
    ami = "ami-1234567890abcdef0"
    instance_type = "t3.micro"
    tags = {
        "Name": each.value,
    }
```

PHCL does not change the meaning of Terraform `for_each`; it only renders the
value. Use a collection shape that is valid for the Terraform construct being
authored.

## `generate(...)` with Terraform `for_each`

PHCL-side generation and Terraform-side iteration can be combined. The generated
declaration is selected first, then Terraform instance indexing can be applied.

```python
from phcl.runtime import generate, this
from phcl.terraform import Output, Resource, each


BUCKETS = {
    "logs": {"bucket": "app-logs"},
    "assets": {"bucket": "app-assets"},
}


@generate(BUCKETS)
class Bucket(Resource["aws_s3_bucket"]):
    for_each = {
        "primary": {"suffix": "primary"},
        "replica": {"suffix": "replica"},
    }

    bucket = this.value["bucket"]
    tags = {
        "Family": this.key,
        "Instance": each.value.suffix,
    }
```

Reference a generated declaration first, then the Terraform instance:

```python
class PrimaryLogBucketId(Output):
    value = Bucket._["logs"]["primary"].id
```

## `this` and `each`

`this` and `each` live at different times.

`this` belongs to PHCL generation:

- available only inside `@generate(...)`
- resolved while Python materializes declarations
- selects values from the data passed to `generate(...)`

`each` belongs to Terraform:

- available when the generated Terraform declaration uses `for_each`
- resolved by Terraform, not PHCL
- refers to the current target-side instance

Both can appear in the same declaration when both layers are being used.

## `derive(...)`

Most data-driven declaration materialization should use `generate(...)`.

Use `derive(...)` when code needs full control over the generation flow: custom
loops, cross-products, conditional materialization, or naming rules that do not
fit one `generate(...)` mapping.

```python
from itertools import product

from phcl.syntax import abstract
from phcl.runtime import derive
from phcl.terraform import Resource


@abstract
class RegionalBucket(Resource["aws_s3_bucket"]):
    force_destroy = True


ENVS = ["dev", "prod"]
REGIONS = ["us_east_1", "eu_central_1"]


for env, region in product(ENVS, REGIONS):
    derive(
        RegionalBucket,
        f"{env}_{region}",
        bucket=f"app-{env}-{region}",
        tags={
            "Env": env,
            "Region": region,
        },
    )
```

`derive(...)` creates one concrete declaration class from an ancestor. It is a
lower-level materialization helper, not the common path for everyday repeated
declarations.
