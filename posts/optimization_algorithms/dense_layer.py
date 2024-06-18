import numpy as np


class DenseLayer:
    def __init__(self, n_inputs, n_neurons):
        self.width = n_neurons
        # Weight vectors per neuron
        self.weights = 0.01 * np.random.randn(n_neurons, n_inputs)
        self.biases = np.zeros((1, n_neurons))

    def forward(self, inputs):
        self.inputs = inputs
        self.output = np.dot(inputs, self.weights.T) + self.biases

    def backward(self, dloss_dz):
        self.dloss_dz = dloss_dz
        self.dz_dweights = self.inputs
        self.dz_dbiases = np.ones_like(self.inputs)
        self.dz_dinputs = self.weights
        self.dloss_dweights = np.dot(self.inputs.T, self.dloss_dz)
        self.dloss_dbiases = np.sum(self.dloss_dz, axis=0, keepdims=True)
        self.dloss_dinputs = np.dot(self.dloss_dz, self.dz_dinputs)
