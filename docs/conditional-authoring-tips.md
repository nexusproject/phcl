# Conditional Authoring Tips

Most PHCL conditionals are ordinary Python `if` statements. Use them when
Python should decide which attributes or declarations exist in the generated
HCL.

## Optional Attributes

Use a normal `if` inside the class body when an attribute should exist only for
some inputs.

```python
from phcl.terraform import Resource


ENABLE_VERSIONING = True
KMS_KEY_ID = None


class LogsBucket(Resource["aws_s3_bucket"]):
    bucket = "app-logs"

    if KMS_KEY_ID is not None:
        server_side_encryption_configuration = {
            "rule": {
                "apply_server_side_encryption_by_default": {
                    "kms_master_key_id": KMS_KEY_ID,
                    "sse_algorithm": "aws:kms",
                }
            }
        }

    if ENABLE_VERSIONING:
        versioning = {
            "enabled": True,
        }
```

When the condition is false, the attribute is not defined on the declaration
class, so PHCL has nothing to render for it.

## Conditional Declarations

Use a normal `if` around a class declaration when the whole declaration should
exist only for some inputs.

```python
from phcl.terraform import Resource


ENABLE_LOGS = True


if ENABLE_LOGS:
    class LogsBucket(Resource["aws_s3_bucket"]):
        bucket = "app-logs"
```

When the condition is false, the class is never created and never enters the
PHCL registry.

## `when(...)` Helper

`when(...)` is useful when a class declaration should stay in place, but its
rendering should be toggled by a Python-side condition.

```python
from phcl.runtime import when
from phcl.terraform import Resource


ENABLE_LOGS = False


@when(ENABLE_LOGS)
class LogsBucket(Resource["aws_s3_bucket"]):
    bucket = "app-logs"
```

When the condition is false, the class still exists in Python and remains in
the PHCL registry, but it is not selected for rendering.

`when(...)` also works with `generate(...)`; the enabled state is applied to
the materialized generated declarations.

```python
from phcl.runtime import generate, this, when
from phcl.terraform import Resource


ENABLE_REPLICAS = False

REPLICAS = {
    "eu": {"bucket": "app-logs-eu"},
    "us": {"bucket": "app-logs-us"},
}


@when(ENABLE_REPLICAS)
@generate(REPLICAS)
class ReplicaBucket(Resource["aws_s3_bucket"]):
    bucket = this.value["bucket"]
```
