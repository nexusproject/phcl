from typing import Any, Dict, List, Type


class Declarative:
    """
    Declarative base.
    """

    @property
    def _phcl_attributes(self) -> Dict[str, Any]:
        attrs: Dict[str, Any] = {}

        for base in list(reversed(self.__class__.mro())) + [self]:
            if base is Declarative:
                continue

            for name, value in base.__dict__.items():
                if name.startswith("_"):
                    continue

                # skip methods, keep classes and properties
                if callable(value) and not isinstance(value, (property, type)):
                    continue

                if isinstance(value, property):
                    attrs[name] = getattr(self, name)
                else:
                    attrs[name] = value

        return attrs


class Registry(type):
    """
    Registers Node subclasses that should be rendered.
    """

    _registry: List[Type["Node"]] = []

    def __init__(self, *args: Any) -> None:
        name: str = args[0]
        bases: tuple[type, ...] = args[1]

        phcl_types = [
            getattr(parent, "__phcl_type", None)
            for parent in bases
            if hasattr(parent, "__phcl_type")
        ]

        if not phcl_types:
            return

        if len(phcl_types) > 1:
            raise Exception(
                f"{name} cannot inherit multiple Resource/Data types"
            )

        setattr(self, "__phcl_label", name)
        Registry._registry.append(self)

    @classmethod
    def render(cls) -> List[Dict[str, Any]]:
        return [
            node()._phcl_render()
            for node in cls._registry
            if not node.__dict__.get("__phcl_abstract")
        ]


class Renderable:
    """
    Default render.
    Recursive materialization of declarative values.
    """

    def _phcl_render_value(self, v: Any) -> Any:
        if hasattr(v, "_phcl_render"):
            v = v() if isinstance(v, type) else v
            return v._phcl_render()

        if isinstance(v, list):
            return [self._phcl_render_value(x) for x in v]

        if isinstance(v, dict):
            return {k: self._phcl_render_value(x) for k, x in v.items()}

        return v

    def _phcl_render(self) -> Dict[str, Any]:
        return {
            k: self._phcl_render_value(v)
            for k, v in self._phcl_attributes.items()
        }


class Node(Declarative, Renderable, metaclass=Registry):
    """
    Top-level PHCL entity.
    """

    def _get_identity(self) -> tuple[str, str]:
        t, l = getattr(self, "__phcl_type"), getattr(self, "__phcl_label")

        if not t or not l:
            raise ValueError("Resource type/label not set")
        
        return t, l


class Block(Declarative, Renderable):
    """
    Nested block. Supports inheritance + ctor override.
    """

    def __init__(self, **kwargs: Any) -> None:
        for k in kwargs:
            if k.startswith("_"):
                raise ValueError("Attributes starting with '_' are reserved")

        self.__dict__.update(kwargs)


def abstract(cls: Type[Node]) -> Type[Node]:
    """Marks Node class as non-renderable."""
    cls.__phcl_abstract = True
    return cls
