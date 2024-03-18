from typing import TYPE_CHECKING, Dict, Any

from couchbase.collection import Collection
from couchbase.scope import Scope

from _types import BucketBind, ScopeBind, Field
from errors import FieldNotFound, ModelAttributeError

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
            bucket_name = getattr(new_class, "__bucket__")
            scope_name = getattr(new_class, "__scope__")
            collection_name = getattr(new_class, "__collection__")
            # 1. Ensure that the model class has a bucket attribute defined
            if not getattr(new_class, "__bucket__", None):
                raise TypeError(f"Model class {name} must have a __bucket__ attribute")
            
            # Set up internal attributes on the class defn
            # 1. Set the __fields__ attribute on the class
            fields: Dict[str, Field] = dict()
            for name, attr in dct.items():
                if isinstance(attr, Field):
                    fields[name] = attr
            setattr(new_class, "__fields__", fields)

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
    __bucket__: str
    __scope__: str = Scope.default_name()
    __collection__: str = Collection.default_name()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ModelAttributeError(f"Model {self.__name__} does not contain field {key}")

            # Ensure the type of the field is correct when setting it
            field = self.__fields__[key]
            field.ensure_type(value)
            setattr(self, key, value)

    @classmethod
    def bind(cls) -> "Collection":
        raise NotImplementedError("Bind should not be called directly from BaseModel")

    @classmethod
    def get(cls, key) -> Any:
        if not hasattr(cls, "__fields__"):
            raise Exception("Unable to use model to fetch, as no fields defined")

        # Get the document from the database
        collection: Collection = cls.bind()
        doc = collection.get(key)
        content = doc.content_as[dict]

        # Deserialize the data into the correct Python values
        cls_dict = {}
        for _key, field in cls.__fields__.items():
            if _key not in content:
                raise FieldNotFound(f"Field {_key} not found within document {key}")
            cls_dict[_key] = field.deserialize(content[_key])

        # Construct the model instance, and set some internal fields
        new_class = cls.from_json(**cls_dict)
        setattr(new_class, "__raw__", content)
        setattr(new_class, "__cas__", doc.cas)
        setattr(new_class, "__key__", doc.key)

        # Return the new model instance
        return new_class

    @classmethod
    def from_json(cls, **kwargs) -> "BaseModel":
        # Create an instance of the class
        instance = cls(**kwargs)
        return instance
