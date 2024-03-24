from datetime import datetime
from typing import Any, Type

import pytest

from src.couch_potato._types import Field
from src.couch_potato.fields import (
    Boolean,
    DateTime,
    EmbeddedModel,
    Float,
    Integer,
    String,
    TypedArray,
)
from tests.conftest import DummyModel, dummy_json, dummy_model


@pytest.mark.parametrize(
    "field, value, expected_result",
    [
        pytest.param(Integer(), 1, 1, id="Integer"),
        pytest.param(Float(), 1.0, 1.0, id="Float"),
        pytest.param(String(), "foobar", "foobar", id="String"),
        pytest.param(Boolean(), True, True, id="Boolean"),
        pytest.param(
            DateTime(),
            datetime(2024, 3, 23, 0, 0, 0),
            "2024-03-23T00:00:00",
            id="DateTime",
        ),
        pytest.param(
            EmbeddedModel(DummyModel), dummy_model(), dummy_json(), id="EmbeddedModel"
        ),
        pytest.param(
            TypedArray(Integer()), [1, 2, 3], [1, 2, 3], id="TypedArray[Integer]"
        ),
        pytest.param(
            TypedArray(Float()),
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
            id="TypedArray[Float]",
        ),
        pytest.param(
            TypedArray(String()),
            ["foo", "bar"],
            ["foo", "bar"],
            id="TypedArray[String]",
        ),
        pytest.param(
            TypedArray(Boolean()),
            [True, False],
            [True, False],
            id="TypedArray[Boolean]",
        ),
        pytest.param(
            TypedArray(DateTime()),
            [datetime(2024, 3, 23, 0, 0, 0), datetime(2024, 3, 23, 1, 0, 0)],
            ["2024-03-23T00:00:00", "2024-03-23T01:00:00"],
            id="TypedArray[Boolean]",
        ),
        pytest.param(
            TypedArray(EmbeddedModel(DummyModel)),
            [dummy_model()],
            [dummy_json()],
            id="TypedArray[EmbeddedModel]",
        ),
    ],
)
def test_field_serialize(field: Field, value: Any, expected_result: Any):
    serialized_value = field.serialize(value)
    assert serialized_value == expected_result


@pytest.mark.parametrize(
    "field, value, expected_result",
    [
        pytest.param(Integer(), 1, 1, id="Integer"),
        pytest.param(Float(), 1.0, 1.0, id="Float"),
        pytest.param(String(), "foobar", "foobar", id="String"),
        pytest.param(Boolean(), True, True, id="Boolean"),
        pytest.param(
            DateTime(),
            "2024-03-23T00:00:00",
            datetime(2024, 3, 23, 0, 0, 0),
            id="DateTime",
        ),
        pytest.param(
            EmbeddedModel(DummyModel), dummy_json(), dummy_model(), id="EmbeddedModel"
        ),
        pytest.param(
            TypedArray(Integer()), [1, 2, 3], [1, 2, 3], id="TypedArray[Integer]"
        ),
        pytest.param(
            TypedArray(Float()),
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
            id="TypedArray[Float]",
        ),
        pytest.param(
            TypedArray(String()),
            ["foo", "bar"],
            ["foo", "bar"],
            id="TypedArray[String]",
        ),
        pytest.param(
            TypedArray(Boolean()),
            [True, False],
            [True, False],
            id="TypedArray[Boolean]",
        ),
        pytest.param(
            TypedArray(DateTime()),
            ["2024-03-23T00:00:00", "2024-03-23T01:00:00"],
            [datetime(2024, 3, 23, 0, 0, 0), datetime(2024, 3, 23, 1, 0, 0)],
            id="TypedArray[Boolean]",
        ),
        pytest.param(
            TypedArray(EmbeddedModel(DummyModel)),
            [dummy_json()],
            [dummy_model()],
            id="TypedArray[EmbeddedModel]",
        ),
    ],
)
def test_field_deserialize(field: Field, value: Any, expected_result: Any):
    serialized_value = field.deserialize(value)
    assert serialized_value == expected_result
