from phcl.core.decorators import abstract
from phcl.runtime import generate, this, when
from phcl.terraform import Output, Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


ENABLE_REPLICA_BUCKETS = False

BUCKETS = {
    "logs": {
        "bucket": "phcl-example-logs",
        "purpose": "logs",
    },
    "assets": {
        "bucket": "phcl-example-assets",
        "purpose": "assets",
    },
}

REPLICA_BUCKETS = {
    "eu": {
        "bucket": "phcl-example-logs-eu",
        "purpose": "replica",
    },
    "us": {
        "bucket": "phcl-example-logs-us",
        "purpose": "replica",
    },
}


@abstract
class ManagedBucket(Resource["aws_s3_bucket"]):
    force_destroy = True


@generate(BUCKETS)
class Bucket(ManagedBucket):
    bucket = this.value["bucket"]
    tags = {
        "Name": this.key,
        "Label": this.label,
        "Purpose": this.value["purpose"],
        "Order": this.index,
        "ManagedBy": "PHCL",
    }


@when(ENABLE_REPLICA_BUCKETS)
@generate(REPLICA_BUCKETS)
class ReplicaBucket(ManagedBucket):
    bucket = this.value["bucket"]
    tags = {
        "Name": this.key,
        "Purpose": this.value["purpose"],
        "ManagedBy": "PHCL",
    }


class BucketIds(Output):
    value = {
        "logs": Bucket._["logs"].id,
        "assets": Bucket._["assets"].id,
    }
