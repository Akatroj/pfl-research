import pickle

from typing_extensions import override

from pfl.serverless.stores.base import DataStoreConfig, EmptyConfigParams, ServerlessPFLStore


class SimpleStoreConfig(DataStoreConfig):
    name = "simple"
    params = EmptyConfigParams()


class SimpleStore(ServerlessPFLStore):
    def __init__(self, config: SimpleStoreConfig) -> None:
        super().__init__(config)
        self._data = {}

    @override
    def get_data_for_key(self, key):
        return pickle.loads(self._data[key])

    @override
    def save_data_for_key(self, key, data) -> None:
        self._data[key] = pickle.dumps(data)
