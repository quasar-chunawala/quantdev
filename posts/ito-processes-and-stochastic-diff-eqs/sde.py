from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class SDE:
    """
    An abstraction for a stochastic differential equation
    """

    initial_condition: float
    drift: Callable[[float, float], float]
    vol: Callable[[float, float], float]
    dvol_dx: Optional[Callable[[float, float], float]]
