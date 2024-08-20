from dataclasses import dataclass
from typing import ClassVar, Dict

from typing_extensions import override

from pfl.serverless.stores.base import ConfigParams, DataStoreConfig, ServerlessPFLStore


@dataclass
class EmptyConfigParams(ConfigParams):
    pass


@dataclass
class SimpleStoreConfig(DataStoreConfig):
    name = "simple"
    params = EmptyConfigParams()

    def __init__(self) -> None:
        super().__init__(self.name, self.params)


class SimpleStore(ServerlessPFLStore):
    _store_data: ClassVar[Dict[str, bytes]] = {}

    def __init__(self, config: SimpleStoreConfig) -> None:
        super().__init__(config)

    @override
    def _get_data_for_key(self, key):
        return SimpleStore._store_data[key]

    @override
    def _save_data_for_key(self, key, data) -> None:
        SimpleStore._store_data[key] = data
