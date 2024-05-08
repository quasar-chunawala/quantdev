import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
import joypy


class CIRProcess:
    """An engine for generating sample paths of the Cox-Ingersoll-Ross process"""

    def __init__(
        self,
        kappa: float,
        theta: float,
        sigma: float,
        step_size: float,
        total_time: float,
    ):
        self.kappa = kappa
        self.theta = theta
        self.sigma = sigma
        self.step_size = step_size
        self.total_time = total_time

    def generate_paths(self, num_paths):
        """Generate sample paths"""
        num_steps = int(self.total_time / self.step_size)
        dz = np.random.standard_normal((num_paths, num_steps))
        r_t = np.zeros((num_paths, num_steps))
        zero_vector = np.full(num_paths, 0.0)
        prev_r = zero_vector
        for i in range(num_steps):
            r_t[:, i] = (
                prev_r
                + self.kappa * np.subtract(self.theta, prev_r) * self.step_size
                + self.sigma
                * np.sqrt(np.abs(prev_r))
                * math.sqrt(self.step_size)
                * dz[:, i]
            )

            prev_r = r_t[:, i]

        return r_t


cir_process = CIRProcess(
    kappa=0.5, theta=0.5, sigma=1.0, step_size=0.01, total_time=1.0
)

num_paths = 10000
paths = cir_process.generate_paths(num_paths)

# Wrap the paths 2d-array in a dataframe
paths_tr = paths.transpose()
samples = paths_tr[
    4::5
]  # Take 20 samples at times t=0.05, 0.10, 0.15, ..., 1.0 along each path
samples_arr = samples.reshape(num_paths * 20)  # Reshape in a 1d column-vector
samples_df = pd.DataFrame(samples_arr, columns=["values"])
samples_df["time"] = [
    "t=" + str((int(i / num_paths) + 1) / 20) for i in range(num_paths * 20)
]

fig, ax = joypy.joyplot(
    samples_df,
    by="time",
    column="values",
    grid="y",
    range_style="own",
    kind="kde",
    tails=0.00002,
    colormap=cm.autumn_r,
)

plt.show()
