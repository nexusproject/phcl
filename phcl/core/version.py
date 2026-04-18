from importlib.metadata import PackageNotFoundError, version


def get_version() -> str:
    try:
        return version("phcl")
    except PackageNotFoundError:
        return "0+unknown"


__version__ = get_version()

