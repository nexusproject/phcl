#
#
import typing 
from .dsl import Node, Block
import re
from pprint import pprint as p

def sanitize(type_name: str) -> str:
    """Convert Terraform type name into a safe Python class identifier."""
    return re.sub(r"[^0-9a-zA-Z_]", "_", type_name)


class Resource(Node):
    """
    Resource does not own initialization.
    Decorator sets internal PHCL metadata on the CLASS.
    """

    @classmethod
    def __class_getitem__(cls, type_name: str):
        """Resource['subtype']"""
        safe = sanitize(type_name)
        return type(
            f"Resource__{safe}",
            (cls,),
            {"__phcl_type": safe}
        )
    
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

class Data(Node):
    """
    Resource does not own initialization.
    Decorator sets internal PHCL metadata on the CLASS.
    """

    @classmethod
    def __class_getitem__(cls, type_name: str):
        """Data['subtype']"""
        safe = sanitize(type_name)
        return type(
            f"Data__{safe}",
            (cls,),
            {"__phcl_type": safe}
        )
    
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