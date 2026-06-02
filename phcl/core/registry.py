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
    def renderables(cls, module_name=None):
        renderables = [
            node_cls
            for node_cls in cls._phcl_registry
            if not node_cls.__dict__.get("_phcl_abstract", False)
            and node_cls.__dict__.get("_phcl_enabled", True)
        ]

        if module_name is not None:
            renderables = [
                node_cls
                for node_cls in renderables
                if getattr(node_cls, "__module__", None) == module_name
            ]

        return renderables

    @classmethod
    def render(cls, module_name=None):
        return cls.renderables(module_name=module_name)

    @classmethod
    def reset(cls):
        cls._phcl_registry.clear()
