from _types import Field


class Integer(Field):
    __type__ = int


class Float(Field):
    __type__ = float


class String(Field):
    __type__ = str
