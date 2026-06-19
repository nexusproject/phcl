import pytest

from phcl.core.expression import Reference, hcl
from phcl.core.nodes import Block, Node
from phcl.render.hcl2 import build_hcl, quote_string, render_block, render_value, walk_block
from phcl.runtime import label


def test_quote_string_escapes_quotes_and_backslashes():
    assert quote_string('a"b\\c') == '"a\\"b\\\\c"'


def test_render_value_supports_scalars_expressions_references_and_collections():
    assert render_value(None) == "null"
    assert render_value(True) == "true"
    assert render_value(False) == "false"
    assert render_value(42) == "42"
    assert render_value("hello") == '"hello"'
    assert render_value(hcl("var.region")) == "var.region"
    assert render_value(Reference("aws_instance.web.id")) == "aws_instance.web.id"
    assert render_value([]) == "[]"
    assert render_value({}) == "{}"
    assert render_value(["a", 1]) == '["a", 1]'
    assert render_value({"name": "web"}) == '{\n  name = "web"\n}'


def test_render_value_raises_for_unsupported_objects():
    with pytest.raises(TypeError, match="Unsupported HCL value"):
        render_value(object())


def test_walk_block_splits_scalar_attributes_and_nested_blocks():
    class Service(Block):
        _phcl_kind = "service"
        enabled = True
        config = Block(value="x")
        tags = ["a", "b"]
        ports = ("http", "https")
        ingress = [Block(port=80), Block(port=443)]

    attrs, nested = walk_block(Service())

    assert attrs == [
        ("enabled", True),
        ("tags", ["a", "b"]),
        ("ports", ["http", "https"]),
    ]
    assert [name for name, _ in nested] == ["config", "ingress", "ingress"]


def test_walk_block_materializes_block_classes_as_nested_blocks():
    class HttpIngress(Block):
        port = 80

    class HttpsIngress(HttpIngress):
        port = 443

    class Service(Block):
        _phcl_kind = "service"
        ingress = [HttpIngress, HttpsIngress]

    attrs, nested = walk_block(Service())

    assert attrs == []
    assert [(name, child._phcl_attributes["port"]) for name, child in nested] == [
        ("ingress", 80),
        ("ingress", 443),
    ]


def test_render_block_renders_block_with_labels_attributes_and_nested_blocks():
    class Service(Node["api"]):
        _phcl_kind = "service"
        enabled = True
        source = hcl("var.source")
        meta = {"team": "platform"}
        config = Block(path="/srv/app")

    rendered = render_block(Service())

    assert rendered == (
        'service "api" "service" {\n'
        '  enabled = true\n'
        '  source = var.source\n'
        '  meta = {\n'
        '    team = "platform"\n'
        '  }\n'
        '\n'
        '  config {\n'
        '    path = "/srv/app"\n'
        '  }\n'
        '}\n'.rstrip()
    )


def test_render_block_can_disable_automatic_class_name_label_for_a_node_family():
    class TerraformLike(Node):
        _phcl_kind = "terraform"
        _phcl_auto_label = False

    class Settings(TerraformLike):
        required_version = ">= 1.8.0"

    rendered = render_block(Settings())

    assert rendered == (
        "terraform {\n"
        '  required_version = ">= 1.8.0"\n'
        "}"
    )


def test_render_block_uses_node_logical_name_for_automatic_label():
    class ResourceLike(Node["example"]):
        _phcl_kind = "resource"

    class Bucket(ResourceLike):
        name = "app"

        @classmethod
        def _phcl_logical_name(cls):
            return "logs"

    rendered = render_block(Bucket())

    assert rendered == (
        'resource "example" "logs" {\n'
        '  name = "app"\n'
        "}"
    )


def test_render_block_uses_label_decorator_for_node_logical_name():
    class ResourceLike(Node["example"]):
        _phcl_kind = "resource"

    @label("dev", "logs")
    class Bucket(ResourceLike):
        name = "app"

    rendered = render_block(Bucket())

    assert rendered == (
        'resource "example" "dev_logs" {\n'
        '  name = "app"\n'
        "}"
    )


def test_label_decorator_is_local_to_the_decorated_class():
    class ResourceLike(Node["example"]):
        _phcl_kind = "resource"

    @label("base")
    class Base(ResourceLike):
        pass

    class Child(Base):
        pass

    assert render_block(Base()) == 'resource "example" "base" {\n}'
    assert render_block(Child()) == 'resource "example" "child" {\n}'


def test_render_block_can_use_underscore_named_local_helper_class():
    class ProviderLike(Node["aws"]):
        _phcl_kind = "provider"
        _phcl_auto_label = False

    class _(ProviderLike):
        region = "us-east-1"

    rendered = render_block(_())

    assert rendered == (
        'provider "aws" {\n'
        '  region = "us-east-1"\n'
        "}"
    )


def test_render_block_preserves_explicit_labels_when_auto_label_is_disabled():
    class ProviderLike(Node["aws"]):
        _phcl_kind = "provider"
        _phcl_auto_label = False

    class Aws(ProviderLike):
        region = "us-east-1"

    rendered = render_block(Aws())

    assert rendered == (
        'provider "aws" {\n'
        '  region = "us-east-1"\n'
        "}"
    )


def test_render_block_raises_when_block_kind_is_missing():
    class Service(Block):
        pass

    with pytest.raises(ValueError, match="Block type is not set"):
        render_block(Service())


def test_build_hcl_renders_multiple_registered_classes_with_spacing():
    class Service(Node):
        _phcl_kind = "service"
        enabled = True

    class Worker(Node):
        _phcl_kind = "worker"
        replicas = 2

    rendered = build_hcl([Service, Worker])

    assert rendered == (
        'service "service" {\n'
        '  enabled = true\n'
        '}\n'
        '\n'
        'worker "worker" {\n'
        '  replicas = 2\n'
        '}\n'
    )


def test_build_hcl_returns_empty_string_for_empty_registry():
    assert build_hcl([]) == ""


def test_build_hcl_supports_custom_indentation():
    class Service(Node):
        _phcl_kind = "service"
        meta = {"team": "platform"}

    rendered = build_hcl([Service], indent=" " * 4)

    assert rendered == (
        'service "service" {\n'
        '    meta = {\n'
        '        team = "platform"\n'
        '    }\n'
        '}\n'
    )
