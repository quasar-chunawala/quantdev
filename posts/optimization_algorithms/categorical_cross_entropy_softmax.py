import numpy as np
from softmax_activation import SoftmaxActivation
from categorical_cross_entropy_loss import CategoricalCrossEntropyLoss


class CategoricalCrossEntropySoftmax:

    # create activation and loss function objects
    def __init__(self):
        self.activation = SoftmaxActivation()
        self.loss = CategoricalCrossEntropyLoss()

    # forward pass
    def forward(self, inputs, y_true):

        self.inputs = inputs
        self.activation.forward(inputs)

        self.output = self.activation.output

        return self.loss.calculate(self.output, y_true)

    # Backward pass
    def backward(self, y_pred, y_true):
        # number of samples
        batch_size = len(y_pred)

        # number of labels
        num_labels = len(y_pred[0])

        # If labels are sparse, turn them into a one-hot vector
        if len(y_true.shape) == 1:
            y_true = np.eye(num_labels)[y_true]

        # Calculate the gradient
        self.dloss_dz = y_pred - y_true

        # Normalize the gradient
        self.dloss_dz = self.dloss_dz / batch_size
