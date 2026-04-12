class Expression:
    """
    Raw HCL expression fragment.

    Expressions are kept opaque by the core DSL: they are authored as HCL text
    and later emitted by the renderer without string quoting.
    """

    __slots__ = ("source",)

    def __init__(self, source: str = ""):
        self.source = source.strip()

    def __str__(self):
        return self.source

    def __repr__(self):
        return f"Expression({self.source!r})"

    def __bool__(self):
        raise TypeError("HCL Expression cannot be used in Python boolean context")


def hcl(source: str) -> Expression:
    """
    Wrap an inline native HCL expression.

    Use this as an escape hatch when a value should be emitted as HCL syntax
    exactly as written, rather than rendered from normal Python data.
    """
    return Expression(source)


class Reference(Expression):
    """
    Lazy traversal object for building HCL expression paths.

    A `Reference` stays as a lightweight path builder until it is rendered,
    at which point it behaves like a plain raw HCL expression fragment.
    """

    def __init__(self, source: str):
        super().__init__(source)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return Reference(f"{self.source}.{name}")

    def __getitem__(self, key):
        if isinstance(key, Expression):
            rendered = key.source
        elif isinstance(key, str):
            escaped = key.replace("\\", "\\\\").replace('"', '\\"')
            rendered = f'"{escaped}"'
        else:
            rendered = str(key)
        return Reference(f"{self.source}[{rendered}]")

    def __repr__(self):
        return f"Reference({self.source!r})"
