from typing import TYPE_CHECKING, Dict, Type, TypeVar

from couchbase.collection import Collection
from couchbase.options import InsertOptions, ReplaceOptions
from couchbase.scope import Scope

from src.couch_potato._context import MODEL_CREATE_CONTEXT
from src.couch_potato._types import BucketBind, Field, ScopeBind
from src.couch_potato.errors import FieldNotFound, ModelAttributeError, ReadOnlyError

if TYPE_CHECKING:
    from src.couch_potato import CouchPotato
    from src.couch_potato.model import KeyGenerator

T = TypeVar("T", bound="BaseModel")


class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)

        # Set up internal attributes on the class defn
        # 1. Set the __fields__ attribute on the class
        # TODO: Validate that field names do not conflict with reserved named
        fields: Dict[str, Field] = dict()
        for name, attr in dct.items():
            if isinstance(attr, Field):
                fields[name] = attr
        setattr(new_class, "__fields__", fields)

        return new_class


def make_meta_model(cp: "CouchPotato"):
    from src.couch_potato.model import KeyGenerator

    class BoundModelMeta(ModelMeta):
        def __new__(cls, name, bases, dct):
            new_class = super().__new__(cls, name, bases, dct)

            # BaseModel instantiation
            try:
                ctx = MODEL_CREATE_CONTEXT.get()
            except LookupError:
                pass
            else:
                if not ctx.add_to_registry:
                    return new_class

            # Check validity of the model class
            # 1. Ensure that the model class has a bucket attribute defined
            if not getattr(new_class, "__bucket__", None):
                raise TypeError(f"Model class {name} must have a __bucket__ attribute")

            # 2. Ensure that the model class has a key generator
            if not getattr(new_class, "__key_generator__", None):
                raise TypeError(
                    f"Model class {name} must have a __key_generator__ attribute"
                )
            if not isinstance(getattr(new_class, "__key_generator__"), KeyGenerator):
                raise TypeError(
                    f"Model class {name} __key_generator__ is not a KeyGenerator instance"
                )

            # 3. Ensure that the key generator is made up of valid format parts
            key_generator: KeyGenerator = getattr(new_class, "__key_generator__")
            fields: Dict[str, Field] = getattr(new_class, "__fields__")
            missing_keys = set()
            for format_key in key_generator.format_keys:
                if format_key not in fields:
                    missing_keys.add(format_key)
            if missing_keys:
                raise TypeError(
                    f"Model class {name}'s KeyGenerator contains keys without "
                    f"corresponding fields: {list(missing_keys)}"
                )

            # Set up the binds on the CouchPotato instance
            # 1. Bucket bind
            bucket_name = getattr(new_class, "__bucket__")
            if bucket_name in cp._binds:
                bucket_bind = cp._binds[bucket_name]
            else:
                bucket = cp._cluster.bucket(bucket_name)
                bucket_bind = BucketBind(bucket=bucket)
                cp._binds[bucket.name] = bucket_bind
            # 2. Scope bind
            scope_name = getattr(new_class, "__scope__")
            if scope_name in bucket_bind.scope_binds:
                scope_bind = bucket_bind.scope_binds[scope_name]
            else:
                scope = bucket_bind.bucket.scope(scope_name)
                scope_bind = ScopeBind(scope=scope)
                bucket_bind.scope_binds[scope_name] = scope_bind
            # 3. Collection bind
            collection_name = getattr(new_class, "__collection__")
            if collection_name not in scope_bind.collection_binds:
                collection = scope_bind.scope.collection(collection_name)
                scope_bind.collection_binds[collection_name] = collection
            else:
                collection = scope_bind.collection_binds[collection_name]
            cp._model_binds[new_class] = collection

            # Append the model class to the list of models associated
            # with the CouchPotato instance
            cp._models.append(new_class)

            # Finally, return the new model class
            return new_class

    return BoundModelMeta


class BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ModelAttributeError(
                    f"Model {self.__name__} does not contain field {key}"
                )

            # Ensure the type of the field is correct when setting it
            field = self.__fields__[key]
            field.ensure_type(value)
            setattr(self, key, value)

    @classmethod
    def from_json(cls: Type[T], **kwargs) -> T:
        # Create an instance of the class
        instance = cls(**kwargs)
        return instance

    def to_json(self) -> dict:
        ret = {}
        for key, field in self.__fields__.items():
            ret[key] = field.serialize(getattr(self, key))
        return ret


class BoundModel(BaseModel):
    __bucket__: str
    __scope__: str = Scope.default_name()
    __collection__: str = Collection.default_name()
    __key_generator__: "KeyGenerator"
    __read_only__: bool = False

    @classmethod
    def bind(cls: Type[T]) -> "Collection":
        raise NotImplementedError("Bind should not be called directly from BaseModel")

    @classmethod
    def get(cls: Type[T], **kwargs) -> T:
        if not hasattr(cls, "__fields__"):
            raise Exception("Unable to use model to fetch, as no fields defined")

        # Validate the kwargs we have passed in match the expected ones from the key generator
        kwarg_keys = set(kwargs.keys())
        key_gen_keys = set(cls.__key_generator__.format_keys)
        added_keys = kwarg_keys - key_gen_keys
        if added_keys:
            raise KeyError(f"Unexpected kwargs: {list(added_keys)}")
        missing_keys = key_gen_keys - kwarg_keys
        if missing_keys:
            raise KeyError(f"Expected kwargs: {list(missing_keys)}")

        key = cls.__key_generator__.generate(**kwargs)

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

    # TODO: Add kwargs for supporting InsertOptions and ReplaceOptions,
    #  such as timeout and expiry
    def save(self):
        # TODO: Move this logic inside of a __setattr__, so that any attempt to
        #  modify fields on the model is rejected and cannot actually modify state
        if self.__read_only__:
            raise ReadOnlyError("Cannot save read-only model")

        if not hasattr(self, "__fields__"):
            raise Exception("Unable to save model, as no fields defined")

        serialized = self.to_json()
        doc_key = self.__key_generator__.generate(
            **{key: getattr(self, key) for key in self.__key_generator__.format_keys}
        )

        if hasattr(self, "__cas__"):
            # Updating the document
            # Update the raw dictionary with the values of the fields
            # defined in the model, but leave everything else which not
            # a defined field as it was
            raw_doc = getattr(self, "__raw__", {})
            for key, value in serialized.items():
                raw_doc[key] = value
            serialized = raw_doc
            options = ReplaceOptions(cas=self.__cas__)
            # TODO: What happens if the key for this document changes?
            mutation_result = self.bind().replace(doc_key, serialized, options)
        else:
            # Inserting the document
            options = InsertOptions()
            mutation_result = self.bind().insert(doc_key, serialized, options)
        # Set the class attributes updated to the values in the mutation result, so that this
        # instance can then be reused without needing to fetch again
        setattr(self, "__raw__", serialized)
        setattr(self, "__cas__", mutation_result.cas)
        setattr(self, "__key__", mutation_result.key)
