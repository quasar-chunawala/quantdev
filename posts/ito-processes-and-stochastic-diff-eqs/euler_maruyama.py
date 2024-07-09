import numpy as np
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class EulerMaruyama:
    """
    Numerical solver for a stochastic differential equation(SDE) using
    the Euler-Maruyama method.

    Consider an SDE of the form :

    dX_t = mu(t,X_t) dt + sigma(t,X_t) dB_t

    with initial condition X_0 = x_0

    The solution to the SDE can be computed using the increments

    X_{n+1} - X_n = mu(n,X_n)(t_{n+1}-t_n) + sigma(n,X_n)(B(n+1)-B(n))

    """

    drift: Callable
    volatility: Callable
    init_value: float
    t_start: float
    t_end: float
    step_size: float
    num_paths: int

    def __post_init__(self):
        self.iter = 0
        self.x_curr = np.full(shape=(self.num_paths,), fill_value=self.init_value)
        self.num_steps = int((self.t_end - self.t_start) / self.step_size)
        self.times = np.linspace(self.t_start, self.t_end, self.num_steps + 1)
        self.delta_brownian = np.sqrt(self.step_size) * np.random.standard_normal(
            size=(self.num_paths, self.num_steps)
        )
        self.brownian = np.cumsum(self.delta_brownian, axis=1)
        self.brownian = np.concatenate(
            [np.zeros(shape=(self.num_paths, 1)), self.brownian], axis=1
        )
        self.solution = [self.x_curr.copy()]

    def iterate(self):
        """
        Generate the next iterate X(n+1)
        """

        mu_n = np.array([self.drift(self.times[self.iter], x) for x in self.x_curr])
        sigma_n = np.array(
            [self.volatility(self.times[self.iter], x) for x in self.x_curr]
        )

        d_brownian = self.brownian[:, self.iter + 1] - self.brownian[:, self.iter]

        self.x_curr += (
            mu_n * (self.times[self.iter + 1] - self.times[self.iter])
            + sigma_n * d_brownian
        )

        return self.x_curr.copy()

    def solve(self):
        while self.iter < self.num_steps:
            self.solution.append(self.iterate())
            self.iter += 1

        return np.array(self.solution).transpose()
