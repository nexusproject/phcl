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


def abstract(cls):
    cls.__phcl_abstract = True
    return cls


class Registry(type):
    _registry = []

    def __init__(self, *args):
        name, bases = args[0], args[1]

        phcl_types = [
            getattr(parent, "__phcl_type", None)
            for parent in bases
            if hasattr(parent, "__phcl_type")
        ]
        if not phcl_types:
            return

        if len(phcl_types) > 1:
            raise Exception(
                f"{name} cannot be derived from two or more Resource/Data types"
            )

        setattr(self, "__phcl_label", name)
        Registry._registry.append(self)

    @classmethod
    def render(cls):
        return [
            node()._phcl_render()
            for node in cls._registry
            if not node.__dict__.get("__phcl_abstract")
        ]


class Node(Declarative, metaclass=Registry):
    """
    Base AST node capable of recursive rendering.
    """

    def _get_identity(self):
        return getattr(self, "__phcl_type"), getattr(self, "__phcl_label")


    def _phcl_render(self):
        return {
            k: v._phcl_render() if hasattr(v, "_phcl_render") else v
            for k, v in self._phcl_attributes.items()
        }


class Block(Declarative):
    def __init__(self, **kwargs):
        self.__phcl_kwargs = kwargs

    def _render_value(self, v):
        if hasattr(v, "_phcl_render"):
            if isinstance(v, type):
                v = v()
            return v._phcl_render()

        if isinstance(v, list):
            return [self._render_value(x) for x in v]

        if isinstance(v, dict):
            return {k: self._render_value(x) for k, x in v.items()}

        return v

    def _phcl_render(self):
        base = dict(getattr(type(self), "_phcl_attributes", {}))  # <-- ВОТ ЭТО
        base.update(self.__phcl_kwargs)  # kwargs поверх

        p(base)
        return {k: self._render_value(v) for k, v in base.items()}


