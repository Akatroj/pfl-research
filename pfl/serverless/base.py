from abc import abstractmethod
from time import sleep
from typing import Generic, TypeVar

from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.model.base import ModelType
from pfl.serverless.stores.base import DataStoreConfig, MetricsType, ServerlessPFLStore
from pfl.serverless.stores.utils import get_store
from pfl.stats import StatisticsType

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")

COLD_START_DURATION_MS = 300
WARM_START_DURATION_MS = 50


class ServerlessFunction(Generic[InputType, OutputType]):
    _store: ServerlessPFLStore[AlgorithmHyperParamsType, ModelHyperParamsType, ModelType, StatisticsType, MetricsType]

    def __init__(self, dataStoreConfig: DataStoreConfig):
        self._store = get_store(dataStoreConfig)
        self.__cold = True

    def run_function(self, *args, **kwargs) -> OutputType:
        return self._with_simulated_startup(self.function, *args, **kwargs)

    @abstractmethod
    def function(self, *args, **kwargs) -> OutputType:
        pass

    def _with_simulated_startup(self, fn: callable, *args, **kwargs):
        # if self.__cold:
        #     sleep(COLD_START_DURATION_MS)
        #     self.__cold = False
        # else:
        #     sleep(WARM_START_DURATION_MS)
        return fn(*args, **kwargs)
