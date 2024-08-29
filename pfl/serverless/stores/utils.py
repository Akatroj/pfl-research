from typing import Optional

from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.model.base import ModelType
from pfl.serverless.stores.base import DataStoreConfig, MetricsType, ServerlessPFLStore
from pfl.serverless.stores.mongo import MongoConfigParams, MongoStore, MongoStoreConfig
from pfl.serverless.stores.redis import RedisConfigParams, RedisStore, RedisStoreConfig
from pfl.serverless.stores.s3 import S3ConfigParams, S3Store, S3StoreConfig
from pfl.serverless.stores.simple import SimpleStore, SimpleStoreConfig
from pfl.stats import StatisticsType


def get_store(
    config: DataStoreConfig,
) -> ServerlessPFLStore[AlgorithmHyperParamsType, ModelHyperParamsType, ModelType, StatisticsType, MetricsType]:
    if config.name == "simple":
        return SimpleStore(config)
    elif config.name == "mongo":
        return MongoStore(config)
    elif config.name == "redis":
        return RedisStore(config)
    elif config.name == "s3":
        return S3Store(config)
    else:
        raise ValueError(f"Unknown data store type: {config['type']}")


def create_config(name: str, **kwargs) -> DataStoreConfig:
    if name == "simple":
        return SimpleStoreConfig()
    elif name == "mongo":
        return MongoStoreConfig(MongoConfigParams(**kwargs))
    elif name == "redis":
        return RedisStoreConfig(RedisConfigParams(**kwargs))
    elif name == "s3":
        return S3StoreConfig(S3ConfigParams(**kwargs))
    else:
        raise ValueError(f"Unknown data store type: {name}")
