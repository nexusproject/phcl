from dataclasses import dataclass
from typing import Any, Optional

from phcl.core import Declarative

DEFAULT_OUTPUT_EXTENSION = ".hcl"


@dataclass(frozen=True)
class FileConfig:
    extension: Optional[str]
    indentation: str = "  "
    skip: bool = False


def normalize_extension(value: str) -> str:
    return value if value.startswith(".") else f".{value}"


def load_file_config(module_globals: dict[str, Any]) -> Optional[FileConfig]:
    config = module_globals.get("PHCL")
    if config is None:
        return None

    config_attrs: Optional[dict[str, Any]] = None
    if isinstance(config, Declarative):
        config_attrs = config._phcl_attributes
    elif isinstance(config, type) and issubclass(config, Declarative):
        config_attrs = config()._phcl_attributes

    if config_attrs is not None:
        extension = config_attrs.get("extension")
        indentation = config_attrs.get("indentation", "  ")
        skip = config_attrs.get("skip", False)
    else:
        extension = getattr(config, "extension", None)
        indentation = getattr(config, "indentation", "  ")
        skip = getattr(config, "skip", False)

    if extension is not None:
        extension = normalize_extension(extension)

    if not isinstance(indentation, str) or not indentation:
        raise TypeError("PHCL.indentation must be a non-empty string")

    return FileConfig(extension=extension, indentation=indentation, skip=bool(skip))
