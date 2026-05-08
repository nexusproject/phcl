from phcl.core.declarative import Declarative


def test_merges_attributes_from_base_classes():
    class Base(Declarative):
        name = "base"
        enabled = True

    class Child(Base):
        region = "us-east-1"

    attrs = Child()._phcl_attributes

    assert attrs == {
        "name": "base",
        "enabled": True,
        "region": "us-east-1",
    }


def test_child_attributes_override_base_attributes():
    class Base(Declarative):
        name = "base"
        size = "small"

    class Child(Base):
        size = "large"

    attrs = Child()._phcl_attributes

    assert attrs["name"] == "base"
    assert attrs["size"] == "large"


def test_instance_attributes_override_class_attributes():
    class Config(Declarative):
        name = "base"
        enabled = False

    obj = Config()
    obj.enabled = True
    obj.region = "eu-west-1"

    attrs = obj._phcl_attributes

    assert attrs["name"] == "base"
    assert attrs["enabled"] is True
    assert attrs["region"] == "eu-west-1"


def test_properties_are_included_but_methods_and_phcl_names_are_skipped():
    class Config(Declarative):
        _secret = "hidden"
        _phcl_internal = "skip"
        kind = "service"

        @property
        def computed(self):
            return f"{self.kind}-computed"

        def helper(self):
            return "skip me"

    attrs = Config()._phcl_attributes

    assert attrs == {
        "_secret": "hidden",
        "kind": "service",
        "computed": "service-computed",
    }


def test_single_underscore_name_is_reserved_for_phcl_accessors():
    class Config(Declarative):
        _ = "skip"
        _secret = "hidden"

    assert Config()._phcl_attributes == {
        "_secret": "hidden",
    }


def test_nested_classes_are_preserved():
    class Nested:
        pass

    class Config(Declarative):
        nested = Nested

    attrs = Config()._phcl_attributes

    assert attrs["nested"] is Nested
