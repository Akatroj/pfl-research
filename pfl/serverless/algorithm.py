import logging
from abc import abstractmethod
from typing import Generic, List, Optional, Tuple, TypedDict, TypeVar

from pfl.aggregate.base import Backend
from pfl.algorithm import algorithm_utils
from pfl.algorithm.base import FederatedAlgorithm
from pfl.callback import TrainingProcessCallback
from pfl.context import CentralContext
from pfl.data.dataset import AbstractDatasetType
from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.internal.platform.selector import get_platform
from pfl.metrics import Metrics
from pfl.model.base import ModelType
from pfl.serverless.context_getter import ContextGetter
from pfl.serverless.stores.simple import SimpleStoreConfig
from pfl.serverless.stores.utils import get_store
from pfl.stats import StatisticsType

logger = logging.getLogger(__name__)


class ServerlessFederatedAlgorithm(
    FederatedAlgorithm[AlgorithmHyperParamsType, ModelHyperParamsType, ModelType, StatisticsType, AbstractDatasetType],
):
    def run(
        self,
        algorithm_params: AlgorithmHyperParamsType,
        backend: Backend,
        model: ModelType,
        model_train_params: ModelHyperParamsType,
        model_eval_params: Optional[ModelHyperParamsType] = None,
        callbacks: Optional[List[TrainingProcessCallback]] = None,
        *,
        send_metrics_to_platform: bool = True,
    ) -> ModelType:
        callbacks, should_stop, on_train_metrics = self._init(model, callbacks)
        xd = 1
        while True:
            print(xd)
            # Step 1
            # Get instructions from algorithm what to run next.
            # Can be multiple queries to cohorts of devices.
            # isntrukcja co ma się dziać
            # Step 1
            # Get instructions from algorithm what to run next.
            # Can be multiple queries to cohorts of devices.
            (new_central_contexts, model, all_metrics) = self.get_next_central_contexts(
                model, self._current_central_iteration, algorithm_params, model_train_params, model_eval_params
            )
            # config = SimpleStoreConfig()
            # store = get_store(config)

            # store.save_data(
            #     **{
            #         "model": model,
            #         "iteration": self._current_central_iteration,
            #         "algorithm_params": algorithm_params,
            #         "model_train_params": model_train_params,
            #         "model_eval_params": model_eval_params,
            #     }
            # )

            # (new_central_contexts, model, all_metrics) = ContextGetter(config).run_function(self)
            if new_central_contexts is None:
                break
            else:
                central_contexts = new_central_contexts

            if self._current_central_iteration == 0:
                all_metrics |= on_train_metrics

            # odpal uczenie u klientów (robi to simulated backend)
            # Step 2
            # Get aggregated model updates and
            # metrics from the requested queries.
            results: List[Tuple[StatisticsType, Metrics]] = algorithm_utils.run_train_eval(
                self, backend, model, central_contexts
            )

            # Step 3
            # For each query result, accumulate metrics and
            # let model handle statistics result if query had any.
            stats_context_pairs = []
            for central_context, (stats, metrics) in zip(central_contexts, results):
                all_metrics |= metrics
                if stats is not None:
                    stats_context_pairs.append((central_context, stats))
            # Process statistics and get new model.

            # wazne: agregacja sie tutaj dzieje.
            (model, update_metrics) = self.process_aggregated_statistics_from_all_contexts(
                tuple(stats_context_pairs), all_metrics, model
            )

            all_metrics |= update_metrics

            # Step 4
            # End-of-iteration callbacks
            for callback in callbacks:
                stop_signal, callback_metrics = callback.after_central_iteration(
                    all_metrics, model, central_iteration=self._current_central_iteration
                )
                all_metrics |= callback_metrics
                should_stop |= stop_signal

            if send_metrics_to_platform:
                get_platform().consume_metrics(all_metrics, iteration=self._current_central_iteration)

            if should_stop:
                break
            self._current_central_iteration += 1

        for callback in callbacks:
            # Calls with central iteration configs used for final round.
            callback.on_train_end(model=model)

        return model

    def process_aggregated_statistics_serverless(self) -> Tuple[ModelType, Metrics]:
        central_context, aggregate_metrics, model, statistics = self._get_data()

        self.process_aggregated_statistics(central_context, aggregate_metrics, model, statistics)

    def _init(self, model, callbacks):
        self._current_central_iteration = 0
        should_stop = False
        callbacks = list(callbacks or [])
        default_callbacks = get_platform().get_default_callbacks()
        for default_callback in default_callbacks:
            # Add default callback if it is not in the provided callbacks
            if all(type(callback) != type(default_callback) for callback in callbacks):
                logger.debug(f"Adding {default_callback}")
                callbacks.append(default_callback)
            else:
                logger.debug(f"Not adding duplicate {default_callback}")

        on_train_metrics = Metrics()
        for callback in callbacks:
            on_train_metrics |= callback.on_train_begin(model=model)

        return callbacks, should_stop, on_train_metrics
