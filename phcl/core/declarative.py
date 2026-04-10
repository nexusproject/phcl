from typing import Any, Dict


class Declarative:
    """
    Declarative DSL base.

    Provides declarative composition via inheritance:
    attributes defined on base classes are merged and overridden
    by subclasses to form the final configuration body.

    This class does not represent an HCL block itself —
    it only defines *what* should be rendered, not *how*.
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
