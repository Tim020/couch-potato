from datetime import timedelta
from typing import Dict, List, Type

from couchbase.cluster import Cluster
from couchbase.collection import Collection

from _types import BucketBind
from _model import make_meta_model
from model import BaseModel


class CouchPotato:
    __model__: Type[BaseModel] = None

    def __init__(self, cluster: Cluster, **kwargs):
        self._cluster: Cluster = cluster
        self._models: List[BaseModel] = []
        self._binds: Dict[str, BucketBind] = {}
        self._model_binds: Dict[BaseModel, Collection] = {}

        # After init, wait until the cluster is ready
        init_timeout = kwargs.get('init_timeout', 5)
        self._cluster.wait_until_ready(timeout=timedelta(seconds=init_timeout))

    @property
    def Model(self) -> Type[BaseModel]:
        if self.__model__ is None:
            class _Model(BaseModel, metaclass=make_meta_model(self)):
                @classmethod
                def bind(cls) -> Collection:
                    return self.model_binds[cls]

            self.__model__ = _Model
        return self.__model__

    @property
    def cluster(self) -> Cluster:
        return self._cluster

    @property
    def models(self) -> List[BaseModel]:
        return self._models

    @property
    def binds(self) -> Dict[str, BucketBind]:
        return self._binds

    @property
    def model_binds(self) -> Dict[BaseModel, Collection]:
        return self._model_binds
