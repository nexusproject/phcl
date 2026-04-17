import pytest

from phcl.core.expression import Reference, hcl
from phcl.core.values import normalize_value


def test_normalize_value_preserves_scalars_and_string_like_values():
    assert normalize_value(None) is None
    assert normalize_value(True) is True
    assert normalize_value(42) == 42
    assert normalize_value("hello") == "hello"
    assert normalize_value(b"hello") == b"hello"


def test_normalize_value_materializes_tuples_and_generators_into_lists():
    values = normalize_value((item for item in (1, 2, 3)))

    assert values == [1, 2, 3]
    assert normalize_value(("a", "b")) == ["a", "b"]


def test_normalize_value_preserves_expression_and_reference_inside_nested_structures():
    normalized = normalize_value(
        {
            "image": hcl("var.app_image"),
            "subnet_ids": (Reference("data.aws_subnets.selected").ids[index] for index in range(2)),
            "enabled": True,
        }
    )

    assert normalized["image"].source == "var.app_image"
    assert [item.source for item in normalized["subnet_ids"]] == [
        "data.aws_subnets.selected.ids[0]",
        "data.aws_subnets.selected.ids[1]",
    ]
    assert normalized["enabled"] is True


def test_normalize_value_supports_nested_mixed_iterables():
    normalized = normalize_value(
        {
            "ports": {port for port in (8080, 9090)},
            "metadata": (
                {"name": name, "enabled": True}
                for name in ("api", "worker")
            ),
        }
    )

    assert sorted(normalized["ports"]) == [8080, 9090]
    assert normalized["metadata"] == [
        {"name": "api", "enabled": True},
        {"name": "worker", "enabled": True},
    ]


def test_normalize_value_raises_for_cyclic_lists():
    values = []
    values.append(values)

    with pytest.raises(ValueError, match="Cyclic Python structure"):
        normalize_value(values)


def test_normalize_value_raises_for_cyclic_mappings():
    values = {}
    values["self"] = values

    with pytest.raises(ValueError, match="Cyclic Python structure"):
        normalize_value(values)


def test_normalize_value_supports_custom_coercion_hook():
    normalized = normalize_value(
        {"items": (1, 2, 3)},
        coerce=lambda value: list(value) if isinstance(value, tuple) else value,
    )

    assert normalized == {"items": [1, 2, 3]}
