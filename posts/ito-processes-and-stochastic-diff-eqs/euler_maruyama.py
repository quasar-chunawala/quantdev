from dataclasses import dataclass
import numpy as np
from sivp import SIVP
from solver import Solver

# More descriptive type hints
T = np.ndarray
X = np.ndarray


@dataclass
class EulerMaruyama(Solver):
    """
    Numerical solver for a stochastic differential equation(SDE) using
    the Euler-Maruyama method.

    Consider an SDE of the form :

    dX_t = mu(t,X_t) dt + sigma(t,X_t) dB_t

    with initial condition X_0 = x_0

    The solution to the SDE can be computed using the increments

    X_{n+1} - X_n = mu(n,X_n)(t_{n+1}-t_n) + sigma(n,X_n)(B(n+1)-B(n))

    """

    def iterate(self, sivp: SIVP) -> X:
        """
        Generate the next iterate X(n+1)
        """
        current_time = self.iter * self.step_size
        mu_n = sivp.drift(current_time, self.x_values[:, self.iter])
        sigma_n = sivp.vol(current_time, self.x_values[:, self.iter])
        delta_x = (
            mu_n * self.step_size + sigma_n * self.brownian_increments[:, self.iter]
        )
        return self.x_values[:, self.iter] + delta_x
