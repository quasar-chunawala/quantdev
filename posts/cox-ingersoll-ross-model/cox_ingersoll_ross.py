import math
from dataclasses import dataclass

import joypy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from tqdm import tqdm


@dataclass
class CIRProcess:
    """An engine for generating sample paths of the Cox-Ingersoll-Ross process"""

    kappa: float
    theta: float
    sigma: float
    step_size: float
    total_time: float
    r_0: float

    def generate_paths(self, paths: int):
        """Generate sample paths"""
        num_steps = int(self.total_time / self.step_size)
        dz = np.random.standard_normal((paths, num_steps))
        r_t = np.zeros((paths, num_steps))
        zero_vector = np.full(paths, self.r_0)
        prev_r = zero_vector
        for i in tqdm(range(num_steps)):
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


if __name__ == "__main__":
    cir_process = CIRProcess(
        kappa=3,
        r_0=9,
        sigma=0.5,
        step_size=10e-3,
        theta=3,
        total_time=1.0,
    )

    num_paths = 100_000
    print(
        f"Generating {num_paths} sample paths "
        f"for the Cox-Ingersoll-Ross process\n{cir_process=}"
    )

    paths = cir_process.generate_paths(num_paths)

    # TODO: [bwrob] - this is where slowness lies, generating paths is a brezze

    # Wrap the paths 2d-array in a dataframe
    paths_tr = paths.transpose()
    # Take 20 samples at times t=0.05, 0.10, 0.15, ..., 1.0 along each path
    samples = paths_tr[4::5]
    # Reshape in a 1d column-vector
    samples_arr = samples.reshape(num_paths * 20)
    samples_df = pd.DataFrame(samples_arr, columns=["values"])
    samples_df["time"] = [
        "t=" + str((int(i / num_paths) + 1) / 20) for i in range(num_paths * 20)
    ]

    # TODO: end

    fig, ax = joypy.joyplot(
        samples_df,
        by="time",
        colormap=cm.autumn_r,
        column="values",
        grid="y",
        kind="kde",
        range_style="own",
        tails=10e-3,
    )
    plt.vlines(
        [cir_process.theta, cir_process.r_0],
        -0.2,
        1,
        color="k",
        linestyles="dashed",
    )
    plt.show()
