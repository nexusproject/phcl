def abstract(cls):
    """
    Mark a declaration as abstract so it is skipped by renderable selection.
    """
    cls._phcl_abstract = True
    return cls
