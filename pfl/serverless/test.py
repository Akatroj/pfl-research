import json
import logging
import os
from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Optional, Tuple, TypeVar

import numpy as np

from pfl.aggregate.base import Backend
from pfl.algorithm.base import NNAlgorithmParamsType
from pfl.callback import TrainingProcessCallback
from pfl.common_types import Population, Saveable
from pfl.context import CentralContext
from pfl.data.dataset import AbstractDatasetType
from pfl.exception import CheckpointNotFoundError
from pfl.hyperparam.base import (
    AlgorithmHyperParams,
    AlgorithmHyperParamsType,
    HyperParamClsOrInt,
    ModelHyperParamsType,
    get_param_value,
)
from pfl.internal.platform.selector import get_platform
from pfl.metrics import Metrics, TrainMetricName
from pfl.model.base import ModelType, StatefulModelType
from pfl.serverless.algorithm import ServerlessFederatedAlgorithm
from pfl.stats import StatisticsType


logger = logging.getLogger(__name__)


class ServerlessFederatedNNAlgorithm(
    ServerlessFederatedAlgorithm[
        NNAlgorithmParamsType, ModelHyperParamsType, StatefulModelType, StatisticsType, AbstractDatasetType
    ]
):
    def __init__(self):
        super().__init__()
        # Just a placeholder of tensors to get_parameters faster.
        self._initial_model_state = None

    @abstractmethod
    def train_one_user(
        self,
        initial_model_state: StatisticsType,
        model: StatefulModelType,
        user_dataset: AbstractDatasetType,
        central_context: CentralContext[NNAlgorithmParamsType, ModelHyperParamsType],
    ) -> Tuple[StatisticsType, Metrics]:
        pass

    def get_next_central_contexts(
        self,
        model: StatefulModelType,
        iteration: int,
        algorithm_params: NNAlgorithmParamsType,
        model_train_params: ModelHyperParamsType,
        model_eval_params: Optional[ModelHyperParamsType] = None,
    ) -> Tuple[
        Optional[Tuple[CentralContext[NNAlgorithmParamsType, ModelHyperParamsType], ...]], StatefulModelType, Metrics
    ]:
        if iteration == 0:
            self._initial_model_state = None

        # Stop condition for iterative NN federated algorithms.
        if iteration == algorithm_params.central_num_iterations:
            return None, model, Metrics()

        do_evaluation = iteration % algorithm_params.evaluation_frequency == 0
        static_model_train_params: ModelHyperParamsType = model_train_params.static_clone()
        static_model_eval_params: Optional[ModelHyperParamsType]
        static_model_eval_params = None if model_eval_params is None else model_eval_params.static_clone()

        configs: List[CentralContext[NNAlgorithmParamsType, ModelHyperParamsType]] = [
            CentralContext(
                current_central_iteration=iteration,
                do_evaluation=do_evaluation,
                cohort_size=get_param_value(algorithm_params.train_cohort_size),
                population=Population.TRAIN,
                model_train_params=static_model_train_params,
                model_eval_params=static_model_eval_params,
                algorithm_params=algorithm_params.static_clone(),
                seed=self._get_seed(),
            )
        ]
        if do_evaluation and algorithm_params.val_cohort_size:
            configs.append(
                CentralContext(
                    current_central_iteration=iteration,
                    do_evaluation=do_evaluation,
                    cohort_size=algorithm_params.val_cohort_size,
                    population=Population.VAL,
                    model_train_params=static_model_train_params,
                    model_eval_params=static_model_eval_params,
                    algorithm_params=algorithm_params.static_clone(),
                    seed=self._get_seed(),
                )
            )

        return tuple(configs), model, Metrics()

    def simulate_one_user(
        self,
        model: StatefulModelType,
        user_dataset: AbstractDatasetType,
        central_context: CentralContext[NNAlgorithmParamsType, ModelHyperParamsType],
    ) -> Tuple[Optional[StatisticsType], Metrics]:
        """
        If population is ``Population.TRAIN``, trains one user and returns the
        model difference before and after training.
        Also evaluates the performance before and after training the user.
        Metrics with the postfix "after local training" measure the performance
        after training the user.
        If population is not ``Population.TRAIN``, does only evaluation.
        """
        # pytype: disable=duplicate-keyword-argument
        initial_metrics_format_fn = lambda n: TrainMetricName(n, central_context.population, after_training=False)
        final_metrics_format_fn = lambda n: TrainMetricName(n, central_context.population, after_training=True)
        # pytype: enable=duplicate-keyword-argument

        metrics = Metrics()
        # Train local user.

        if central_context.population == Population.TRAIN:
            if central_context.do_evaluation:
                metrics |= model.evaluate(user_dataset, initial_metrics_format_fn, central_context.model_eval_params)

            self._initial_model_state = model.get_parameters(self._initial_model_state)
            statistics, train_metrics = self.train_one_user(
                self._initial_model_state, model, user_dataset, central_context
            )
            metrics |= train_metrics

            # Evaluate after local training.
            if central_context.do_evaluation:
                metrics |= model.evaluate(user_dataset, final_metrics_format_fn, central_context.model_eval_params)

            model.set_parameters(self._initial_model_state)
            return statistics, metrics
        else:
            metrics = model.evaluate(user_dataset, initial_metrics_format_fn, central_context.model_eval_params)
            return None, metrics
