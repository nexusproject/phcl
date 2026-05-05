import pytest

from phcl.core import Block
from phcl.core.expression import hcl
from phcl.runtime import block_dict, dict_block, json_block, yaml_block


def test_dict_block_builds_block_base_from_mapping():
    class Service(dict_block({"name": "api", "replicas": 2})):
        pass

    assert isinstance(Service(), Block)
    assert Service()._phcl_attributes == {
        "name": "api",
        "replicas": 2,
    }


def test_dict_block_allows_class_attributes_to_override_mapping_values():
    class Service(dict_block({"name": "api", "replicas": 2})):
        replicas = 3

    assert Service()._phcl_attributes == {
        "name": "api",
        "replicas": 3,
    }


def test_block_dict_returns_shallow_attribute_mapping_from_block_instance():
    environment = hcl("var.environment")

    class Tags(Block):
        Project = "phcl"
        Environment = environment

    value = block_dict(Tags(Name="api"))

    assert value == {
        "Project": "phcl",
        "Environment": environment,
        "Name": "api",
    }


def test_block_dict_accepts_block_class():
    class Tags(Block):
        Project = "phcl"

    assert block_dict(Tags) == {"Project": "phcl"}


def test_block_dict_is_shallow():
    nested = Block(enabled=True)

    class Config(Block):
        settings = nested

    assert block_dict(Config)["settings"] is nested


def test_dict_block_rejects_non_mapping_values():
    with pytest.raises(TypeError, match="mapping"):
        dict_block([("name", "api")])


def test_dict_block_rejects_non_string_keys():
    with pytest.raises(TypeError, match="keys must be strings"):
        dict_block({1: "api"})


def test_dict_block_rejects_keys_that_are_not_python_identifiers():
    with pytest.raises(ValueError, match="valid Python identifiers"):
        dict_block({"not-valid": "api"})


def test_dict_block_rejects_python_keywords():
    with pytest.raises(ValueError, match="valid Python identifiers"):
        dict_block({"class": "api"})


def test_dict_block_rejects_reserved_keys():
    with pytest.raises(ValueError, match="reserved"):
        dict_block({"_secret": "nope"})


def test_block_dict_rejects_non_block_values():
    with pytest.raises(TypeError, match="Block"):
        block_dict({"name": "api"})


def test_json_block_builds_block_base_from_file_mapping(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"name": "api", "replicas": 2}', encoding="utf-8")

    Config = json_block(path)

    assert Config()._phcl_attributes == {
        "name": "api",
        "replicas": 2,
    }


def test_json_block_selects_nested_mapping_with_string_at(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"dev": {"name": "api"}}', encoding="utf-8")

    Config = json_block(path, at="dev")

    assert Config()._phcl_attributes == {"name": "api"}


def test_json_block_selects_nested_mapping_with_path_at(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"envs": {"dev": {"name": "api"}}}', encoding="utf-8")

    Config = json_block(path, at=("envs", "dev"))

    assert Config()._phcl_attributes == {"name": "api"}


def test_json_block_rejects_non_mapping_selection(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"dev": ["api"]}', encoding="utf-8")

    with pytest.raises(TypeError, match="must be a mapping"):
        json_block(path, at="dev")


def test_json_block_rejects_missing_selection_key(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"dev": {"name": "api"}}', encoding="utf-8")

    with pytest.raises(KeyError, match="prod"):
        json_block(path, at="prod")


def test_json_block_uses_dict_block_key_validation(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"not-valid": "api"}', encoding="utf-8")

    with pytest.raises(ValueError, match="valid Python identifiers"):
        json_block(path)


def test_yaml_block_builds_block_base_from_file_mapping(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("dev:\n  name: api\n  replicas: 2\n", encoding="utf-8")

    Config = yaml_block(path, at="dev")

    assert Config()._phcl_attributes == {
        "name": "api",
        "replicas": 2,
    }
