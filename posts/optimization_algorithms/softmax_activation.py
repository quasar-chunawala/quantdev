import numpy as np


class SoftmaxActivation:

    # Forward pass
    def forward(self, inputs):
        self.inputs = inputs
        exp_values = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
        probabilities = exp_values / np.sum(exp_values, axis=1, keepdims=True)
        self.output = probabilities

    # Backward pass
    def backward(self, dloss_da):
        dloss_dz = []
        n = len(self.output)
        for i in range(n):
            softmax_output = self.output[i]

            # Reshape as a column vector
            softmax_output = softmax_output.reshape(-1, 1)

            dsoftmax_dz = np.diagflat(softmax_output) - np.dot(
                softmax_output, softmax_output.T
            )
            dloss_dz.append(np.dot(dloss_da[i], dsoftmax_dz))

        self.dloss_dz = np.array(dloss_dz)
