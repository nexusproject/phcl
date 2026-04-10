#
#
import typing 
from .dsl import Node, Block
import re
from pprint import pprint as p


class Addressable:
    """
    Mixin for Terraform addressable blocks (resource, data).

    Enables Class["type"] and requires parametrization before instantiation.
    https://developer.hashicorp.com/terraform/cli/state/resource-addressing
    """

    __phcl_type: str  # Terraform resource/data type (resource_type)

    @classmethod
    def __class_getitem__(cls, type_name: str):
        safe = re.sub(r"[^0-9a-zA-Z_]", "_", type_name)
        return type(
            f"{cls.__name__}__{safe}",
            (cls,),
            {
                "__phcl_type": type_name,  # terraform type
            }
        )


class Resource(Addressable, Node):
    """
    Resource does not own initialization.
    Decorator sets internal PHCL metadata on the CLASS.
    """

    def _phcl_render(self):
        body = super()._phcl_render()

        t, l = self._get_identity()

        if not t or not l:
            raise ValueError("Resource type/label not set")

        return {
            "resource": {
                t: {
                    l: body
                }
            }
        }

class Data(Addressable, Node):
    """
    Resource does not own initialization.
    Decorator sets internal PHCL metadata on the CLASS.
    """

    def _phcl_render(self):
        body = super()._phcl_render()

        t, l = self._get_identity()

        if not t or not l:
            raise ValueError("Resource type/label not set")

        return {
            "resource": {
                t: {
                    l: body
                }
            }
        }


class Dynamic(Block):
    pass