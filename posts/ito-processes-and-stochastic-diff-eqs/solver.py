from dataclasses import dataclass
from abc import ABC, abstractmethod
from sde import SDE
import numpy as np


@dataclass
class Solver(ABC):
    """
    An abstract base class for all numerical schemes
    """

    t_start: float = 0.0
    t_end: float = 1.0
    step_size: float = 0.01
    num_paths: int = 100

    def __post_init__(self):
        self.iter = 0
        self.x_curr = np.zeros((self.num_paths,))
        self.num_steps = int((self.t_end - self.t_start) / self.step_size)
        self.times = np.linspace(self.t_start, self.t_end, self.num_steps + 1)
        self.brownian_increments = np.sqrt(self.step_size) * np.random.standard_normal(
            size=(self.num_paths, self.num_steps)
        )
        self.brownian = np.cumsum(self.brownian_increments, axis=1)
        self.brownian = np.concatenate(
            [np.zeros(shape=(self.num_paths, 1)), self.brownian], axis=1
        )
        self.solution = []

    @abstractmethod
    def iterate(self, sde: SDE):
        """
        Compute the next iterate X(n+1)
        """

    def solve(self, sde: SDE):
        """
        Solve the SDE
        """
        self.x_curr = np.full(shape=(self.num_paths,), fill_value=sde.initial_condition)
        self.solution = [self.x_curr.copy()]

        while self.iter < self.num_steps:
            self.solution.append(self.iterate(sde))
            self.iter += 1

        return np.array(self.solution).transpose()

    def reset(self):
        self.__post_init__()
