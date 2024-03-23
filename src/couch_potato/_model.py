from typing import TYPE_CHECKING, Dict

from src.couch_potato._types import BucketBind, ScopeBind, Field
from src.couch_potato.model import BaseModel, KeyGenerator

if TYPE_CHECKING:
    from src.couch_potato.couch_potato import CouchPotato


def make_meta_model(cp: "CouchPotato"):
    class MetaModel(type):
        def __new__(cls, name, bases, dct):
            new_class = super().__new__(cls, name, bases, dct)

            # BaseModel instantiation
            if len(bases) == 0:
                return new_class
            if len(bases) == 1 and bases[0] is BaseModel:
                return new_class

            # Set up internal attributes on the class defn
            # 1. Set the __fields__ attribute on the class
            # TODO: Validate that field names do not conflict with reserved named
            fields: Dict[str, Field] = dict()
            for name, attr in dct.items():
                if isinstance(attr, Field):
                    fields[name] = attr
            setattr(new_class, "__fields__", fields)

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

    return MetaModel
