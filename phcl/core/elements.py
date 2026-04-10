#
#

from .dsl import Node, Block

class Resource(Node):
    """
    Resource does not own initialization.
    Decorator sets internal PHCL metadata on the CLASS.
    """

    # class level private
    __phcl_type = None
    __phcl_label = None

    @classmethod
    def _phcl_set_resource_metadata(cls, type_name, label):
        cls.__phcl_type = type_name
        cls.__phcl_label = label

    def _phcl_render(self):
        body = super()._phcl_render()

        t = self.__class__.__phcl_type
        l = self.__class__.__phcl_label

        if not t or not l:
            raise ValueError("Resource type/label not set by decorator")

        return {
            "resource": {
                t: {
                    l: body
                }
            }
        }

class Dynamic(Block):
    pass