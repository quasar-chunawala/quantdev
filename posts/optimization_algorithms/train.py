import numpy as np
import nnfs
import matplotlib.pyplot as plt
from nnfs.datasets import spiral_data

from dense_layer import DenseLayer
from relu_activation import ReLUActivation
from softmax_activation import SoftmaxActivation

from loss import Loss
from categorical_cross_entropy_loss import CategoricalCrossEntropyLoss
from categorical_cross_entropy_softmax import CategoricalCrossEntropySoftmax
from sgd_optimizer import SGDOptimizer


def train(decay, momentum):
    # Create a dataset
    X, y = spiral_data(samples=100, classes=3)

    # Create a dense layer with 2 input features and 64 output values
    dense1 = DenseLayer(2, 64)

    # Create ReLU activation (to be used with the dense layer)
    activation1 = ReLUActivation()

    # Create second DenseLayer with 64 input features (as we take output of the
    # previous layer here) and 3 output values
    dense2 = DenseLayer(64, 3)

    # Create Softmax classifier's combined loss and activation
    loss_activation = CategoricalCrossEntropySoftmax()

    # Create optimizer
    optimizer = SGDOptimizer(learning_rate=1.0, decay=decay, momentum=momentum)

    acc_vals = []
    loss_vals = []
    lr_vals = []

    # Train in a loop
    for epoch in range(10001):
        # Perform a forward pass of our training data through this layer
        dense1.forward(X)

        # Perform a forward pass through the activation function
        # takes the output of the first dense layer here
        activation1.forward(dense1.output)

        # Perform a forward pass through second DenseLayer
        # takes the outputs of the activation function of first layer as inputs
        dense2.forward(activation1.output)

        # Perform a forward pass through the activation/loss function
        # takes the output of the second DenseLayer here and returns the loss
        loss = loss_activation.forward(dense2.output, y)

        # Calculate accuracy from output of activation2 and targets
        # Calculate values along the first axis
        predictions = np.argmax(loss_activation.output, axis=1)
        if len(y.shape) == 2:
            y = np.argmax(y, axis=1)

        accuracy = np.mean(predictions == y)

        if epoch % 100 == 0:
            print(
                f"epoch: {epoch}, \
                acc : {accuracy:.3f}, \
                loss: {loss: .3f}, \
                lr : {optimizer.current_learning_rate}"
            )

        acc_vals.append(accuracy)
        loss_vals.append(loss)
        lr_vals.append(optimizer.current_learning_rate)

        # Backward pass
        loss_activation.backward(loss_activation.output, y)
        dense2.backward(loss_activation.dloss_dz)
        activation1.backward(dense2.dloss_dinputs)
        dense1.backward(activation1.dloss_dz)

        # Update the weights and the biases
        optimizer.pre_update_params()
        optimizer.update_params(dense1)
        optimizer.update_params(dense2)
        optimizer.post_update_params()

    return acc_vals, loss_vals, lr_vals


acc_vals, loss_vals, lr_vals = train(decay=1e-3, momentum=0)
