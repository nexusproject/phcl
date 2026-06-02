from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812
from phcl.syntax import B, hcl
from phcl.terraform import Data, Output, Provider, Resource, Terraform, Variable, each
from phcl.types import LIST, STRING


class Settings(Terraform):
    required_version = ">= 1.8.0"


class Region(Variable):
    type = STRING
    default = "us-east-1"


class VpcId(Variable):
    type = STRING


class InstanceNames(Variable):
    type = LIST(STRING)
    default = ["web-a", "web-b"]


class Aws(Provider["aws"]):
    region = Region._


class AmazonLinux(Data["aws_ami"]):
    most_recent = True
    owners = ["amazon"]
    filter = [
        {
            "name": "name",
            "values": ["al2023-ami-2023.*-x86_64"],
        }
    ]


class WebSecurityGroup(Resource["aws_security_group"]):
    name = "web"
    description = "Web access"
    vpc_id = VpcId._

    ingress = [
        B(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        B(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ]

    egress = [
        B(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ]


class WebInstance(Resource["aws_instance"]):
    ami = AmazonLinux._.id
    instance_type = "t3.micro"
    vpc_security_group_ids = [WebSecurityGroup._.id]
    tags = {
        "Name": "web",
    }


class FleetInstance(Resource["aws_instance"]):
    for_each = hcl("toset(var.instance_names)")
    ami = AmazonLinux._.id
    instance_type = "t3.micro"
    vpc_security_group_ids = [WebSecurityGroup._.id]
    tags = {
        "Name": each.value,
    }


class FleetFromPython(Resource["aws_instance"]):
    for_each = [
        {
            "name": f"jobs-{suffix}",
            "instance_type": size,
        }
        for suffix, size in [
            ("a", "t3.micro"),
            ("b", "t3.small"),
        ]
    ]
    ami = AmazonLinux._.id
    instance_type = each.value.instance_type
    vpc_security_group_ids = [WebSecurityGroup._.id]
    tags = {
        "Name": each.value.name,
    }


class InstanceId(Output):
    value = WebInstance._.id
