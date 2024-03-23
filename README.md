# Couch Potato

An ODM (Object Document Mapper) for Couchbase in Python. 

Inspired in part by SQLAlchemy.

## Usage

Example usage:

```python
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster

from couch_potato import CouchPotato
from couch_potato.model import KeyGenerator
from couch_potato.fields import String, Integer

cluster = Cluster(
    'couchbase://localhost',
    authenticator=PasswordAuthenticator('Administrator', 'password')
)
couch_potato = CouchPotato(cluster)

class UserModel(couch_potato.Model):
    __bucket__ = "test"
    __key_generator__ = KeyGenerator("User::{name}")

    name = String()
    age = Integer()

if __name__ == "__main__":
    # Get the model from the database
    a: UserModel = UserModel.get(name="test")
    print(a.name, a.age)
    # Update one of the instance attributes, and save the model
    a.age = 30
    a.save()

```