from collections.abc import Iterable, Mapping


def abstract(cls):
    """
    Mark a declaration as abstract so it is skipped by the registry.
    """
    cls._phcl_abstract = True
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
