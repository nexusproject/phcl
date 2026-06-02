from phcl.runtime import block_dict, json_block, path_module, yaml_block
from phcl.terraform import Output, Resource
from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812


ENV = "dev"
MODULE_DIR = path_module()

Config = yaml_block(MODULE_DIR / "envs.yaml", at=ENV)
PublicSubnetConfig = yaml_block(
    MODULE_DIR / "envs.yaml",
    at=(ENV, "network", "public", "subnet"),
)


class BaseTags(json_block(MODULE_DIR / "fragments.json", at="tags")):
    Environment = ENV


class WebTags(BaseTags):
    Component = Config.component


class TcpIngress(json_block(MODULE_DIR / "fragments.json", at=("ingress", "tcp"))):
    description = "HTTP"
    from_port = 80
    to_port = 80


class HttpsIngress(TcpIngress):
    description = "HTTPS"
    from_port = 443
    to_port = 443


class WebSecurityGroup(Resource["aws_security_group"]):
    name = Config.security_group_name
    description = "File-backed web access"
    vpc_id = Config.vpc_id

    ingress = [
        TcpIngress,
        HttpsIngress,
    ]
    tags = block_dict(WebTags(Name=Config.security_group_name))


class PublicSubnet(Resource["aws_subnet"], PublicSubnetConfig):
    vpc_id = Config.vpc_id
    tags = block_dict(WebTags(Name="public-a"))


class LoadedConfig(Output):
    value = block_dict(Config)


class LoadedPublicSubnetConfig(Output):
    value = block_dict(PublicSubnetConfig)


class LoadedTags(Output):
    value = block_dict(WebTags(Name="web"))
