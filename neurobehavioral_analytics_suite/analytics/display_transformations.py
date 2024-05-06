"""
Module for applying and visualizing transformations in the NeuroBehavioral Analytics Suite.

This module defines a function to apply a series of transformations to a given dataset and visualize the results
using matplotlib. It includes methods for deep copying data, applying transformations, and plotting the results.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from copy import deepcopy
from matplotlib import pyplot as plt


def display_transformations(data_in, transformations, cmap='viridis'):
    """
    Applies a series of transformations to a given dataset and visualizes the results.

    This function applies each transformation in the list to the dataset in order and plots the results using matplotlib.

    Args:
        data_in: The dataset to apply the transformations to.
        transformations (list): The list of transformations to be applied.
        cmap (str): The colormap to use for the plot.

    Returns:
        None
    """

    plt.figure(figsize=(10, 10))

    # Create a colormap based on the number of transformations
    colormap = plt.get_cmap(cmap, len(transformations) + 1)

    # Plot the original data first
    x_original = []
    y_original = []
    for frame in data_in.pose.frames:
        for coord in frame.coords:
            x_original.append(coord.x)
            y_original.append(coord.y)
    plt.scatter(x_original, y_original, color=colormap(0), label='Original', s=1,
                alpha=0.5)  # Using the first color of colormap

    current_frames = deepcopy(data_in.pose.frames)

    # Apply each transformation in sequence and plot
    for i, transform in enumerate(transformations):
        transformed_x = []
        transformed_y = []

        # Apply the transformation to current_frames
        for frame in current_frames:
            for coord in frame.coords:
                transformed_coord = transform.transform(deepcopy(coord))
                transformed_x.append(transformed_coord.x)
                transformed_y.append(transformed_coord.y)
                coord.x = transformed_coord.x  # Update the coordinate for the next transformation
                coord.y = transformed_coord.y

        # Plot the transformed coordinates using the next color in the colormap
        plt.scatter(transformed_x, transformed_y, color=colormap(i + 1), label=str(transform.__repr__()), s=1,
                    alpha=0.5)

    plt.title("Visualization of Transformations")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend(loc='upper right', markerscale=5)
    plt.grid(True)
    plt.show()
