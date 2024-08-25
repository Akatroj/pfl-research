from typing_extensions import override

from pfl.algorithm.base import FederatedAlgorithm
from pfl.serverless.base import ServerlessFunction
from pfl.serverless.benchmarks import AGGREGATOR, CALL_FN, GET_INPUT, ITERATION, SAVE_OUTPUT, PFLCounter, PFLTimeCounter


class Aggregator(ServerlessFunction[None, None]):
    """process_aggregated_statistics_from_all_contexts"""

    @override
    def function(self, algorithm: FederatedAlgorithm):
        PFLTimeCounter.start(f"{GET_INPUT}:{AGGREGATOR}:{PFLCounter.get(ITERATION)!s}")
        stats_context_pairs, all_metrics, model = self._store.get_for_aggregation()
        PFLTimeCounter.stop(f"{GET_INPUT}:{AGGREGATOR}:{PFLCounter.get(ITERATION)!s}")

        PFLTimeCounter.start(f"{CALL_FN}:{AGGREGATOR}:{PFLCounter.get(ITERATION)!s}")
        (model, update_metrics) = algorithm.process_aggregated_statistics_from_all_contexts(
            tuple(stats_context_pairs), all_metrics, model
        )
        all_metrics |= update_metrics
        PFLTimeCounter.stop(f"{CALL_FN}:{AGGREGATOR}:{PFLCounter.get(ITERATION)!s}")

        PFLTimeCounter.start(f"{SAVE_OUTPUT}:{AGGREGATOR}:{PFLCounter.get(ITERATION)!s}")
        self._store.save_data(**{"model": model, "all_metrics": all_metrics})
        PFLTimeCounter.stop(f"{SAVE_OUTPUT}:{AGGREGATOR}:{PFLCounter.get(ITERATION)!s}")
