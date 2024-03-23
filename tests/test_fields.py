from datetime import datetime
from typing import Type, Any

import pytest

from src.couch_potato._types import Field
from src.couch_potato.fields import Float, String, Integer, Boolean, DateTime


@pytest.mark.parametrize(
    "field_class, value, expected_result",
    [
        pytest.param(Integer, 1, 1, id="Integer"),
        pytest.param(Float, 1.0, 1.0, id="Float"),
        pytest.param(String, "foobar", "foobar", id="String"),
        pytest.param(Boolean, True, True, id="Boolean"),
        pytest.param(
            DateTime,
            datetime(2024, 3, 23, 0, 0, 0),
            "2024-03-23T00:00:00",
            id="DateTime",
        ),
    ],
)
def test_field_serialize(field_class: Type[Field], value: Any, expected_result: Any):
    field = field_class()
    serialized_value = field.serialize(value)
    assert serialized_value == expected_result


@pytest.mark.parametrize(
    "field_class, value, expected_result",
    [
        pytest.param(Integer, 1, 1, id="Integer"),
        pytest.param(Float, 1.0, 1.0, id="Float"),
        pytest.param(String, "foobar", "foobar", id="String"),
        pytest.param(Boolean, True, True, id="Boolean"),
        pytest.param(
            DateTime,
            "2024-03-23T00:00:00",
            datetime(2024, 3, 23, 0, 0, 0),
            id="DateTime",
        ),
    ],
)
def test_field_deserialize(field_class: Type[Field], value: Any, expected_result: Any):
    field = field_class()
    serialized_value = field.deserialize(value)
    assert serialized_value == expected_result
