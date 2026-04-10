#
#

from ..core.dsl import Node

class Expression(Node):
    """
    Terraform HCL expression node (${...}).

    Рендерится в чистую строку вида "${...}" и не содержит атрибутов.
    """

    def __init__(self, body: str):
        self.body = body

    def _phcl_render(self):
        return f"${{{self.body}}}"

    def __str__(self):
        return self._phcl_render()

    def __repr__(self):
        return f"Expression({self.body!r})"


def expr(s: str) -> Expression:
    """Wrap string as Terraform HCL expression (${...})."""
    return Expression(s)


class _PathProxy:
    def __init__(self, path: str):
        self._path = path

    def __getattr__(self, item: str):
        if not self._path:
            return _PathProxy(item)
        return _PathProxy(f"{self._path}.{item}")

    def __getitem__(self, item):
        if isinstance(item, tuple):
            raise TypeError("Terraform supports only single-key indexing")

        if isinstance(item, str):
            item_repr = f'"{item}"'
        else:
            item_repr = str(item)

        if not self._path:
            return _PathProxy(item_repr)

        return _PathProxy(f"{self._path}[{item_repr}]")

    def __repr__(self):
        return f"Expression({self._path!r})"

    def __str__(self):
        return f"${{{self._path}}}"
    
    def expr(self):
        return Expression(self._path)


# Terraform special namespaces
terraform = _PathProxy("terraform")
var = _PathProxy("var")
each = _PathProxy("each")
local = _PathProxy("local")
tf = _PathProxy("")   # tf.aws_s3_bucket.main.id → Expression("aws_s3_bucket.main.id")

