from phcl.runtime import path_module, yaml_block


InvalidConfig = yaml_block(path_module() / "invalid.yaml", at=("dev", "reserved"))
