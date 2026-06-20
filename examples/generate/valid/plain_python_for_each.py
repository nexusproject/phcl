from phcl.runtime import label
from phcl.terraform import Output, Resource, each
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


BUCKETS = {
    "logs": "app-logs",
    "assets": "app-assets",
}

buckets = {}

for key, name in BUCKETS.items():

    @label("bucket", key)
    class _(Resource["aws_s3_bucket"]):
        for_each = {
            "primary": {"suffix": "primary"},
            "replica": {"suffix": "replica"},
        }

        bucket = name
        tags = {
            "Family": key,
            "Instance": each.value.suffix,
        }

    buckets[key] = _


class PrimaryBucketIds(Output):
    value = {
        key: bucket._["primary"].id
        for key, bucket in buckets.items()
    }
