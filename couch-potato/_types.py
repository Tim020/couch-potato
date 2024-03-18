from abc import ABCMeta
from dataclasses import dataclass, field
from typing import Dict

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
    def __init__(self, nullable: bool = True):
        self._nullable = nullable

    def serialize(self):
        raise NotImplementedError

    def deserialize(self):
        raise NotImplementedError
