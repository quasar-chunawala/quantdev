import numpy as np
from loss import Loss


class CategoricalCrossEntropyLoss(Loss):

    # Forward pass
    def forward(self, y_pred, y_true):
        num_samples = len(y_pred)

        # Clip data to prevent division by 0
        # Clip both sides to not drag mean towards any value
        epsilon = 1e-7
        y_pred_clipped = np.clip(y_pred, epsilon, 1 - epsilon)

        # If categorical labels
        if len(y_true.shape) == 1:
            correct_confidences = y_pred_clipped[range(len(y_pred)), y_true]
        # else if one-hot encoding
        elif len(y_true.shape) == 2:
            correct_confidences = np.sum(y_pred_clipped * y_true, axis=1)

        neg_log = -np.log(correct_confidences)
        return neg_log

    # Backward pass
    def backward(self, y_pred, y_true):

        # number of samples
        batch_size = len(y_pred)

        # number of labels
        num_labels = len(y_pred[0])

        # If labels are sparse, turn them into a one-hot vector
        if len(y_true.shape) == 1:
            y_true = np.eye(num_labels)[y_true]

        # Calculate gradient
        self.dloss_da = -y_true / y_pred

        # Normalize the gradient
        self.dloss_da = self.dloss_da / batch_size
