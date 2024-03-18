from datetime import timedelta
from typing import Dict

from couchbase.cluster import Cluster
from couchbase.collection import Collection

from _types import BucketBind
from _model import BaseModel, make_meta_model


class CouchPotato:
    __model__: BaseModel = None

    def __init__(self, cluster: Cluster):
        self._cluster = cluster
        self._models = []
        self._binds: Dict[str, BucketBind] = {}
        self._model_binds: Dict[BaseModel, Collection] = {}

        # After init, wait until the cluster is ready
        self._cluster.wait_until_ready(timeout=timedelta(seconds=5))

    @property
    def Model(self) -> BaseModel:
        if self.__model__ is None:
            class _Model(BaseModel, metaclass=make_meta_model(self)):
                @classmethod
                def bind(cls):
                    return self

            self.__model__ = _Model
        return self.__model__
