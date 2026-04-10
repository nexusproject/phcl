#
#

from typing import Union


class Expression:
    """
    Terraform HCL expression.
    """

    __slots__ = ("_body",)

    def __init__(self, body: str = ""):
        self._body = body  # raw HCL code (NO ${})

    @classmethod
    def lit(cls, s: str) -> "Expression":
        return cls(f'"{s}"')

    @classmethod
    def val(cls, v) -> "Expression":
        # numbers/bools/null -> code; strings -> literal by default
        if isinstance(v, Expression):
            return v
        if v is None:
            return cls("null")
        if isinstance(v, bool):
            return cls("true" if v else "false")
        if isinstance(v, (int, float)):
            return cls(str(v))
        if isinstance(v, str):
            return cls.lit(v)
        return cls(str(v))

    def __getattr__(self, item: str):
        return Expression(f"{self._body}.{item}" if self._body else item)

    def __getitem__(self, item):
        key = Expression.val(item)._body
        return Expression(f"{self._body}[{key}]" if self._body else key)

    def _phcl_render(self) -> str:
        return f"${{{self._body}}}"

    def __str__(self):
        return self._body

    def __repr__(self):
        return f"Expression({self._body!r})"

    def __bool__(self):
        raise TypeError("Terraform Expression cannot be used in Python boolean context")

    def _bin(self, op: str, other):
        other = Expression.val(other)
        return Expression(f"{self._body} {op} {other._body}")

    def __gt__(self, other): return self._bin(">", other)
    def __lt__(self, other): return self._bin("<", other)
    def __ge__(self, other): return self._bin(">=", other)
    def __le__(self, other): return self._bin("<=", other)
    def __eq__(self, other): return self._bin("==", other)
    def __ne__(self, other): return self._bin("!=", other)
    def __and__(self, other): return self._bin("&&", other)
    def __or__(self, other):  return self._bin("||", other)


def expr(s: str) -> Expression:
    return Expression(s.strip())

class Function(Expression):
    def __init__(self, name: str, *args):
        def render(arg):
            if isinstance(arg, Expression):
                return arg._body
            if isinstance(arg, bool):
                return "true" if arg else "false"
            if isinstance(arg, (int, float)):
                return str(arg)
            if isinstance(arg, str):
                return f'"{arg}"'
            if isinstance(arg, dict):
                items = []
                for k, v in arg.items():
                    key = f'"{k}"' if isinstance(k, str) else str(k)
                    items.append(f"{key} = {render(v)}")
                return "{" + ", ".join(items) + "}"
            if isinstance(arg, (list, tuple)):
                return "[" + ", ".join(render(v) for v in arg) + "]"
            raise TypeError(f"Unsupported arg type: {type(arg)}")

        rendered_args = [render(arg) for arg in args]
        super().__init__(f"{name}({', '.join(rendered_args)})")

# HCL functions
Scalar = Union[str, int, float, bool, Expression]

# ── core ──
def try_(a: Scalar, b: Scalar) -> Expression: return Function("try", a, b)
def can_(e: Expression) -> Expression: return Function("can", e)

# ── string ──
def join_(sep: str, items: Expression) -> Expression: return Function("join", sep, items)
def split_(sep: str, s: Scalar) -> Expression: return Function("split", sep, s)
def lower_(s: Scalar) -> Expression: return Function("lower", s)
def upper_(s: Scalar) -> Expression: return Function("upper", s)
def replace_(s: Scalar, a: str, b: str) -> Expression: return Function("replace", s, a, b)
def trimspace_(s: Scalar) -> Expression: return Function("trimspace", s)

# ── collection ──
def length_(v: Scalar) -> Expression: return Function("length", v)
def lookup_(m: Expression, k: Scalar, d: Scalar) -> Expression: return Function("lookup", m, k, d)
def contains_(c: Expression, v: Scalar) -> Expression: return Function("contains", c, v)
def concat_(*xs: Expression) -> Expression: return Function("concat", *xs)
def merge_(*ms: Expression) -> Expression: return Function("merge", *ms)
def keys_(m: Expression) -> Expression: return Function("keys", m)
def values_(m: Expression) -> Expression: return Function("values", m)
def range_(a: int, b: int = None, c: int = None) -> Expression:
    return Function("range", *(x for x in (a, b, c) if x is not None))

# ── type / convert ──
def tostring_(v: Scalar) -> Expression: return Function("tostring", v)
def tonumber_(v: Scalar) -> Expression: return Function("tonumber", v)
def tobool_(v: Scalar) -> Expression: return Function("tobool", v)
def tolist_(v: Scalar) -> Expression: return Function("tolist", v)
def toset_(v: Scalar) -> Expression: return Function("toset", v)
def tomap_(v: Scalar) -> Expression: return Function("tomap", v)

# ── encoding ──
def jsonencode_(v: Scalar) -> Expression: return Function("jsonencode", v)
def jsondecode_(v: Scalar) -> Expression: return Function("jsondecode", v)
def base64encode_(v: Scalar) -> Expression: return Function("base64encode", v)
def base64decode_(v: Scalar) -> Expression: return Function("base64decode", v)

# ── datetime ──
def timestamp_() -> Expression: return Function("timestamp")
def timeadd_(ts: Scalar, dur: str) -> Expression: return Function("timeadd", ts, dur)

# ── network ──
def cidrsubnet_(p: str, n: int, i: int) -> Expression: return Function("cidrsubnet", p, n, i)
def cidrhost_(p: str, h: int) -> Expression: return Function("cidrhost", p, h)



# Terraform namespaces
var = Expression("var")
local = Expression("local")
data = Expression("data")
module = Expression("module")
each = Expression("each")
count = Expression("count")
terraform = Expression("terraform")
path = Expression("path")
