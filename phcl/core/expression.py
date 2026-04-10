class Expression:
    """
    Raw HCL expression fragment.

    Expressions are kept opaque by the core DSL: they are authored as HCL text
    and later emitted by the renderer without string quoting.
    """

    __slots__ = ("source",)

    def __init__(self, source: str = ""):
        self.source = source.strip()

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return Expression(f"{self.source}.{name}" if self.source else name)

    def __getitem__(self, key):
        rendered = Expression.value(key).source
        return Expression(f"{self.source}[{rendered}]" if self.source else f"[{rendered}]")

    @classmethod
    def literal(cls, value):
        if value is None:
            return cls("null")
        if isinstance(value, bool):
            return cls("true" if value else "false")
        if isinstance(value, (int, float)):
            return cls(str(value))
        if isinstance(value, str):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return cls(f'"{escaped}"')
        raise TypeError(f"Unsupported expression literal: {type(value)!r}")

    @classmethod
    def value(cls, value):
        if isinstance(value, Expression):
            return value
        return cls.literal(value)

    def __str__(self):
        return self.source

    def __repr__(self):
        return f"Expression({self.source!r})"

    def __bool__(self):
        raise TypeError("HCL Expression cannot be used in Python boolean context")


def expr(source: str) -> Expression:
    return Expression(source)
