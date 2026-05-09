import pytest

from phcl.core.decorators import abstract
from phcl.core.nodes import Node
from phcl.core.registry import Registry


@pytest.fixture(autouse=True)
def reset_registry():
    Registry.reset()
    yield
    Registry.reset()


def test_abstract_marks_class_but_keeps_it_in_full_registry():
    class Service(Node):
        pass

    assert Service not in Registry.all()
    assert Service not in Registry.renderables()

    Service = abstract(Service)

    assert Service.__dict__["_phcl_abstract"] is True
    assert Service not in Registry.all()
    assert Service not in Registry.renderables()
