from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, List, NamedTuple, Optional, Tuple, TypeVar

from pfl.aggregate.base import Backend
from pfl.algorithm.base import FederatedAlgorithm
from pfl.context import CentralContext
from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.metrics import Metrics
from pfl.model.base import ModelType
from pfl.stats import StatisticsType


@dataclass
class ConfigParams:
    pass


@dataclass
class EmptyConfigParams(ConfigParams):
    pass


@dataclass
class DataStoreConfig:
    name: str
    params: ConfigParams


class ServerlessDataStore:
    def __init__(self, config: DataStoreConfig) -> None:
        self.config = config

    @abstractmethod
    def get_data_for_key(self, key):
        """Get the data saved for a specific key"""

    @abstractmethod
    def save_data_for_key(self, key, data) -> None:
        """Save the data for a specific key"""

    def save_data(self, **kwargs):
        for key, data in kwargs.items():
            self.save_data_for_key(key, data)

    def _get_data_for_keys(self, keys):
        return [self.get_data_for_key(key) for key in keys]


MetricsType = TypeVar("MetricsType", bound=Metrics)


class ServerlessPFLStore(
    ServerlessDataStore, Generic[AlgorithmHyperParamsType, ModelHyperParamsType, ModelType, StatisticsType, MetricsType]
):
    def get_for_context_getter(
        self,
    ) -> Tuple[ModelType, int, AlgorithmHyperParamsType, ModelHyperParamsType, Optional[ModelHyperParamsType]]:
        keys = ["model", "iteration", "algorithm_params", "model_train_params", "model_eval_params"]
        return self._get_data_for_keys(keys)

    def get_from_context_getter(
        self,
    ) -> Tuple[
        Optional[Tuple[CentralContext[AlgorithmHyperParamsType, ModelHyperParamsType], ...]], ModelType, Metrics
    ]:
        keys = ["central_contexts", "model", "all_metrics"]
        return self._get_data_for_keys(keys)

    def get_for_clients(self) -> Tuple[FederatedAlgorithm, Backend, ModelType, Tuple[CentralContext, ...]]:
        keys = ["algorithm", "backend", "model", "central_contexts"]
        return self._get_data_for_keys(keys)

    def get_from_clients(self) -> List[Tuple[StatisticsType, Metrics]]:
        pass

    def get_for_aggregation(
        self,
    ) -> Tuple[
        Tuple[Tuple[CentralContext[AlgorithmHyperParamsType, ModelHyperParamsType], StatisticsType], ...],
        Metrics,
        ModelType,
        StatisticsType,
    ]:
        keys = ["stats_context_pairs", "aggregate_metrics", "model"]
        return self._get_data_for_keys(keys)

    def get_from_aggregation(self) -> Tuple[ModelType, Metrics]:
        keys = ["model", "update_metrics"]
        return self._get_data_for_keys(keys)
