import numpy as np

from sivp import SIVP
from euler_maruyama import EulerMaruyama
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

# Let's solve the following SDE
# dS_t = S_t dB_t + (mu + 1/2) S_t dt, S_0 = 1.0
# where mu = 0. This has the known solution S_t = exp(B_t - t/2)

euler = EulerMaruyama(num_paths=10, num_steps=100)

gbm_sde = SIVP(
    t_start=0.0,
    t_end=1.0,
    initial_condition=1.0,
    drift=lambda t, s_t: 0.50 * s_t,
    vol=lambda t, s_t: s_t,
    dvol_dx=lambda t, s_t: np.ones(10),
)

ts, xs = euler.solve(gbm_sde)

plt.xlabel(r"Time $t$")
plt.ylabel(r"$S(t)$")
plt.title(r"10 sample paths of Geometric Brownian Motion, $\mu=0.0$, Euler method")
plt.grid(True)

plt.plot(ts, xs.transpose())

plt.show()
