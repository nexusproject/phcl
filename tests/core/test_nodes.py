import pytest

from phcl.core.decorators import abstract
from phcl.core.expression import Reference
from phcl.core.nodes import Block, Node, class_to_label
from phcl.core.registry import Registry


@pytest.fixture(autouse=True)
def reset_registry():
    Registry.reset()
    yield
    Registry.reset()


def test_class_to_label_converts_pascal_case_and_acronyms():
    assert class_to_label("WebEC2") == "web_ec2"
    assert class_to_label("XMLParser") == "xml_parser"
    assert class_to_label("HttpServer") == "http_server"


def test_block_class_getitem_sets_labels_and_marks_variant_abstract():
    ApiBlock = Block["api", "v1"]

    assert ApiBlock._phcl_label == ("api", "v1")
    assert ApiBlock.__dict__["_phcl_abstract"] is True


def test_block_label_chains_and_tuple_labels_generate_the_same_class_name():
    Chained = Block["api"]["v1"]
    Packed = Block["api", "v1"]

    assert Chained.__name__ == Packed.__name__


def test_block_allows_underscore_constructor_attributes():
    assert Block(_secret="ok")._phcl_attributes["_secret"] == "ok"


def test_block_rejects_phcl_constructor_attributes():
    with pytest.raises(ValueError, match="reserved"):
        Block(_phcl_secret="nope")


def test_block_rejects_single_underscore_constructor_attribute():
    with pytest.raises(ValueError, match="reserved"):
        Block(_="nope")


def test_block_spec_includes_class_name_label_and_nested_values():
    class Service(Block["api"]):
        _phcl_kind = "service"
        replicas = 2
        metadata = {"team": "platform"}
        ports = (80, 443)

    spec = Service()._phcl_spec()

    assert spec == {
        "kind": "service",
        "labels": ("service", "api"),
        "attrs": {
            "replicas": 2,
            "metadata": {"team": "platform"},
            "ports": [80, 443],
        },
    }


def test_block_spec_materializes_generic_iterables_as_indexed_objects():
    class Service(Block):
        _phcl_kind = "service"
        ports = ("http", "https")

    spec = Service()._phcl_spec()

    assert spec["attrs"]["ports"] == ["http", "https"]


def test_node_direct_subclass_gets_kind_from_class_name_and_is_not_registered():
    class Service(Node):
        pass

    assert Service._phcl_kind == "service"
    assert Registry.all() == []
    assert Registry.renderables() == []


def test_grandchildren_and_deeper_descendants_of_node_are_registered():
    class Service(Node):
        pass

    class Api(Service):
        pass

    class Web(Api):
        pass

    assert Registry.all() == [Api, Web]
    assert Registry.renderables() == [Api, Web]


def test_abstract_node_is_not_registered_but_concrete_child_is():
    @abstract
    class Base(Node):
        pass

    class Concrete(Base):
        pass

    assert Base not in Registry.all()
    assert Base not in Registry.renderables()
    assert Concrete in Registry.renderables()


def test_node_reference_entrypoint_uses_reference_base():
    class Service(Node):
        @classmethod
        def _phcl_reference_base(cls) -> str:
            return "service.main"

    ref = Service._

    assert isinstance(ref, Reference)
    assert str(ref) == "service.main"


def test_node_reference_entrypoint_does_not_use_classmethod_property_stack():
    descriptor = Node.__dict__["_"]

    assert not isinstance(descriptor, classmethod)
    assert not isinstance(descriptor, property)


def test_node_reference_entrypoint_raises_for_non_addressable_nodes():
    class Service(Node):
        pass

    with pytest.raises(TypeError, match="not addressable"):
        _ = Service._


def test_block_normalization_coerces_node_subclasses_to_references_in_attrs():
    class Listener(Node):
        @classmethod
        def _phcl_reference_base(cls) -> str:
            return "aws_lb_listener.https_listener"

    class Service(Node):
        @classmethod
        def _phcl_reference_base(cls) -> str:
            return "aws_ecs_service.api"

    class Deployment(Service):
        depends_on = [Listener]
        wiring = {
            "primary": Service,
            "dependencies": (item for item in (Listener,)),
        }

    normalized_depends_on = Deployment()._phcl_normalize_attr("depends_on", Deployment.depends_on)
    normalized_wiring = Deployment()._phcl_normalize_attr("wiring", Deployment.wiring)

    assert [item.source for item in normalized_depends_on] == [Listener._.source]
    assert normalized_wiring["primary"].source == Service._.source
    assert [item.source for item in normalized_wiring["dependencies"]] == [Listener._.source]


def test_block_normalization_materializes_block_subclasses():
    class HttpIngress(Block):
        port = 80

    class HttpsIngress(HttpIngress):
        port = 443

    class Service(Block):
        ingress = [HttpIngress, HttpsIngress]

    normalized = Service()._phcl_normalize_attr("ingress", Service.ingress)

    assert [item._phcl_attributes for item in normalized] == [
        {"port": 80},
        {"port": 443},
    ]
