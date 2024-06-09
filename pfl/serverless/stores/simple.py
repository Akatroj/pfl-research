import pickle
from dataclasses import dataclass

from typing_extensions import override

from pfl.serverless.stores.base import DataStoreConfig, EmptyConfigParams, ServerlessPFLStore


@dataclass
class SimpleStoreConfig(DataStoreConfig):
    name = "simple"
    params = EmptyConfigParams()

    def __init__(self) -> None:
        super().__init__(self.name, self.params)


_store_data = {}


class SimpleStore(ServerlessPFLStore):
    def __init__(self, config: SimpleStoreConfig) -> None:
        super().__init__(config)

    @override
    def get_data_for_key(self, key):
        return pickle.loads(_store_data[key])

    @override
    def save_data_for_key(self, key, data) -> None:
        _store_data[key] = pickle.dumps(data)


print(SimpleStoreConfig())
