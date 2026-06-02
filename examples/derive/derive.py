from phcl.core.decorators import abstract
from phcl.runtime import derive
from phcl.terraform import Output, Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


@abstract
class ManagedBucket(Resource["aws_s3_bucket"]):
    force_destroy = True
    tags = {
        "ManagedBy": "PHCL",
    }


LogsBucket = derive(
    ManagedBucket,
    "logs",
    bucket="phcl-example-logs",
    tags={
        "ManagedBy": "PHCL",
        "Name": "logs",
    },
)

AssetsBucket = derive(
    ManagedBucket,
    "assets",
    bucket="phcl-example-assets",
    tags={
        "ManagedBy": "PHCL",
        "Name": "assets",
    },
)


class PreviewAssetsBucket(AssetsBucket):
    bucket = "phcl-example-preview-assets"
    tags = {
        "ManagedBy": "PHCL",
        "Name": "preview-assets",
    }


class BucketNames(Output):
    value = {
        "logs": LogsBucket._.id,
        "assets": AssetsBucket._.id,
        "preview_assets": PreviewAssetsBucket._.id,
    }
