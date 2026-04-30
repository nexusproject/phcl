from phcl.syntax import B


def test_syntax_exports_block_alias():
    assert B.__name__ == "Block"


def test_block_alias_accepts_self_as_hcl_attribute():
    block = B(self="current")

    assert block._phcl_attributes["self"] == "current"
