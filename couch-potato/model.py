from string import Formatter
from typing import Any

from couchbase.collection import Collection
from couchbase.scope import Scope

from errors import ModelAttributeError, FieldNotFound


class KeyGenerator:
    def __init__(self, format_str: str):
        self.format_str = format_str

    def generate(self, **kwargs):
        return self.format_str.format(**kwargs)

    @property
    def format_keys(self):
        return [i[1] for i in Formatter().parse(self.format_str) if i[1] is not None]


class BaseModel:
    __bucket__: str
    __scope__: str = Scope.default_name()
    __collection__: str = Collection.default_name()
    __key_generator__: KeyGenerator

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
    def get(cls, **kwargs) -> Any:
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

    @classmethod
    def from_json(cls, **kwargs) -> "BaseModel":
        # Create an instance of the class
        instance = cls(**kwargs)
        return instance
