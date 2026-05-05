import pytest

from phcl.core import Block
from phcl.core.expression import hcl
from phcl.runtime import block_dict, dict_block


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
