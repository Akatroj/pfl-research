import pickle

from pfl.serverless.stores.base import DataStoreConfig, ServerlessPFLStore


class SimpleStoreConfig(DataStoreConfig):
    name = "simple"
    params = {}  # noqa: RUF012


class SimpleStore(ServerlessPFLStore):
    def __init__(self, config: SimpleStoreConfig) -> None:
        super().__init__(config)
        self._data = {}

    def get_data_for_key(self, key):
        return pickle.loads(self._data[key])

    def save_data_for_key(self, key, data) -> None:
        self._data[key] = pickle.dumps(data)
