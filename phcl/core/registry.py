class Registry:
    """
    Global registry for top-level declaration classes.

    The registry intentionally stores all discovered declaration classes.
    Higher-level integrations can then ask for narrower views such as only
    concrete renderables.
    """

    _phcl_registry = []

    @classmethod
    def add(cls, node_cls):
        cls._phcl_registry.append(node_cls)

    @classmethod
    def all(cls):
        return list(cls._phcl_registry)

    @classmethod
    def renderables(cls):
        return [
            node_cls
            for node_cls in cls._phcl_registry
            if not node_cls.__dict__.get("_phcl_abstract", False)
        ]

    @classmethod
    def render(cls):
        return cls.renderables()

    @classmethod
    def reset(cls):
        cls._phcl_registry.clear()
