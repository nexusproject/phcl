from collections.abc import Iterable, Mapping

from .registry import Registry


def abstract(cls):
    """
    Mark a declaration as abstract so it is skipped by the registry.
    """
    cls._phcl_abstract = True
    Registry._phcl_registry = [
        node_cls for node_cls in Registry._phcl_registry if node_cls is not cls
    ]
    return cls

def generate(source):
    """
    Attach compile-time generation metadata to a declaration class.

    Normalization rules:
    - Mapping -> preserve key/value pairs
    - Iterable -> enumerate items into (index, value) pairs

    The core decorator only stores normalized generation data. Higher-level
    integrations decide how keys affect naming, labels, and emitted blocks.
    """

    if isinstance(source, Mapping):
        entries = list(source.items())
    elif isinstance(source, (str, bytes)):
        raise TypeError("generate() does not accept string-like iterables")
    elif isinstance(source, Iterable):
        entries = list(enumerate(source))
    else:
        raise TypeError("generate() expects a Mapping or an Iterable")

    def decorator(cls):
        cls._phcl_generate = entries
        return cls

    return decorator
