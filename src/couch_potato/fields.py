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


class TypedArray(Field):
    __type__ = list

    def __init__(
        self, item_type: Field, nullable: bool = True, read_only: bool = False
    ):
        self.item_type = item_type
        super().__init__(nullable=nullable, read_only=read_only)

    def serialize(self, value: list):
        self.ensure_type(value)
        return [self.item_type.serialize(item) for item in value]

    def deserialize(self, value):
        self.ensure_type(value)
        return [self.item_type.deserialize(item) for item in value]
