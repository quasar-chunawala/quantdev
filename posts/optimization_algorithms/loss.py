import numpy as np
from abc import ABC, abstractmethod


class Loss:

    @abstractmethod
    def forward(self, y_pred, y_true):
        pass

    @abstractmethod
    def backward(self, y_pred, y_true):
        pass

    # Calculates the data and regularization losses
    # given model output and ground truth values
    def calculate(self, output, y):

        # Calculate the sample losses
        sample_losses = self.forward(output, y)

        # Calculate the mean loss
        data_loss = np.mean(sample_losses)

        # Return loss
        return data_loss
