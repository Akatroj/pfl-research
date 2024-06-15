from typing_extensions import override

from pfl.algorithm.base import FederatedAlgorithm
from pfl.serverless.base import ServerlessFunction


class ContextGetter(ServerlessFunction[None, None]):
    """get_next_central_contexts"""

    @override
    def function(self, algorithm: FederatedAlgorithm):
        model, iteration, algorithm_params, model_train_params, model_eval_params = self._store.get_for_context_getter()

        (new_central_contexts, model, all_metrics) = algorithm.get_next_central_contexts(
            model, iteration, algorithm_params, model_train_params, model_eval_params
        )

        self._store.save_data(**{"central_contexts": new_central_contexts, "model": model, "all_metrics": all_metrics})
