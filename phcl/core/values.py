from collections.abc import Iterable, Mapping
from typing import Any, Callable, Optional, Tuple


def normalize_value(
    value: Any,
    *,
    passthrough_types: Tuple[type, ...] = (),
    coerce: Optional[Callable[[Any], Any]] = None,
) -> Any:
    """
    Normalize Python values into PHCL's structural value model.

    Rules:
    - passthrough types are kept as-is
    - mappings are normalized recursively
    - lists/tuples and generic iterables become lists
    - string-like iterables are preserved
    - cyclic container structures raise a ValueError
    """

    return _normalize_value(
        value,
        seen=set(),
        passthrough_types=passthrough_types,
        coerce=coerce,
    )


def _normalize_value(
    value: Any,
    *,
    seen: set[int],
    passthrough_types: Tuple[type, ...],
    coerce: Optional[Callable[[Any], Any]],
) -> Any:
    if coerce is not None:
        value = coerce(value)

    if passthrough_types and isinstance(value, passthrough_types):
        return value

    normalize = getattr(value, "_phcl_normalize", None)
    if normalize is not None:
        return normalize()

    if isinstance(value, Mapping):
        marker = id(value)
        if marker in seen:
            raise ValueError("Cyclic Python structure cannot be lowered to HCL")

        seen.add(marker)
        try:
            return {
                key: _normalize_value(
                    item,
                    seen=seen,
                    passthrough_types=passthrough_types,
                    coerce=coerce,
                )
                for key, item in value.items()
            }
        finally:
            seen.remove(marker)

    if isinstance(value, list):
        marker = id(value)
        if marker in seen:
            raise ValueError("Cyclic Python structure cannot be lowered to HCL")

        seen.add(marker)
        try:
            return [
                _normalize_value(
                    item,
                    seen=seen,
                    passthrough_types=passthrough_types,
                    coerce=coerce,
                )
                for item in value
            ]
        finally:
            seen.remove(marker)

    if isinstance(value, tuple):
        marker = id(value)
        if marker in seen:
            raise ValueError("Cyclic Python structure cannot be lowered to HCL")

        seen.add(marker)
        try:
            return [
                _normalize_value(
                    item,
                    seen=seen,
                    passthrough_types=passthrough_types,
                    coerce=coerce,
                )
                for item in value
            ]
        finally:
            seen.remove(marker)

    if isinstance(value, (str, bytes)):
        return value

    if isinstance(value, Iterable):
        marker = id(value)
        if marker in seen:
            raise ValueError("Cyclic Python structure cannot be lowered to HCL")

        seen.add(marker)
        try:
            return [
                _normalize_value(
                    item,
                    seen=seen,
                    passthrough_types=passthrough_types,
                    coerce=coerce,
                )
                for item in value
            ]
        finally:
            seen.remove(marker)

    return value
