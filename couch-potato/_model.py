from typing import TYPE_CHECKING

from couchbase.collection import Collection
from couchbase.scope import Scope

from _types import BucketBind, ScopeBind

if TYPE_CHECKING:
    from couch_potato import CouchPotato


def make_meta_model(cp: "CouchPotato"):
    class MetaModel(type):
        def __new__(cls, name, bases, dct):
            new_class = super().__new__(cls, name, bases, dct)

            # BaseModel instantiation
            if len(bases) == 0:
                return new_class
            if len(bases) == 1 and bases[0] is BaseModel:
                return new_class

            # Append the model class to the list of models associated
            # with the CouchPotato instance
            cp._models.append(new_class)

            # Check validity of the model class
            bucket_name = getattr(new_class, "_bucket")
            scope_name = getattr(new_class, "_scope")
            collection_name = getattr(new_class, "_collection")
            # 1. Ensure that the model class has a bucket attribute defined
            if not getattr(new_class, "_bucket", None):
                raise TypeError(f"Model class {name} must have a _bucket attribute")

            # Set up the binds on the CouchPotato instance
            if bucket_name in cp._binds:
                bucket_bind = cp._binds[bucket_name]
            else:
                bucket = cp._cluster.bucket(bucket_name)
                bucket_bind = BucketBind(bucket=bucket)
                cp._binds[bucket.name] = bucket_bind

            if scope_name in bucket_bind.scope_binds:
                scope_bind = bucket_bind.scope_binds[scope_name]
            else:
                scope = bucket_bind.bucket.scope(scope_name)
                scope_bind = ScopeBind(scope=scope)
                bucket_bind.scope_binds[scope_name] = scope_bind

            if collection_name not in scope_bind.collection_binds:
                collection = scope_bind.scope.collection(collection_name)
                scope_bind.collection_binds[collection_name] = collection
            else:
                collection = scope_bind.collection_binds[collection_name]

            cp._model_binds[new_class] = collection

            return new_class
    return MetaModel


class BaseModel:
    _bucket: str
    _scope: str = Scope.default_name()
    _collection: str = Collection.default_name()

    @classmethod
    def bind(cls):
        raise NotImplementedError("Bind should not be called directly from BaseModel")
