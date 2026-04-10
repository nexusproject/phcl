#
#


class DSL:
    """
    Base class for declarative constructs.
    """

    @property
    def _phcl_attributes(self) -> dict:
        attrs = {}

        for base in reversed(self.__class__.mro()):
            if base is DSL:
                continue

            for name, value in base.__dict__.items():
                if name.startswith("_"):
                    continue
                if callable(value) and not isinstance(value, property):
                    continue

                if isinstance(value, property):
                    attrs[name] = getattr(self, name)
                else:
                    attrs[name] = value

        return attrs


class Node(DSL):
    """
    Base AST node capable of recursive rendering.
    """

    def _phcl_compute(self):
        pass

    @classmethod
    def _phcl_render_value(cls, value):
        if isinstance(value, Node):
            return value._phcl_render()

        if isinstance(value, list):
            return [cls._phcl_render_value(v) for v in value]

        if isinstance(value, dict):
            return {k: cls._phcl_render_value(v) for k, v in value.items()}

        return value

    def _phcl_render(self):
        self._phcl_compute()
        return {k: self._phcl_render_value(v) for k, v in self._phcl_attributes.items()}


class Block(Node):
    def __init__(self, **kwargs):
        super().__init__()
        self.__phcl_kwargs = kwargs

    def _phcl_render(self):
        base = super()._phcl_render()
        return {**base, **self.__phcl_kwargs}