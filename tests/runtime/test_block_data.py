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
    with pytest.raises(TypeError, match=r"invalid key: PHCL block attribute name 1 must be a string"):
        dict_block({1: "api"})


def test_dict_block_rejects_keys_that_are_not_python_identifiers():
    with pytest.raises(ValueError, match=r"invalid key: PHCL block attribute name 'not-valid'"):
        dict_block({"not-valid": "api"})


def test_dict_block_rejects_python_keywords():
    with pytest.raises(ValueError, match=r"cannot be a Python keyword"):
        dict_block({"class": "api"})


def test_dict_block_rejects_reserved_keys():
    with pytest.raises(ValueError, match=r"names cannot start with '_'"):
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


def test_json_block_selects_nested_mapping_with_list_at(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"envs": {"dev": {"name": "api"}}}', encoding="utf-8")

    Config = json_block(path, at=["envs", "dev"])

    assert Config()._phcl_attributes == {"name": "api"}


def test_json_block_treats_dotted_string_at_as_one_key(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"envs.dev": {"name": "api"}}', encoding="utf-8")

    Config = json_block(path, at="envs.dev")

    assert Config()._phcl_attributes == {"name": "api"}


def test_json_block_rejects_non_mapping_selection(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"dev": ["api"]}', encoding="utf-8")

    with pytest.raises(TypeError, match=r"selection at='dev' must be a mapping"):
        json_block(path, at="dev")


def test_json_block_rejects_missing_selection_key(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"dev": {"name": "api"}}', encoding="utf-8")

    with pytest.raises(KeyError, match=r"selection at='prod' does not exist"):
        json_block(path, at="prod")


def test_json_block_rejects_selection_that_cannot_continue(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"envs": ["dev"]}', encoding="utf-8")

    with pytest.raises(TypeError, match=r"selection at='envs' cannot continue at 'dev'"):
        json_block(path, at=("envs", "dev"))


def test_json_block_rejects_invalid_at_type(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"dev": {"name": "api"}}', encoding="utf-8")

    with pytest.raises(TypeError, match="at must be a string key"):
        json_block(path, at=123)  # type: ignore[arg-type]


def test_json_block_rejects_invalid_at_key_type(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"dev": {"name": "api"}}', encoding="utf-8")

    with pytest.raises(TypeError, match="at must contain only string keys"):
        json_block(path, at=("dev", 1))  # type: ignore[list-item]


def test_json_block_uses_dict_block_key_validation(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"not-valid": "api"}', encoding="utf-8")

    with pytest.raises(ValueError, match=r"selection root contains invalid PHCL block attributes"):
        json_block(path)


def test_yaml_block_builds_block_base_from_file_mapping(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("dev:\n  name: api\n  replicas: 2\n", encoding="utf-8")

    Config = yaml_block(path, at="dev")

    assert Config()._phcl_attributes == {
        "name": "api",
        "replicas": 2,
    }
