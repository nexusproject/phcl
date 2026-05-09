import pytest

from phcl.core import Block
from phcl.core.decorators import abstract
from phcl.core.expression import hcl
from phcl.core.nodes import Node
from phcl.core.registry import Registry
from phcl.render.hcl2 import render_block
from phcl.runtime import block_dict, derive, dict_block, generate, json_block, this, yaml_block


@pytest.fixture(autouse=True)
def reset_registry():
    Registry.reset()
    yield
    Registry.reset()


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


def test_dict_block_allows_hcl_identifiers_that_are_not_python_identifiers():
    class Service(dict_block({"app-name": "api"})):
        enabled = True

    assert Service()._phcl_attributes == {
        "app-name": "api",
        "enabled": True,
    }


def test_dict_block_allows_python_keywords_that_are_valid_hcl_identifiers():
    class Service(dict_block({"from": "noreply@example.com"})):
        pass

    assert Service()._phcl_attributes == {
        "from": "noreply@example.com",
    }


def test_dict_block_rejects_keys_that_are_not_hcl_identifiers():
    with pytest.raises(ValueError, match=r"invalid key: PHCL block attribute name 'AWS:SourceArn'"):
        dict_block({"AWS:SourceArn": "api"})


def test_dict_block_allows_underscore_keys():
    class Service(dict_block({"_secret": "ok"})):
        pass

    assert Service()._phcl_attributes == {
        "_secret": "ok",
    }


def test_dict_block_rejects_phcl_reserved_keys():
    with pytest.raises(ValueError, match=r"names cannot start with '_phcl_'"):
        dict_block({"_phcl_secret": "nope"})


def test_dict_block_rejects_single_underscore_key():
    with pytest.raises(ValueError, match=r"attribute name '_' is reserved"):
        dict_block({"_": "nope"})


def test_block_dict_rejects_non_block_values():
    with pytest.raises(TypeError, match="Block"):
        block_dict({"name": "api"})


def test_derive_materializes_declaration_from_ancestor_and_explicit_label():
    @abstract
    class Resource(Node["aws_api_gateway_rest_api"]):
        _phcl_kind = "resource"

    @abstract
    class RegionalApi(Resource):
        endpoint_configuration = {"types": ["REGIONAL"]}

    Api = derive(RegionalApi, "public", description="Public API")

    assert Api.__name__ == "public"
    assert render_block(Api()) == (
        'resource "aws_api_gateway_rest_api" "public" {\n'
        '  endpoint_configuration = {\n'
        '    types = ["REGIONAL"]\n'
        '  }\n'
        '  description = "Public API"\n'
        "}"
    )
    assert Registry.renderables() == [Api]


def test_derive_uses_calling_module_for_generated_class():
    Derived = derive(Block, "derived")

    assert Derived.__module__ == __name__


def test_derive_rejects_non_block_ancestor():
    with pytest.raises(TypeError, match="Block ancestor"):
        derive(object, "public")


def test_derive_rejects_empty_label():
    with pytest.raises(ValueError, match="cannot be empty"):
        derive(Block, "")


def test_derive_validates_attribute_names():
    with pytest.raises(ValueError, match=r"derive\(\.\.\.\) invalid attribute"):
        derive(Block, "public", **{"AWS:SourceArn": "api"})


def test_generate_materializes_declarations_from_mapping_with_key_suffix():
    @abstract
    class Resource(Node["aws_s3_bucket"]):
        _phcl_kind = "resource"

    @generate({
        "dev": {"bucket": "app-dev"},
        "prod": {"bucket": "app-prod"},
    })
    class Bucket(Resource):
        bucket = this.value["bucket"]
        tags = {
            "Env": this.key,
            "Index": this.index,
        }

    BucketDev, BucketProd = Registry.renderables()

    assert Bucket.__dict__["_phcl_abstract"] is True
    assert BucketDev.__name__ == "Bucket_dev"
    assert BucketProd.__name__ == "Bucket_prod"
    assert render_block(BucketDev()) == (
        'resource "aws_s3_bucket" "bucket_dev" {\n'
        '  bucket = "app-dev"\n'
        '  tags = {\n'
        '    Env = "dev"\n'
        '    Index = 0\n'
        '  }\n'
        "}"
    )
    assert render_block(BucketProd()) == (
        'resource "aws_s3_bucket" "bucket_prod" {\n'
        '  bucket = "app-prod"\n'
        '  tags = {\n'
        '    Env = "prod"\n'
        '    Index = 1\n'
        '  }\n'
        "}"
    )


def test_generate_preserves_original_value_objects():
    class Config:
        name = "api"

    @abstract
    class Resource(Node["example"]):
        _phcl_kind = "resource"

    @generate({"dev": Config()})
    class Service(Resource):
        name = this.value.name

    [ServiceDev] = Registry.renderables()

    assert ServiceDev()._phcl_attributes["name"] == "api"


def test_generate_materializes_declarations_from_list_with_positional_keys():
    @abstract
    class Resource(Node["example"]):
        _phcl_kind = "resource"

    @generate([
        {"name": "api"},
        {"name": "worker"},
    ])
    class Service(Resource):
        name = this.value["name"]
        generation_key = this.key
        generation_index = this.index

    Service0, Service1 = Registry.renderables()

    assert Service0.__name__ == "Service_0"
    assert Service1.__name__ == "Service_1"
    assert Service0()._phcl_attributes == {
        "name": "api",
        "generation_key": "0",
        "generation_index": 0,
    }
    assert Service1()._phcl_attributes == {
        "name": "worker",
        "generation_key": "1",
        "generation_index": 1,
    }


def test_generate_rejects_unsupported_iterables():
    with pytest.raises(TypeError, match="mapping or list"):
        generate(("dev", "prod"))

    with pytest.raises(TypeError, match="mapping or list"):
        generate({"dev", "prod"})


def test_generate_rejects_non_string_keys():
    with pytest.raises(TypeError, match="keys must be strings"):
        generate({("dev", "blue"): {}})


def test_generate_omits_non_string_key_reprs_in_errors():
    key = tuple(f"part_{index}" for index in range(50))

    with pytest.raises(TypeError) as excinfo:
        generate({key: {}})

    assert str(excinfo.value) == "generate(...) keys must be strings"


def test_generate_rejects_label_unsafe_keys():
    with pytest.raises(ValueError, match=r"must match \[A-Za-z\]"):
        generate({"dev-blue": {}})


def test_generate_rejects_non_block_classes():
    with pytest.raises(TypeError, match="Block classes"):
        generate({"dev": {}})(object)


def test_generate_rejects_stacked_decorators():
    @abstract
    class Resource(Node["example"]):
        _phcl_kind = "resource"

    with pytest.raises(TypeError, match="cannot be stacked"):
        generate({"dev": {}})(
            generate({"blue": {}})(
                type(
                    "Service",
                    (Resource,),
                    {
                        "__module__": __name__,
                        "name": this.key,
                    },
                )
            )
        )


def test_generated_template_references_select_generated_classes_by_key():
    @abstract
    class Resource(Node["aws_s3_bucket"]):
        _phcl_kind = "resource"

        @classmethod
        def _phcl_reference_base(cls):
            return f"{cls._phcl_label[0]}.{cls._phcl_logical_name()}"

    @generate({"logs": {"bucket": "app-logs"}})
    class Bucket(Resource):
        bucket = this.value["bucket"]

    [BucketLogs] = Registry.renderables()

    assert str(Bucket._["logs"].arn) == "aws_s3_bucket.bucket_logs.arn"
    assert str(BucketLogs._.arn) == "aws_s3_bucket.bucket_logs.arn"


def test_generated_template_references_can_be_indexed_after_key_selection():
    @abstract
    class Resource(Node["aws_s3_bucket"]):
        _phcl_kind = "resource"

        @classmethod
        def _phcl_reference_base(cls):
            return f"{cls._phcl_label[0]}.{cls._phcl_logical_name()}"

    @generate({"logs": {}})
    class Bucket(Resource):
        for_each = ["primary"]

    assert str(Bucket._["logs"]["primary"].id) == (
        'aws_s3_bucket.bucket_logs["primary"].id'
    )


def test_generated_template_rejects_bare_reference_traversal():
    @abstract
    class Resource(Node["aws_s3_bucket"]):
        _phcl_kind = "resource"

    @generate({"logs": {}})
    class Bucket(Resource):
        pass

    with pytest.raises(TypeError, match=r'Bucket\._\["key"\]'):
        Bucket._.arn


def test_generated_template_rejects_missing_reference_keys():
    @abstract
    class Resource(Node["aws_s3_bucket"]):
        _phcl_kind = "resource"

    @generate({"logs": {}})
    class Bucket(Resource):
        pass

    with pytest.raises(KeyError, match="missing"):
        Bucket._["missing"]


def test_this_outside_generate_raises_clear_error():
    class Service(Block):
        name = this.key

    with pytest.raises(RuntimeError, match=r"`this` is only available inside `generate"):
        Service()._phcl_normalize_attr("name", Service.name)


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
    path.write_text('{"AWS:SourceArn": "api"}', encoding="utf-8")

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
