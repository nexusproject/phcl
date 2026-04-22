from phcl.syntax import B


def test_syntax_exports_block_alias():
    assert B.__name__ == "Block"
