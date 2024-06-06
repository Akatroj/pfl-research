from abc import abstractmethod
from time import sleep
from typing import Generic, TypeVar

from pfl.serverless.stores.base import DataStoreConfig
from pfl.serverless.stores.utils import get_store


def with_simulated_cold_start(f: callable, cold: bool) -> callable:
    if cold:
        sleep(100)
    return f


InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class ServerlessFunction(Generic[InputType, OutputType]):
    def __init__(self, dataStoreConfig: DataStoreConfig):
        self._store = get_store(dataStoreConfig)
        self.__cold = True

    def run_function(self, inputData: InputType) -> OutputType:
        result = with_simulated_cold_start(self.function, self.__cold)(inputData)
        self.__cold = False
        return result

    @abstractmethod
    def function(self, inputData: InputType) -> OutputType:
        pass
