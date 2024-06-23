import numpy as np


class SGDOptimizer:

    # Initial optimizer - set settings
    # learning rate of 1. is default for this optimizer
    def __init__(self, learning_rate=1.0, decay=0.0, momentum=0.0):
        self.learning_rate = learning_rate
        self.current_learning_rate = learning_rate
        self.decay = decay
        self.iterations = 0
        self.beta = momentum

    # Call once before any parameter updates
    def pre_update_params(self):
        if self.decay:
            self.current_learning_rate = self.learning_rate * (
                1.0 / (1.0 + self.decay * self.iterations)
            )

    # Update parameters
    def update_params(self, layer):

        # If we use momentum
        if self.beta:

            # If the layer does not contain momentum arrays, create them
            # filled with zeros
            if not hasattr(layer, "weight_momentums"):
                layer.weight_momentums = np.zeros_like(layer.dloss_dweights)
                # If there is no momentumm array for weights
                # the array doesnt exist for biases yet either
                layer.bias_momentums = np.zeros_like(layer.dloss_dbiases)

            # Build weight updates with momentum - take previous
            # updates multiplied by retain factor and update with
            # with current gradients
            # v[t+1] = \beta * v[t] - \alpha * dL/dw
            weight_updates = (
                self.beta * layer.weight_momentums
                + self.current_learning_rate * layer.dloss_dweights
            )
            layer.weight_momentums = weight_updates

            # Build bias updates
            bias_updates = (
                self.beta * layer.bias_momentums
                + self.current_learning_rate * layer.dloss_dbiases
            )
            layer.bias_momentums = bias_updates
        else:
            # Vanilla SGD updates (as before momentum update)
            weight_updates = self.current_learning_rate * layer.dloss_dweights
            bias_updates = self.current_learning_rate * layer.dloss_dbiases

        layer.weights += -weight_updates
        layer.biases += -bias_updates

    def post_update_params(self):
        self.iterations += 1
