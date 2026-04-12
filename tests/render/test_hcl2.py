import pytest

from phcl.core.expression import Reference, hcl
from phcl.core.nodes import Block, Node
from phcl.render.hcl2 import build_hcl, quote_string, render_block, render_value, walk_block


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
        ingress = [Block(port=80), Block(port=443)]

    attrs, nested = walk_block(Service())

    assert attrs == [
        ("enabled", True),
        ("tags", ["a", "b"]),
    ]
    assert [name for name, _ in nested] == ["config", "ingress", "ingress"]


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
