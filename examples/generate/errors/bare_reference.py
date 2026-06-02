from phcl.runtime import generate
from phcl.terraform import Output, Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


@generate({"logs": {}})
class Bucket(Resource["aws_s3_bucket"]):
    bucket = "example"


class BucketId(Output):
    value = Bucket._.id
