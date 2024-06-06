from pfl.serverless.stores.base import ConfigParams, DataStoreConfig, ServerlessPFLStore


class MongoConfigParams(ConfigParams):
    uri: str


class MongoStoreConfig(DataStoreConfig):
    name = "mongo"
    params: MongoConfigParams


class MongoStore(ServerlessPFLStore):
    def __init__(self, config: MongoStoreConfig) -> None:
        super().__init__(config)
        # self._client = pymongo.MongoClient(config.uri)
        # self._db = self._client.get_default_database()

    def get_data_for_key(self, key):
        return self._db.data.find_one({"key": key})["data"]

    def save_data_for_key(self, key, data) -> None:
        self._db.data.update_one({"key": key}, {"$set": {"data": data}}, upsert=True)
