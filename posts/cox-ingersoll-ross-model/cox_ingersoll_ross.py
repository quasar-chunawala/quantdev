import math
import numpy as np
import matplotlib.pyplot as plt


class CIRProcess:
    """An engine for generating sample paths of the Cox-Ingersoll-Ross process"""

    def __init__(
        self,
        kappa: float,
        theta: float,
        sigma: float,
        num_paths: int,
        step_size: float,
        total_time: float,
    ):
        self.kappa = kappa
        self.theta = theta
        self.sigma = sigma
        self.num_paths = num_paths
        self.step_size = step_size
        self.total_time = total_time

    def generate_paths(self):
        """Generate sample paths"""
        num_steps = int(self.total_time / self.step_size)
        dz = np.random.standard_normal((self.num_paths, num_steps))
        r_t = np.zeros((self.num_paths, num_steps))
        zero_vector = np.full(self.num_paths, 0.0)
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
    kappa=0.1, theta=0.5, sigma=0.5, num_paths=10, step_size=0.01, total_time=1.0
)

paths = cir_process.generate_paths()
t = np.linspace(0.01, 1.0, 100)

plt.grid(True)
for path in paths:
    plt.plot(t, path)

plt.show()
