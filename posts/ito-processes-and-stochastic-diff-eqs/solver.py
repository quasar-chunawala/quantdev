from dataclasses import dataclass
from abc import ABC, abstractmethod
from sivp import SIVP
import numpy as np

# More descriptive type hints
T = np.ndarray
X = np.ndarray


@dataclass
class Solver(ABC):
    """
    An abstract base class for all numerical schemes
    """

    num_steps: int = 100
    num_paths: int = 100

    def __post_init__(self):
        self.iter = 0

        # x_values is a matrix of shape [num_paths,num_steps]
        self.x_values = np.zeros((self.num_paths, self.num_steps + 1))
        self.step_size = 1.0 / self.num_steps

        # gaussian increments
        self.brownian_increments = np.sqrt(self.step_size) * np.random.standard_normal(
            size=(self.num_paths, self.num_steps)
        )
        self.brownian = np.cumsum(self.brownian_increments, axis=1)
        self.brownian = np.concatenate(
            [np.zeros(shape=(self.num_paths, 1)), self.brownian], axis=1
        )

    @abstractmethod
    def iterate(self, sivp: SIVP) -> X:
        """
        Compute the next iterate X(n+1)
        """

    def solve(self, sivp: SIVP) -> (T, X):
        """
        Solve the SIVP
        """
        self.x_values[:, 0] = np.full(
            shape=(self.num_paths,), fill_value=sivp.initial_condition
        )
        while self.iter < self.num_steps:
            self.x_values[:, self.iter + 1] = self.iterate(sivp)
            self.iter += 1

        times = np.linspace(sivp.t_start, sivp.t_end, self.num_steps + 1)
        return times, self.x_values

    def reset(self):
        self.__post_init__()
