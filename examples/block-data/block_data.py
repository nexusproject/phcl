from phcl.core import Block
from phcl.runtime import block_dict, dict_block
from phcl.terraform import Output, Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


class BaseTags(dict_block({"Project": "phcl", "ManagedBy": "PHCL"})):
    Environment = "dev"


class WebTags(BaseTags):
    Component = "web"


class TcpIngress(
    dict_block(
        {
            "protocol": "tcp",
            "cidr_blocks": ["0.0.0.0/0"],
        }
    )
):
    description = "HTTP"
    from_port = 80
    to_port = 80


class HttpsIngress(TcpIngress):
    description = "HTTPS"
    from_port = 443
    to_port = 443


class OpenEgress(Block):
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]


class WebSecurityGroup(Resource["aws_security_group"]):
    name = "web"
    description = "Web access"
    vpc_id = "vpc-0123456789abcdef0"

    ingress = [
        TcpIngress,
        HttpsIngress,
    ]
    egress = [OpenEgress]
    tags = block_dict(WebTags(Name="web-sg"))


class RenderedTags(Output):
    value = block_dict(WebTags(Name="web"))


class RenderedIngress(Output):
    value = block_dict(HttpsIngress)
