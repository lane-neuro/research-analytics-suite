"""
Operation:      StepwiseRegression
Version:        0.0.1
Description:    Perform greedy forward or backward stepwise variable selection by AIC or BIC.

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


class StepwiseRegression(BaseOperation):
    """
    Perform greedy forward or backward stepwise variable selection using OLS.
    Selection criterion is AIC or BIC.

    Requires:
        X (list): List of lists -- each inner list is one observation's predictor values.
        y (list): Dependent variable values.
        direction (str): "forward" or "backward" (default "forward").
        criterion (str): "aic" or "bic" (default "aic").

    Returns:
        selected_indices (list): Zero-based column indices of selected predictors.
        final_aic (float): AIC of the final model.
        final_bic (float): BIC of the final model.
        final_r_squared (float): R-squared of the final model.
        steps (int): Number of selection steps taken.
    """
    name = "StepwiseRegression"
    version = "0.0.1"
    description = "Perform greedy forward or backward stepwise variable selection by AIC or BIC."
    category_id = 402
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"X": list, "y": list, "direction": str, "criterion": str}
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
        import statsmodels.api as sm

        _inputs = self.get_inputs()
        X = _inputs.get("X", [])
        y = _inputs.get("y", [])
        direction = str(_inputs.get("direction", "forward"))
        criterion = str(_inputs.get("criterion", "aic")).lower()

        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y, dtype=float)
        n_predictors = X_arr.shape[1]

        def score(indices):
            if not indices:
                return float("inf")
            cols = sm.add_constant(X_arr[:, list(indices)])
            m = sm.OLS(y_arr, cols).fit()
            return float(m.aic) if criterion == "aic" else float(m.bic)

        steps = 0
        if direction == "forward":
            selected = set()
            remaining = set(range(n_predictors))
            while remaining:
                best_score = float("inf")
                best_idx = None
                for idx in remaining:
                    s = score(selected | {idx})
                    if s < best_score:
                        best_score = s
                        best_idx = idx
                current_score = score(selected)
                if best_idx is not None and best_score < current_score:
                    selected.add(best_idx)
                    remaining.remove(best_idx)
                    steps += 1
                else:
                    break
        else:
            selected = set(range(n_predictors))
            while len(selected) > 1:
                best_score = score(selected)
                best_remove = None
                for idx in selected:
                    candidate = selected - {idx}
                    s = score(candidate)
                    if s < best_score:
                        best_score = s
                        best_remove = idx
                if best_remove is not None:
                    selected.remove(best_remove)
                    steps += 1
                else:
                    break

        selected_indices = sorted(selected)
        final_cols = sm.add_constant(X_arr[:, selected_indices])
        final_model = sm.OLS(y_arr, final_cols).fit()

        self.add_log_entry(
            f"[RESULT] {direction} selection; criterion={criterion}; "
            f"selected {len(selected_indices)} predictors in {steps} steps; "
            f"final AIC={final_model.aic:.4f}"
        )
        return {
            "selected_indices": selected_indices,
            "final_aic": float(final_model.aic),
            "final_bic": float(final_model.bic),
            "final_r_squared": float(final_model.rsquared),
            "steps": steps,
        }
