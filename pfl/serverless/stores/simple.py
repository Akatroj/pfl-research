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
    def _get_data_for_key(self, key):
        return _store_data[key]

    @override
    def _save_data_for_key(self, key, data) -> None:
        _store_data[key] = data


print(SimpleStoreConfig())
