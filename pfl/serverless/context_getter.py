from typing_extensions import override

from pfl.algorithm.base import FederatedAlgorithm
from pfl.serverless.base import ServerlessFunction
from pfl.serverless.benchmarks import (
    CALL_FN,
    CONTEXT_GETTER,
    GET_INPUT,
    ITERATION,
    SAVE_OUTPUT,
    PFLCounter,
    PFLTimeCounter,
)


class ContextGetter(ServerlessFunction[None, None]):
    """get_next_central_contexts"""

    @override
    def function(self, algorithm: FederatedAlgorithm):
        PFLTimeCounter.start(f"{GET_INPUT}:{CONTEXT_GETTER}:{PFLCounter.get(ITERATION)!s}")
        (
            model,
            iteration,
            algorithm_params,
            model_train_params,
            model_eval_params,
        ) = self._store.get_for_context_getter()
        PFLTimeCounter.stop(f"{GET_INPUT}:{CONTEXT_GETTER}:{PFLCounter.get(ITERATION)!s}")

        PFLTimeCounter.start(f"{CALL_FN}:{CONTEXT_GETTER}:{PFLCounter.get(ITERATION)!s}")
        (new_central_contexts, model, all_metrics) = algorithm.get_next_central_contexts(
            model, iteration, algorithm_params, model_train_params, model_eval_params
        )
        PFLTimeCounter.stop(f"{CALL_FN}:{CONTEXT_GETTER}:{PFLCounter.get(ITERATION)!s}")

        PFLTimeCounter.start(f"{SAVE_OUTPUT}:{CONTEXT_GETTER}:{PFLCounter.get(ITERATION)!s}")
        self._store.save_data(**{"central_contexts": new_central_contexts, "model": model, "all_metrics": all_metrics})
        PFLTimeCounter.stop(f"{SAVE_OUTPUT}:{CONTEXT_GETTER}:{PFLCounter.get(ITERATION)!s}")
