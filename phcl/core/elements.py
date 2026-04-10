import re
from typing import Any, Dict, Type
from .dsl import Node, Block


class Addressable:
    """
    Mixin for Terraform addressable blocks (resource, data).

    Enables Class["type"] syntax and stores Terraform resource/data type.
    https://developer.hashicorp.com/terraform/cli/state/resource-addressing
    """

    __phcl_type: str  # Terraform resource/data type

    @classmethod
    def __class_getitem__(cls, type_name: str) -> Type["Addressable"]:
        safe: str = re.sub(r"[^0-9a-zA-Z_]", "_", type_name)
        return type(
            f"{cls.__name__}__{safe}",
            (cls,),
            {
                "__phcl_type": type_name,
            },
        )


class Resource(Addressable, Node):
    """
    Terraform resource block.
    """

    def _phcl_render(self) -> Dict[str, Any]:
        t, l = self._get_identity()

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
        t, l = self._get_identity()

        return {
            "data": {
                t: {
                    l: super()._phcl_render()
                }
            }
        }


class Dynamic(Block):
    """
    Example of overriding default block render.
    """

    def _phcl_render(self) -> Dict[str, Any]:
        rendered: Dict[str, Any] = super()._phcl_render()
        return {
            "rendered": rendered
        }
