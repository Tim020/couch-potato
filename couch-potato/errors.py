class ModelError(Exception):
    pass


class FieldNotFound(ModelError):
    pass


class ModelAttributeError(ModelError):
    pass
