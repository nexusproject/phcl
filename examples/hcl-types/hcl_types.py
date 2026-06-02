from phcl.terraform import TerraformPHCL as PHCL  # noqa: N812
from phcl.terraform import Output, Variable
from phcl.types import ANY, BOOL, LIST, NUMBER, OBJECT, OPTIONAL, STRING, TUPLE


class Region(Variable):
    type = STRING
    default = "us-east-1"


class Enabled(Variable):
    type = BOOL
    default = True


class Ports(Variable):
    type = LIST(NUMBER)
    default = [80, 443]


class Settings(Variable):
    type = OBJECT(
        {
            "name": STRING,
            "enabled": OPTIONAL(BOOL),
        }
    )


class Pair(Variable):
    type = TUPLE([STRING, NUMBER])


class Payload(Output):
    value = {
        "region": Region,
        "enabled": Enabled,
        "ports": Ports,
    }


class RawPayload(Variable):
    type = ANY
