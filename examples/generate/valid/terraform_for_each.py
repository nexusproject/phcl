from phcl.runtime import generate, this
from phcl.terraform import Output, Resource, each
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


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


class PrimaryBucketIds(Output):
    value = {
        "logs": Bucket._["logs"]["primary"].id,
        "assets": Bucket._["assets"]["primary"].id,
    }
