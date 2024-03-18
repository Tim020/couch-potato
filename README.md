# Couch Potato

An ODM (Object Document Mapper) for Couchbase in Python. 

Inspired in part by SQLAlchemy.

## Usage

Example usage:

```python
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster

from couch_potato.couch_potato import CouchPotato
from couch_potato.fields import String

cluster = Cluster(
    'couchbase://localhost',
    authenticator=PasswordAuthenticator('Administrator', 'password')
)
couch_potato = CouchPotato(cluster)

class UserModel(couch_potato.Model):
    __bucket__ = "test"

    name = String()

if __name__ == "__main__":
    a: UserModel = UserModel.get("test")
    print(a.name)
```