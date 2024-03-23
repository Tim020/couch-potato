from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class ModelCreateContext:
    add_to_registry: bool


MODEL_CREATE_CONTEXT: ContextVar[ModelCreateContext] = ContextVar(
    "model_create_context"
)


@contextmanager
def model_create_context():
    ctx = MODEL_CREATE_CONTEXT.set(ModelCreateContext(add_to_registry=False))
    try:
        yield
    finally:
        MODEL_CREATE_CONTEXT.reset(ctx)
