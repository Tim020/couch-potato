from datetime import datetime

from src.couch_potato.fields import DateTime, Integer, String
from src.couch_potato.model import Model


class DummyModel(Model):
    name = String()
    age = Integer()
    created_at = DateTime()


def dummy_model():
    return DummyModel(name="Tim", age=27, created_at=datetime(2024, 3, 24, 0, 4, 0))


def dummy_json():
    return {"name": "Tim", "age": 27, "created_at": "2024-03-24T00:04:00"}
