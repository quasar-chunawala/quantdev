"""
A module for Milstein discretization algorithm.
"""

from typing import Callable
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Milstein:
    """
    Numerical solver for a stochastic differential equation(SDE) using
    the Euler-Maruyama method.

    Consider an SDE of the form :

    dX_t = mu(t,X_t) dt + sigma(t,X_t) dB_t

    with initial condition X_0 = x_0

    The solution to the SDE can be computed using the increments

    X_{n+1} - X_n = mu(n,X_n)(t_{n+1}-t_n) + sigma(n,X_n)(B(n+1)-B(n))
    + 0.5 * sigma(n,X_n) * sigma'(n,X_n) * ((B(n+1) - B(n))**2 - (t_{n+1} - t_n))

    """

    drift: Callable
    vol: Callable
    dvol_dx: Callable
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
        sigma_n = np.array([self.vol(self.times[self.iter], x) for x in self.x_curr])
        dvol_dx_n = np.array(
            [self.dvol_dx(self.times[self.iter], x) for x in self.x_curr]
        )

        d_brownian = self.brownian[:, self.iter + 1] - self.brownian[:, self.iter]

        self.x_curr += (
            mu_n * self.step_size
            + sigma_n * d_brownian
            + 0.5 * sigma_n * dvol_dx_n * (d_brownian**2 - self.step_size)
        )

        return self.x_curr.copy()

    def solve(self):
        while self.iter < self.num_steps:
            self.solution.append(self.iterate())
            self.iter += 1

        return np.array(self.solution).transpose()
