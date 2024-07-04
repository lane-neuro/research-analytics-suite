"""
Operation:      NeuralNetworkTraining
Version:        0.0.1
Description:    Train a neural network on a dataset.

Author:         Lane
GitHub:         lane-neuro
Email:          justlane@uw.edu

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Lane (GitHub: @lane-neuro)
Status:         In Progress
"""
from typing import List, Optional, Type

from keras import Sequential
from tensorflow.keras.layers import Dense
from research_analytics_suite.operation_manager import BaseOperation


class NeuralNetworkTraining(BaseOperation):
    """
    Train a neural network on a dataset.

    Attributes:
        x_train (List): The training features.
        y_train (List): The training target variable.

    Returns:
        model: The trained neural network model.
    """
    name = "NeuralNetworkTraining"
    version = "0.0.1"
    description = "Train a neural network on a dataset."
    category_id = 1302
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"X_train": list, "y_train": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, x_train: List, y_train: List, *args, **kwargs):
        """
        Initialize the operation with the training features and target variable.

        Args:
            x_train (List): The training features.
            y_train (List): The training target variable.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.x_train = x_train
        self.y_train = y_train
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: train the neural network on the dataset.
        """
        model = Sequential([
            Dense(64, activation='relu', input_shape=(len(self.x_train[0]),)),
            Dense(64, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        model.fit(self.x_train, self.y_train, epochs=10, batch_size=32)
        print("Model training completed.")
