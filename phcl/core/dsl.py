#
#
from pprint import pprint as p


class Declarative:
    """
    Base class for declarative constructs.
    """

    @property
    def _phcl_attributes(self) -> dict:
        attrs = {}

        for base in reversed(self.__class__.mro()):
            if base is Declarative:
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


class Registry(type):
    _registry = []

    def __init__(self, *args):
        phcl_types = [
            getattr(parent, "__phcl_type", None)
            for parent in args[1]
            if hasattr(parent, "__phcl_type")
        ]
        if not phcl_types:
            return

        if len(phcl_types) > 1:
            raise (
                Exception(
                    f"{args[0]} cannot be derived from two or more Resource/Data types"
                )
            )

        setattr(self, "__phcl_label", args[0])

        print("Registered --", args[0], args[1], self)

        Registry._registry.append(self)


class Node(Declarative, metaclass=Registry):
    """
    Base AST node capable of recursive rendering.
    """

    def _phcl_compute(self):
        pass

    def _get_identity(self):
        return getattr(self, "__phcl_type"), getattr(self, "__phcl_label")

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
        """Node default render."""
        self._phcl_compute()
        return {k: self._phcl_render_value(v) for k, v in self._phcl_attributes.items()}


class Block(Declarative):
    def __init__(self, **kwargs):
        # super().__init__()
        self.__phcl_kwargs = kwargs

    def _phcl_render(self):
        """Block default render."""
        return {**self.__phcl_kwargs}
