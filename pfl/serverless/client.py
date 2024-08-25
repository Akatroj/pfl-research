from typing import TYPE_CHECKING

from typing_extensions import override

from pfl.aggregate.base import Backend
from pfl.algorithm.base import FederatedAlgorithm
from pfl.serverless.base import ServerlessFunction
from pfl.serverless.benchmarks import (
    CALL_FN,
    CLIENT_HANDLER,
    CLIENTS,
    GET_INPUT,
    ITERATION,
    SAVE_OUTPUT,
    PFLCounter,
    PFLTimeCounter,
)

if TYPE_CHECKING:
    from pfl.serverless.backend.simulate import SimulatedServerlessBackend


class ClientHandler(ServerlessFunction[None, None]):
    """simulate_one_user"""

    @override
    def function(self, algorithm: FederatedAlgorithm, backend: "SimulatedServerlessBackend"):
        PFLTimeCounter.start(f"{GET_INPUT}:{CLIENT_HANDLER}:{PFLCounter.get(ITERATION)!s}:{PFLCounter.get(CLIENTS)!s}")
        (
            num_users_trained,
            num_total_datapoints,
            total_weight,
            user_metrics,
            server_statistics,
            user_dataset,
            local_seed,
            central_context,
            model,
        ) = self._store.get_for_clients()
        PFLTimeCounter.stop(f"{GET_INPUT}:{CLIENT_HANDLER}:{PFLCounter.get(ITERATION)!s}:{PFLCounter.get(CLIENTS)!s}")

        PFLTimeCounter.start(f"{CALL_FN}:{CLIENT_HANDLER}:{PFLCounter.get(ITERATION)!s}:{PFLCounter.get(CLIENTS)!s}")
        user_statistics, metrics_one_user = algorithm.simulate_one_user(model, user_dataset, central_context)

        total_weight, server_statistics, user_metrics = backend.get_user_metrics(
            num_users_trained,
            num_total_datapoints,
            total_weight,
            user_metrics,
            server_statistics,
            user_dataset,
            local_seed,
            user_statistics,
            metrics_one_user,
        )
        PFLTimeCounter.stop(f"{CALL_FN}:{CLIENT_HANDLER}:{PFLCounter.get(ITERATION)!s}:{PFLCounter.get(CLIENTS)!s}")

        PFLTimeCounter.start(
            f"{SAVE_OUTPUT}:{CLIENT_HANDLER}:{PFLCounter.get(ITERATION)!s}:{PFLCounter.get(CLIENTS)!s}"
        )
        self._store.save_data(
            **{
                "num_users_trained": num_users_trained,
                "num_total_datapoints": num_total_datapoints,
                "total_weight": total_weight,
                "user_metrics": user_metrics,
                "server_statistics": server_statistics,
            }
        )
        PFLTimeCounter.stop(f"{SAVE_OUTPUT}:{CLIENT_HANDLER}:{PFLCounter.get(ITERATION)!s}:{PFLCounter.get(CLIENTS)!s}")
