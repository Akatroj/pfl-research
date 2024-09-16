from dataclasses import dataclass

import gridfs
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
    DB_NAME = "pfl_data"

    def __init__(self, config: MongoStoreConfig) -> None:
        super().__init__(config)
        self._client = pymongo.MongoClient(config.params.uri)
        self._db = self._client[MongoStore.DB_NAME]
        self._fs = gridfs.GridFS(self._db)

    @override
    def _get_data_for_key(self, key):
        return self._fs.get_last_version(key).read()

    @override
    def _save_data_for_key(self, key, data) -> None:
        existing_file = self._fs.find_one({"filename": key})
        if existing_file:
            self._fs.delete(file_id=existing_file._id)
        self._fs.put(data, filename=key)
