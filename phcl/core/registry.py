class Registry:
    """
    Global registry for concrete top-level declarations.

    The core DSL itself is structure-oriented; this helper is responsible for
    collecting classes that should be emitted by higher-level integrations.
    """

    _phcl_registry = []

    @classmethod
    def add(cls, node_cls):
        cls._phcl_registry.append(node_cls)

    @classmethod
    def renderables(cls):
        return list(cls._phcl_registry)

    @classmethod
    def render(cls):
        return cls.renderables()
