"""
GPUComputation Module

This file contains the GPUComputation class which is responsible for performing computations on the GPU.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import torch


def gpu_computation(data):
    tensor = torch.tensor(data, device='cuda')
    result = tensor * 2  # Example computation
    return result.cpu().numpy().tolist()
