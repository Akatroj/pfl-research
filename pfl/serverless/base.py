import functools
from abc import abstractmethod
from time import sleep
from typing import Generic, TypeVar

from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.model.base import ModelType
from pfl.serverless.stores.base import DataStoreConfig, MetricsType, ServerlessPFLStore
from pfl.serverless.stores.utils import get_store
from pfl.stats import StatisticsType


class Serverless:
    func: callable
    instance: object
    cold_attribute = "__cold"

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __get__(self, obj, objtype):
        self.instance = obj
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        # if getattr(self.instance, Serverless.cold_attribute, True):
        #     sleep(0.1)
        # setattr(self.instance, Serverless.cold_attribute, False)
        return self.func(*args, **kwargs)


InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class ServerlessFunction(Generic[InputType, OutputType]):
    _store: ServerlessPFLStore[AlgorithmHyperParamsType, ModelHyperParamsType, ModelType, StatisticsType, MetricsType]

    def __init__(self, dataStoreConfig: DataStoreConfig):
        self._store = get_store(dataStoreConfig)

    @Serverless
    def run_function(self, inputData: InputType) -> OutputType:
        return self.function(inputData)

    @abstractmethod
    def function(self, inputData: InputType) -> OutputType:
        pass
