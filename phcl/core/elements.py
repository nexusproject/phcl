import re
from typing import Any, Dict, Type
from .dsl import Node, Block
from ..syntax.expressions import Expression

from pprint import pprint as p

def class_to_tf(name: str) -> str:
    """
    Convert Python class name (PascalCase with acronyms)
    to Terraform-style snake_case.

    Examples:
        WebEC2        -> web_ec2
        IAMRole      -> iam_role
        ALBListener  -> alb_listener
    """
    # split before last capital in acronym sequences
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def tf_to_class(name: str) -> str:
    """
    Convert Terraform-style snake_case identifier
    back to Python class name (PascalCase).

    Example:
        my_ec2          -> MyEc2
        web_server_ec2  -> WebServerEc2
    """
    return "".join(part.capitalize() for part in name.split("_"))


class Addressable:
    """
    Mixin for Terraform addressable blocks (resource, data).

    Enables Class["type"] syntax and stores Terraform resource/data type.
    https://developer.hashicorp.com/terraform/cli/state/resource-addressing
    """

    _phcl_type: str  # Terraform resource/data type
    _phcl_label: str  # Terraform label

    @classmethod
    def __class_getitem__(cls, type_name: str) -> Type["Addressable"]:
        safe: str = re.sub(r"[^0-9a-zA-Z_]", "_", type_name)
        return type(
            f"{cls.__name__}__{safe}",
            (cls,),
            {
                "_phcl_type": type_name,
                # "_phcl_label": class_to_tf(cls.__class__.__name__)
            },
        )
    
    @classmethod
    def _phcl_identity(cls) -> tuple[str, str]:
        t = getattr(cls, "_phcl_type", None)
        l = getattr(cls, "_phcl_label", class_to_tf(cls.__name__))

        if not t or not l:
            raise ValueError("Resource type/label not set")

        return t, l
    
    @classmethod
    @property
    def _(cls):
        t, l = getattr(cls, "_phcl_type"), getattr(cls, "_phcl_label", class_to_tf(cls.__name__))

        if issubclass(cls, Data):
            return Expression(f"data.{t}.{l}")

        return Expression(f"{t}.{l}")

class Resource(Addressable, Node):
    """
    Terraform resource block.
    """

    def _phcl_render(self) -> Dict[str, Any]:
        t, l = self.__class__._phcl_identity()

        return {
            "resource": {
                t: {
                    l: super()._phcl_render()
                }
            }
        }


class Data(Addressable, Node):
    """
    Terraform data block.
    """

    def _phcl_render(self) -> Dict[str, Any]:
        t, l = self.__class__._phcl_identity()

        return {
            "data": {
                t: {
                    l: super()._phcl_render()
                }
            }
        }