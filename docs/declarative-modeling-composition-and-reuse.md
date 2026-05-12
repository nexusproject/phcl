# Declarative Modeling, Composition and Reuse

PHCL composition starts from a simple rule: a class body is a declaration body.
That makes ordinary Python inheritance useful for HCL authoring while keeping
the HCL shape visible in the source.

`Block` is the main composition unit: a reusable declaration body that can be
inherited, nested, repeated, converted, loaded from data, and used as a concrete
declaration or declaration fragment.

Alongside the longer `Block` name, PHCL provides `B` as a short alias. It is
the same object, not a separate mechanism, and is especially convenient for
inline nested block values.

## Declaration Bases

Use inheritance when several declarations have the same shape but different
local values.

```python
from phcl.syntax import abstract
from phcl.terraform import Resource


@abstract
class ManagedBucket(Resource["aws_s3_bucket"]):
    force_destroy = True
    tags = {
        "ManagedBy": "PHCL",
    }


class LogsBucket(ManagedBucket):
    bucket = "app-logs"
    tags = ManagedBucket.tags | {"Name": "logs"}


class AssetsBucket(ManagedBucket):
    bucket = "app-assets"
    tags = ManagedBucket.tags | {"Name": "assets"}
```

`ManagedBucket` is a reusable declaration body. It is marked `abstract` because
it is a base shape, not a real bucket that should be emitted.

Inherited attributes can be overridden normally. When a mapping or list should
be extended, merge it explicitly:

```python
tags = ManagedBucket.tags | {"Name": "logs"}
```

Subclass attributes override parent attributes; PHCL does not perform hidden
deep merges.

## Nested Block Fragments

Use `B(...)` for one-off nested blocks:

```python
from phcl.syntax import B, hcl
from phcl.terraform import Variable


class ImageTag(Variable["image_tag"]):
    type = "string"
    description = "Container image tag"

    validation = B(
        condition=hcl('var.image_tag != ""'),
        error_message="image_tag must not be empty",
    )
```

When the same nested block shape should be reused, promote it to a named
`Block` subclass.

```python
from phcl.core import Block
from phcl.terraform import Resource


class TcpIngress(Block):
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]


class HttpIngress(TcpIngress):
    description = "HTTP"
    from_port = 80
    to_port = 80


class HttpsIngress(TcpIngress):
    description = "HTTPS"
    from_port = 443
    to_port = 443


class WebSecurityGroup(Resource["aws_security_group"]):
    name = "web"
    description = "Web access"
    vpc_id = "vpc-0123456789abcdef0"

    ingress = [
        HttpIngress,
        HttpsIngress,
    ]
```

The reusable fragments remain ordinary HCL-shaped bodies. The surrounding
resource decides where they are used.

## Multiple Block Bases

`Block` fragments can also use normal Python multiple inheritance when
independent fragment bodies should be combined.

```python
from phcl.core import Block


class Tcp(Block):
    protocol = "tcp"


class PublicCidr(Block):
    cidr_blocks = ["0.0.0.0/0"]


class HttpIngress(Tcp, PublicCidr):
    description = "HTTP"
    from_port = 80
    to_port = 80
```

Multiple inheritance is intended for block fragments. Top-level declarations
use a single declaration family and compose their body through attributes,
nested blocks, object fragments, or ordinary refinement.

## Local Variations

A reusable block fragment can be extended or overridden at the point where it
is used. Constructor keyword arguments act as a local overlay on top of the
class body.

```python
from phcl.core import Block
from phcl.terraform import Resource


class TcpIngress(Block):
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]


class WebSecurityGroup(Resource["aws_security_group"]):
    name = "web"
    vpc_id = "vpc-0123456789abcdef0"

    ingress = [
        TcpIngress(
            description="HTTP",
            from_port=80,
            to_port=80,
        ),
        TcpIngress(
            description="HTTPS",
            from_port=443,
            to_port=443,
        ),
    ]
```

Use this for small local variations. If the same variation appears in several
places, promote it to a named subclass.

## Object-Valued Fragments

Some HCL attributes expect object values rather than nested blocks. Tags are a
common example. Author the shared structure as a block fragment, then convert it
with `block_dict(...)` at the point where an object value is needed.

```python
from phcl.core import Block
from phcl.runtime import block_dict
from phcl.terraform import Resource


class BaseTags(Block):
    Project = "billing"
    ManagedBy = "PHCL"


class ApiTags(BaseTags):
    Component = "api"


class ApiBucket(Resource["aws_s3_bucket"]):
    bucket = "billing-api"
    tags = block_dict(ApiTags(Environment="prod", Name="api"))
```

The fragment is authored through the same declarative model, while the rendered
attribute remains a normal HCL object value.

## Data-Backed Fragments

When existing Python, JSON, or YAML data already has the shape of a declaration
body, load it as a block base and refine it locally.

```python
from phcl.runtime import path_module, yaml_block
from phcl.terraform import Resource


ENV = "prod"
CONFIG = path_module() / "envs.yaml"


class Config(yaml_block(CONFIG, at=ENV)):
    backend_ami_id = ""
    key_pair_name = ""


class PublicSubnetDefaults(
    yaml_block(CONFIG, at=(ENV, "network", "public", "subnet"))
):
    map_public_ip_on_launch = True


class PublicSubnet(Resource["aws_subnet"]):
    vpc_id = Config.vpc_id
    cidr_block = PublicSubnetDefaults.cidr_block
    availability_zone = PublicSubnetDefaults.availability_zone
    map_public_ip_on_launch = PublicSubnetDefaults.map_public_ip_on_launch
```

`yaml_block(...)`, `json_block(...)`, and `dict_block(...)` serve as bridges
from data into PHCL's declaration fragment model. Once loaded, the fragment
follows the same inheritance and override rules as any other `Block`.
