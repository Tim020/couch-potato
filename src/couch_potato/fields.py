from datetime import datetime
from typing import Any, Dict, Type

from src.couch_potato._types import Field
from src.couch_potato.errors import FieldNotFound
from src.couch_potato.model import Model


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


class EmbeddedModel(Field):
    __type__ = Model

    def __init__(
        self, model_class: Type[Model], nullable: bool = True, read_only: bool = False
    ):
        if not issubclass(model_class, Model):
            raise TypeError("model_class must be a subclass of Model")
        self.model_class = model_class
        super().__init__(nullable=nullable, read_only=read_only)

    def serialize(self, value: Model):
        self.ensure_type(value)
        return value.to_json()

    def deserialize(self, value: Dict[str, Any]):
        cls_dict = {}
        for _key, field in self.model_class.__fields__.items():
            if _key not in value:
                raise FieldNotFound(f"Field {_key} not found within model json")
            cls_dict[_key] = field.deserialize(value[_key])
        ret = self.model_class.from_json(**cls_dict)
        self.ensure_type(ret)
        return ret


class TypedArray(Field):
    __type__ = list

    def __init__(
        self, item_type: Field, nullable: bool = True, read_only: bool = False
    ):
        if not isinstance(item_type, Field):
            raise TypeError("item_type must be an instance of Field")
        self.item_type = item_type
        super().__init__(nullable=nullable, read_only=read_only)

    def serialize(self, value: list):
        self.ensure_type(value)
        return [self.item_type.serialize(item) for item in value]

    def deserialize(self, value):
        self.ensure_type(value)
        return [self.item_type.deserialize(item) for item in value]
