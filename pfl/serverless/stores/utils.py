from pfl.serverless.stores.base import DataStoreConfig, ServerlessPFLStore
from pfl.serverless.stores.mongo import MongoStore
from pfl.serverless.stores.simple import SimpleStore
from pfl.serverless.stores.type_utils import PFLGenericType


def get_store(config: DataStoreConfig) -> ServerlessPFLStore[PFLGenericType]:
    if config["name"] == "simple":
        return SimpleStore(config)
    elif config["name"] == "mongo":
        return MongoStore(config)
    else:
        raise ValueError(f"Unknown data store type: {config['type']}")
