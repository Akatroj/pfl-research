from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.model.base import ModelType
from pfl.serverless.stores.base import DataStoreConfig, MetricsType, ServerlessPFLStore
from pfl.serverless.stores.mongo import MongoStore
from pfl.serverless.stores.simple import SimpleStore
from pfl.serverless.stores.type_utils import PFLGenericType
from pfl.stats import StatisticsType


def get_store(
    config: DataStoreConfig,
) -> ServerlessPFLStore[AlgorithmHyperParamsType, ModelHyperParamsType, ModelType, StatisticsType, MetricsType]:
    if config["name"] == "simple":
        return SimpleStore(config)
    elif config["name"] == "mongo":
        return MongoStore(config)
    else:
        raise ValueError(f"Unknown data store type: {config['type']}")
