from dataclasses import dataclass

import redis
from typing_extensions import override

from pfl.serverless.stores.base import ConfigParams, DataStoreConfig, ServerlessPFLStore


@dataclass
class RedisConfigParams(ConfigParams):
    uri: str


@dataclass
class RedisStoreConfig(DataStoreConfig):
    name = "redis"
    params: RedisConfigParams

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.name, *args, **kwargs)


class RedisStore(ServerlessPFLStore):
    def __init__(self, config: RedisStoreConfig) -> None:
        super().__init__(config)
        self._client = redis.Redis.from_url(config.params.uri)

    @override
    def _get_data_for_key(self, key):
        return self._client.get(key)

    @override
    def _save_data_for_key(self, key, data) -> None:
        self._client.set(key, data)
