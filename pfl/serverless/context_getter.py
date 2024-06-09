from typing_extensions import override

from pfl.serverless.base import ServerlessFunction


class ContextGetter(ServerlessFunction[None, None]):
    """get_next_central_contexts"""

    @override
    def function(self):
        model, iteration, algorithm_params, model_train_params, model_eval_params = self._store.get_for_context_getter()

        (new_central_contexts, model, all_metrics) = algorithm.get_next_central_contexts(
            model, self._current_central_iteration, algorithm_params, model_train_params, model_eval_params
        )

        self._store.save_data_for_key(
            **{"new_central_contexts": new_central_contexts, "model": model, "all_metrics": all_metrics}
        )
