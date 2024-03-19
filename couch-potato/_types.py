from abc import ABCMeta
from dataclasses import dataclass, field
from typing import Dict, Type, Any

from couchbase.bucket import Bucket
from couchbase.collection import Collection
from couchbase.scope import Scope


@dataclass
class ScopeBind:
    scope: Scope
    collection_binds: Dict[str, Collection] = field(default_factory=dict)


@dataclass
class BucketBind:
    bucket: Bucket
    scope_binds: Dict[str, ScopeBind] = field(default_factory=dict)


class Field(metaclass=ABCMeta):
    __type__: Type

    def __init__(self, nullable: bool = True):
        self._nullable = nullable

    @classmethod
    def ensure_type(cls, value: Any):
        if not isinstance(value, cls.__type__):
            raise TypeError(f"Incorrect type for {value}, expected "
                            f"{cls.__type__} but got {type(value)}")

    def serialize(self, value):
        return value

    def deserialize(self, value):
        self.ensure_type(value)
        return value
