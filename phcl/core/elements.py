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
    Resource does not own initialization.
    Decorator sets internal PHCL metadata on the CLASS.
    """

    def _phcl_render(self):
        t, l = self._get_identity()

        return {
            "data": {
                t: {
                    l: super()._phcl_render()
                }
            }
        }


class Dynamic(Block):
    def _phcl_render(self):
        rendered = super()._phcl_render()
        return { "rendered" : rendered }