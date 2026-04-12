"""
Operation:      LogisticRegressionOperation
Version:        0.0.1
Description:    Perform logistic regression for binary or multiclass classification.

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
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class LogisticRegressionOperation(BaseOperation):
    """
    Perform logistic regression for binary or multiclass classification.

    Requires:
        X (list): List of lists -- each inner list is one observation's feature values.
        y (list): Class labels (int or float).
        multi_class (str): "ovr" (one-vs-rest) or "multinomial" (default "ovr").

    Returns:
        coefficients (list): Coefficient matrix [n_classes, n_features].
        intercept (list): Intercept per class.
        classes (list): Unique class labels.
        accuracy (float): Training accuracy.
        n_iter (int): Number of solver iterations.
    """
    name = "LogisticRegressionOperation"
    version = "0.0.1"
    description = "Perform logistic regression for binary or multiclass classification."
    category_id = 402
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"X": list, "y": list, "multi_class": str}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = True
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        import numpy as np
        from sklearn.linear_model import LogisticRegression

        _inputs = self.get_inputs()
        X = _inputs.get("X", [])
        y = _inputs.get("y", [])
        multi_class = str(_inputs.get("multi_class", "ovr"))

        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y)

        model = LogisticRegression(
            multi_class=multi_class, max_iter=1000, solver="lbfgs"
        )
        model.fit(X_arr, y_arr)

        accuracy = float(model.score(X_arr, y_arr))
        n_iter = int(model.n_iter_[0])

        self.add_log_entry(
            f"[RESULT] n_classes={len(model.classes_)}; accuracy={accuracy:.4f}; "
            f"n_iter={n_iter}"
        )
        return {
            "coefficients": [list(float(v) for v in row) for row in model.coef_],
            "intercept": [float(v) for v in model.intercept_],
            "classes": [int(c) if hasattr(c, "item") else c for c in model.classes_.tolist()],
            "accuracy": accuracy,
            "n_iter": n_iter,
        }
