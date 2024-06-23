from dataclasses import dataclass

import pymongo
from typing_extensions import override

from pfl.serverless.stores.base import ConfigParams, DataStoreConfig, ServerlessPFLStore


@dataclass
class MongoConfigParams(ConfigParams):
    uri: str


@dataclass
class MongoStoreConfig(DataStoreConfig):
    name = "mongo"
    params: MongoConfigParams

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.name, *args, **kwargs)


class MongoStore(ServerlessPFLStore):
    def __init__(self, config: MongoStoreConfig) -> None:
        super().__init__(config)
        self._client = pymongo.MongoClient(config.params.uri)
        self._db = self._client["pfl_data"]

    @override
    def _get_data_for_key(self, key):
        return self._db.data.find_one({"key": key})["data"]

    @override
    def _save_data_for_key(self, key, data) -> None:
        self._db.data.update_one({"key": key}, {"$set": {"data": data}}, upsert=True)
