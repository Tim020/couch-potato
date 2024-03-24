# Couch Potato

An ODM (Object Document Mapper) for Couchbase in Python. 

Inspired in part by SQLAlchemy.

## Usage

Example usage:

```python
from datetime import datetime

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster

from couch_potato import CouchPotato
from couch_potato.model import KeyGenerator, Model
from couch_potato.fields import DateTime, EmbeddedModel, Integer, String

cluster = Cluster(
    'couchbase://localhost',
    authenticator=PasswordAuthenticator('Administrator', 'password')
)
couch_potato = CouchPotato(cluster)

class SomeModel(Model):
    some_number = Integer()


class UserModel(couch_potato.Model):
    __bucket__ = "test"
    __key_generator__ = KeyGenerator("User::{name}")

    name = String()
    age = Integer()
    created_at = DateTime()
    some_model = EmbeddedModel(SomeModel)


if __name__ == "__main__":
    # Create a new instance of a model
    user = UserModel(
        name="Tim", 
        age=27, 
        created_at=datetime.utcnow(), 
        some_model=SomeModel(some_number=123)
    )
    user.save()
    # Get that instance, update a value, and save ir
    user = UserModel.get(name="Tim")
    user.some_model.foo = 321
    user.save()
```