from phcl.runtime import generate, this
from phcl.terraform import Locals, Output, Resource, Variable
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812
from phcl.types import STRING


SUBNETS = [
    {
        "cidr": "10.0.1.0/24",
        "az": "us-east-1a",
    },
    {
        "cidr": "10.0.2.0/24",
        "az": "us-east-1b",
    },
]


class VpcId(Variable):
    type = STRING


@generate(SUBNETS)
class Subnet(Resource["aws_subnet"]):
    vpc_id = VpcId
    cidr_block = this.value["cidr"]
    availability_zone = this.value["az"]
    tags = {
        "Name": this.key,
        "Label": this.label,
        "Order": this.index,
    }


class SubnetIds(Output):
    value = [
        Subnet._["0"].id,
        Subnet._["1"].id,
    ]


@generate({"dev": {"region": "us-east-1"}})
class GeneratedConfig(Locals):
    label = this.label
    region = this.value["region"]
