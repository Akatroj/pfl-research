from typing import Optional, Tuple

from pfl.context import CentralContext
from pfl.hyperparam.base import AlgorithmHyperParamsType, ModelHyperParamsType
from pfl.metrics import Metrics
from pfl.model.base import ModelType
from pfl.serverless.base import ServerlessFunction

ContextGetterOutputType = Tuple[
    Optional[Tuple[CentralContext[AlgorithmHyperParamsType, ModelHyperParamsType], ...]], ModelType, Metrics
]


class ContextGetter(ServerlessFunction[None, ContextGetterOutputType]):
    """get_next_central_contexts"""

    def function(self) -> ContextGetterOutputType:
        model, iteration, algorithm_params, model_train_params, model_eval_params = self._store.get_for_context_getter()

        # (new_central_contexts, model, all_metrics) = algorithm.get_next_central_contexts(
        #     model, self._current_central_iteration, algorithm_params, model_train_params, model_eval_params
        # )
