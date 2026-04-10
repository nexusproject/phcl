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


def expr(source: str) -> Expression:
    return Expression(source)
