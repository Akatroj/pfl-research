import os
import sys

# Both Jupyter and `pfl` uses async, nest_asyncio allows `pfl` to run inside the notebook
import nest_asyncio
import numpy as np
import tensorflow as tf

# HAS TO BE IN THIS ORDER
from pfl.aggregate.simulate import SimulatedBackend
from pfl.data.tensorflow import TFDataDataset, TFFederatedDataset
from pfl.data.user_state import InMemoryUserStateStorage
from pfl.model.tensorflow import TFModel  # noqa: W291
from tensorflow.keras.optimizers import SGD
from model.tf2.cnn import resnet18, simple_cnn


import pfl.algorithm.serverless as serverless
from pfl.algorithm import FederatedAveraging, NNAlgorithmParams
from pfl.callback import CentralEvaluationCallback
from pfl.data.dataset import Dataset
from pfl.data.federated_dataset import ArtificialFederatedDataset
from pfl.data.sampling import get_data_sampler
from pfl.hyperparam import NNEvalHyperParams, NNTrainHyperParams
from pfl.serverless.backend.simulate import SimulatedServerlessBackend
from pfl.serverless.stores.utils import create_config

nest_asyncio.apply()


# append the root directory to your paths to be able to reach the examples.
from dataset.cifar10 import load_and_preprocess

print("TensorFlow version: {}".format(tf.__version__))
tf.random.set_seed(7)
np.random.seed(7)


def prepare_dataset():
    # exclude_classes = [1, 3, 4, 5, 6, 7, 8, 9]
    exclude_classes = []
    train_images, train_labels, channel_means, channel_stddevs = load_and_preprocess(
        "../benchmarks/data/cifar10/cifar10_train.p", exclude_classes=exclude_classes
    )

    val_images, val_labels, _, _ = load_and_preprocess(
        "../benchmarks/data/cifar10/cifar10_test.p", channel_means, channel_stddevs, exclude_classes=exclude_classes
    )

    # Convert labels to one-hot vectors.
    one_hots = np.eye(10)
    train_labels = one_hots[train_labels].squeeze()
    val_labels = one_hots[val_labels].squeeze()

    train_data_sampler = get_data_sampler("random", len(train_images))
    val_data_sampler = get_data_sampler("random", len(val_images))

    def user_dataset_len_sampler():
        while True:
            length = np.random.poisson(5)
            if length > 0:
                return length

    train_federated_dataset = ArtificialFederatedDataset.from_slices(
        [train_images, train_labels], train_data_sampler, user_dataset_len_sampler
    )

    val_federated_dataset = ArtificialFederatedDataset.from_slices(
        [val_images, val_labels], val_data_sampler, user_dataset_len_sampler
    )
    central_data = Dataset(raw_data=[val_images, val_labels])

    return train_federated_dataset, val_federated_dataset, central_data


train_federated_dataset, val_federated_dataset, central_data = prepare_dataset()
print("Datasets prepared.")

# keras_model = tf.keras.models.load_model("keras_model.h5")
# keras_model = simple_cnn((32, 32, 3), 10)
# keras_model = resnet18((32, 32, 3), 10)
# keras_model.compile(SGD(0.01), loss="categorical_crossentropy")
# # keras_model.save("simple_cnn.h5")
# keras_model.save("resnet18.h5")
keras_model = tf.keras.models.load_model("resnet18.h5")
# keras_model = tf.keras.models.load_model("./tutorials/keras_model.h5")

metrics = {"accuracy": tf.keras.metrics.CategoricalAccuracy(), "loss": tf.keras.metrics.CategoricalCrossentropy()}
model = TFModel(model=keras_model, central_optimizer=tf.keras.optimizers.SGD(1.0), metrics=metrics)

cohort_size = 20
central_num_iterations = 5
population = 1e7

# Use Gaussian Moments Accountant, and transform it to a central privacy mechanism.
# accountant = PLDPrivacyAccountant(
#     num_compositions=central_num_iterations,
#     sampling_probability=cohort_size / population,
#     mechanism="gaussian",
#     epsilon=2,
#     delta=1e-5,
# )
# central_privacy = CentrallyAppliedPrivacyMechanism(
#     GaussianMechanism.from_privacy_accountant(accountant=accountant, clipping_bound=1.0)
# )

# Instantiate simulated federated averaging
# simulated_backend = SimulatedBackend(
#     training_data=train_federated_dataset, val_data=val_federated_dataset, postprocessors=[central_privacy]
# )

# config = create_config("redis", uri="redis://localhost:6379/0")
# config = create_config("mongo", uri="mongodb://localhost:27017")
# config = create_config(
#     "s3",
#     bucket_name="pfl-bucket-agh",
#     aws_access_key_id="",
#     aws_secret_access_key="",  # noqa: S106
#     aws_session_token="",  # noqa: S106
#     region_name="us-east-1",
# )
# config = create_config("simple")

simulated_backend = SimulatedBackend(
    training_data=train_federated_dataset, val_data=val_federated_dataset, postprocessors=[]
)
# simulated_backend = SimulatedServerlessBackend(
#     config=config, training_data=train_federated_dataset, val_data=val_federated_dataset, postprocessors=[]
# )


os.environ["PFL_GRAPH_CACHE"] = "false"

model_train_params = NNTrainHyperParams(local_learning_rate=0.05, local_num_epochs=5, local_batch_size=5)

# Do full-batch evaluation to run faster.
model_eval_params = NNEvalHyperParams(local_batch_size=None)


callbacks = [CentralEvaluationCallback(central_data, model_eval_params, 4)]

algorithm = FederatedAveraging()
algorithm_params = NNAlgorithmParams(
    central_num_iterations=central_num_iterations,
    evaluation_frequency=4,
    train_cohort_size=cohort_size,
    val_cohort_size=10,
)
# algorithm = serverless.ServerlessFedProx()
# algorithm = serverless.ServerlessSCAFFOLD()
# algorithm_params = serverless.SCAFFOLDParams(
#     central_num_iterations=central_num_iterations,
#     evaluation_frequency=4,
#     train_cohort_size=cohort_size,
#     val_cohort_size=10,
#     population=1e6,
#     use_gradient_as_control_variate=False,
#     user_state_storage=InMemoryUserStateStorage(),
# )


print("Running federated learning...")
algorithm.run(
    backend=simulated_backend,
    model=model,
    algorithm_params=algorithm_params,
    model_train_params=model_train_params,
    model_eval_params=model_eval_params,
    callbacks=callbacks,
)
