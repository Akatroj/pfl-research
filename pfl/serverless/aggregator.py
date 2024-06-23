from typing_extensions import override

from pfl.algorithm.base import FederatedAlgorithm
from pfl.serverless.base import ServerlessFunction


class Aggregator(ServerlessFunction[None, None]):
    """process_aggregated_statistics_from_all_contexts"""

    @override
    def function(self, algorithm: FederatedAlgorithm):
        stats_context_pairs, all_metrics, model = self._store.get_for_aggregation()

        (model, update_metrics) = algorithm.process_aggregated_statistics_from_all_contexts(
            tuple(stats_context_pairs), all_metrics, model
        )

        all_metrics |= update_metrics

        self._store.save_data(**{"model": model, "all_metrics": all_metrics})
