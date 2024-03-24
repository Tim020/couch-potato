from string import Formatter

from src.couch_potato._model import BaseModel, ModelMeta


class KeyGenerator:
    def __init__(self, format_str: str):
        self.format_str = format_str

    def generate(self, **kwargs):
        return self.format_str.format(**kwargs)

    @property
    def format_keys(self):
        return [i[1] for i in Formatter().parse(self.format_str) if i[1] is not None]


class Model(BaseModel, metaclass=ModelMeta):
    __read_only__: bool = False

    def __eq__(self, other):
        if not isinstance(other, Model):
            return False
        return self.__dict__ == other.__dict__
