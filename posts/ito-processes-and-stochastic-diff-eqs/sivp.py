import numpy as np
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class SIVP:
    """
    An abstraction for a stochastic initial value problem
    """

    t_start: float
    t_end: float
    initial_condition: float

    drift: Callable[[float, np.ndarray], np.ndarray]
    vol: Callable[[float, np.ndarray], np.ndarray]
    dvol_dx: Optional[Callable[[float, np.ndarray], np.ndarray]] = None
