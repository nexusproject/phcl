from phcl.runtime import generate
from phcl.terraform import Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


@generate(
    {
        "_dev": {"bucket": "example"},
    }
)
class Bucket(Resource["aws_s3_bucket"]):
    bucket = "example"
