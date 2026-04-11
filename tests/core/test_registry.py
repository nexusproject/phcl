import pytest

from phcl.core.registry import Registry


@pytest.fixture(autouse=True)
def reset_registry():
    Registry.reset()
    yield
    Registry.reset()


def test_add_registers_classes_in_order():
    class First:
        pass

    class Second:
        pass

    Registry.add(First)
    Registry.add(Second)

    assert Registry.renderables() == [First, Second]


def test_renderables_returns_copy_of_registry():
    class Service:
        pass

    Registry.add(Service)

    renderables = Registry.renderables()
    renderables.append("noise")

    assert Registry.renderables() == [Service]


def test_render_is_alias_for_renderables():
    class Service:
        pass

    Registry.add(Service)

    assert Registry.render() == [Service]


def test_reset_clears_registry():
    class Service:
        pass

    Registry.add(Service)
    Registry.reset()

    assert Registry.renderables() == []
