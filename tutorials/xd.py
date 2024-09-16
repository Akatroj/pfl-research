from matplotlib import pyplot as plt
import numpy as np


def user_dataset_len_sampler():
    while True:
        length = np.random.poisson(500)
        if length > 0:
            return length


# Visualize sampling from this function.
plt.xlabel("Number of datapoints for one user")
plt.title("Distribution of user dataset length")
plt.hist([user_dataset_len_sampler() for _ in range(100_000)])
plt.yticks([])
plt.savefig("/mnt/c/Users/Pawel/Coding/STUDIA/magisterus/fedless_new/pfl-research/tutorials/cifar.png")
# plt.show()
