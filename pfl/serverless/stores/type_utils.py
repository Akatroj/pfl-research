from typing import Generic, TypeVar

from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.metrics import Metrics
from pfl.model.base import ModelType
from pfl.stats import StatisticsType

MetricsType = TypeVar("MetricsType", bound=Metrics)

PFLGenericType = Generic[AlgorithmHyperParamsType, ModelHyperParamsType, ModelType, StatisticsType, MetricsType]
