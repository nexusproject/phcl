from phcl.core.decorators import abstract
from phcl.runtime import generate, this
from phcl.terraform import Output, Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


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


class BucketIds(Output):
    value = {
        "logs": Bucket._["logs"].id,
        "assets": Bucket._["assets"].id,
    }
