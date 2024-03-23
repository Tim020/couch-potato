from datetime import timedelta
from typing import Dict, List, Type

from couchbase.cluster import Cluster
from couchbase.collection import Collection

from src.couch_potato._context import model_create_context
from src.couch_potato._model import BoundModel, make_meta_model
from src.couch_potato._types import BucketBind


class CouchPotato:
    __model__: Type[BoundModel] = None

    def __init__(self, cluster: Cluster, **kwargs):
        self._cluster: Cluster = cluster
        self._models: List[BoundModel] = []
        self._binds: Dict[str, BucketBind] = {}
        self._model_binds: Dict[BoundModel, Collection] = {}

        # After init, wait until the cluster is ready
        init_timeout = kwargs.get("init_timeout", 5)
        self._cluster.wait_until_ready(timeout=timedelta(seconds=init_timeout))

    @property
    def Model(self) -> Type[BoundModel]:
        if self.__model__ is None:
            with model_create_context():

                class _Model(BoundModel, metaclass=make_meta_model(self)):
                    @classmethod
                    def bind(cls) -> Collection:
                        return self.model_binds[cls]

            self.__model__ = _Model
        return self.__model__

    @property
    def cluster(self) -> Cluster:
        return self._cluster

    @property
    def models(self) -> List[BoundModel]:
        return self._models

    @property
    def binds(self) -> Dict[str, BucketBind]:
        return self._binds

    @property
    def model_binds(self) -> Dict[BoundModel, Collection]:
        return self._model_binds
