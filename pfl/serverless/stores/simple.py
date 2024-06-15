from dataclasses import dataclass

import dill
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
        print(f"unpickling {key}")
        print()
        result = dill.loads(_store_data[key])
        print(f"done unpickling {key}")
        return result

    @override
    def save_data_for_key(self, key, data) -> None:
        print(f"pickling {key}")
        _store_data[key] = dill.dumps(data)
        print(f"done pickling {key}")


print(SimpleStoreConfig())
