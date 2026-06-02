from phcl.runtime import generate, this
from phcl.terraform import Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


@generate({"dev": {}})
@generate({"blue": {}})
class Bucket(Resource["aws_s3_bucket"]):
    bucket = this.key
