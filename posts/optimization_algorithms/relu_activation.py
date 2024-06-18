import numpy as np


class ReLUActivation:

    # Forward pass
    def forward(self, inputs):
        # Calculate output values from the inputs
        self.inputs = inputs
        self.output = np.maximum(0, inputs)

    # Backward pass
    def backward(self, dloss_da):
        self.dloss_da = dloss_da
        self.da_dz = np.where(self.inputs > 0.0, 1.0, 0.0)
        self.dloss_dz = self.dloss_da * self.da_dz
