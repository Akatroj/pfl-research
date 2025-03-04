from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Optional, Tuple, TypeVar

import dill

from pfl.aggregate.base import Backend
from pfl.algorithm.base import FederatedAlgorithm
from pfl.context import CentralContext
from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.metrics import Metrics
from pfl.model.base import ModelType
from pfl.serverless.benchmarks import PFLCounter, PFLSizeCounter
from pfl.stats import StatisticsType


@dataclass
class ConfigParams:
    pass


@dataclass
class DataStoreConfig:
    name: str
    params: ConfigParams


class ServerlessDataStore:
    def __init__(self, config: DataStoreConfig) -> None:
        self.config = config

    @abstractmethod
    def _get_data_for_key(self, key):
        """Get the data saved for a specific key"""

    @abstractmethod
    def _save_data_for_key(self, key, data) -> None:
        """Save the data for a specific key"""

    def get_data_for_key(self, key):
        # print(f"unpickling {key}")
        pickled_data = self._get_data_for_key(key)
        slug = f"READ:{key}"
        PFLSizeCounter.record_size(f"{slug}:{PFLCounter.get_and_increment(slug)}", pickled_data)
        # print(f"done unpickling {key}")
        return dill.loads(pickled_data)

    def save_data_for_key(self, key, data) -> None:
        # print(f"pickling {key}")
        pickled_data = dill.dumps(data)
        slug = f"WRITE:{key}"
        PFLSizeCounter.record_size(f"{slug}:{PFLCounter.get_and_increment(slug)}", pickled_data)
        # print(f"done pickling {key}")
        return self._save_data_for_key(key, pickled_data)

    def save_data(self, **kwargs):
        for key, data in kwargs.items():
            self.save_data_for_key(key, data)

    def get_data_for_keys(self, keys):
        return [self.get_data_for_key(key) for key in keys]


MetricsType = TypeVar("MetricsType", bound=Metrics)


class ServerlessPFLStore(
    ServerlessDataStore, Generic[AlgorithmHyperParamsType, ModelHyperParamsType, ModelType, StatisticsType, MetricsType]
):
    def get_for_context_getter(
        self,
    ) -> Tuple[ModelType, int, AlgorithmHyperParamsType, ModelHyperParamsType, Optional[ModelHyperParamsType]]:
        keys = ["model", "iteration", "algorithm_params", "model_train_params", "model_eval_params"]
        return self.get_data_for_keys(keys)

    def get_from_context_getter(
        self,
    ) -> Tuple[
        Optional[Tuple[CentralContext[AlgorithmHyperParamsType, ModelHyperParamsType], ...]], ModelType, Metrics
    ]:
        keys = ["central_contexts", "model", "all_metrics"]
        return self.get_data_for_keys(keys)

    def get_for_clients(self):
        keys = [
            "num_users_trained",
            "num_total_datapoints",
            "total_weight",
            "user_metrics",
            "server_statistics",
            "user_dataset",
            "local_seed",
            "central_context",
            "model",
        ]
        return self.get_data_for_keys(keys)

    def get_from_clients(self) -> List[Tuple[StatisticsType, Metrics]]:
        keys = [
            "num_users_trained",
            "num_total_datapoints",
            "total_weight",
            "user_metrics",
            "server_statistics",
        ]
        return self.get_data_for_keys(keys)

    def get_for_aggregation(
        self,
    ) -> Tuple[
        Tuple[Tuple[CentralContext[AlgorithmHyperParamsType, ModelHyperParamsType], StatisticsType], ...],
        Metrics,
        ModelType,
        StatisticsType,
    ]:
        keys = ["stats_context_pairs", "all_metrics", "model"]
        return self.get_data_for_keys(keys)

    def get_from_aggregation(self) -> Tuple[ModelType, Metrics]:
        keys = ["model", "all_metrics"]
        return self.get_data_for_keys(keys)
