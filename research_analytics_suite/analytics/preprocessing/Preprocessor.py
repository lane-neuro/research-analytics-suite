import numpy as np
from sklearn.preprocessing import StandardScaler

from research_analytics_suite.commands import register_commands, command


@register_commands
class Preprocessor:
    def __init__(self):
        self.scaler = StandardScaler()

    @command
    def fit_transform(self, data):
        # Check if data is a scalar value
        if np.isscalar(data):
            # Convert data to a 2D array
            data = np.array([[data]])
        elif len(data.shape) == 1:
            # Reshape data to have a single feature
            data = data.reshape(-1, 1)
        return self.scaler.fit_transform(data)

    @command
    def transform(self, data):
        # Check if data is a scalar value
        if np.isscalar(data):
            # Convert data to a 2D array
            data = np.array([[data]])
        elif len(data.shape) == 1:
            # Reshape data to have a single feature
            data = data.reshape(-1, 1)
        return self.scaler.transform(data)