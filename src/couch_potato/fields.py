from datetime import datetime

from src.couch_potato._types import Field


class Integer(Field):
    __type__ = int


class Float(Field):
    __type__ = float


class String(Field):
    __type__ = str


class Boolean(Field):
    __type__ = bool


class DateTime(Field):
    __type__ = datetime

    def serialize(self, value: datetime):
        self.ensure_type(value)
        return value.isoformat()

    def deserialize(self, value):
        ret = datetime.fromisoformat(value)
        self.ensure_type(ret)
        return ret
