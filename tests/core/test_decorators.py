import pytest

from phcl.core.decorators import abstract, generate
from phcl.core.nodes import Node
from phcl.core.registry import Registry


@pytest.fixture(autouse=True)
def reset_registry():
    Registry.reset()
    yield
    Registry.reset()


def test_abstract_marks_class_and_removes_it_from_registry():
    class Service(Node):
        pass

    assert Service in Registry.renderables()

    Service = abstract(Service)

    assert Service.__dict__["_phcl_abstract"] is True
    assert Service not in Registry.renderables()


def test_generate_preserves_mapping_entries():
    @generate({"web": {"size": "small"}, "api": {"size": "large"}})
    class Service:
        pass

    assert Service._phcl_generate == [
        ("web", {"size": "small"}),
        ("api", {"size": "large"}),
    ]


def test_generate_enumerates_iterables():
    @generate(["web", "api"])
    class Service:
        pass

    assert Service._phcl_generate == [
        (0, "web"),
        (1, "api"),
    ]


def test_generate_rejects_string_like_iterables():
    with pytest.raises(TypeError, match="string-like"):
        generate("web")


def test_generate_rejects_non_iterable_non_mapping():
    with pytest.raises(TypeError, match="expects a Mapping or an Iterable"):
        generate(42)
