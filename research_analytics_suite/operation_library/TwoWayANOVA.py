"""
Operation:      TwoWayANOVA
Version:        0.0.1
Description:    Perform a two-way ANOVA with interaction on a dataset with two categorical factors.

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


class TwoWayANOVA(BaseOperation):
    """
    Perform a two-way ANOVA with interaction on a dataset with two categorical factors.

    Requires:
        data (list): List of dicts, each with keys for value, factor_a, and factor_b.
        factor_a (str): Name of the first factor column.
        factor_b (str): Name of the second factor column.

    Returns:
        anova_table (dict): ANOVA table rows keyed by effect name, each with SS, df, F, p_value.
        interaction_p_value (float): p-value for the interaction term.
    """
    name = "TwoWayANOVA"
    version = "0.0.1"
    description = "Perform a two-way ANOVA with interaction on a dataset with two categorical factors."
    category_id = 303
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"data": list, "factor_a": str, "factor_b": str}
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
        import pandas as pd
        from statsmodels.formula.api import ols
        from statsmodels.stats.anova import anova_lm

        _inputs = self.get_inputs()
        data = _inputs.get("data", [])
        factor_a = str(_inputs.get("factor_a", "factor_a"))
        factor_b = str(_inputs.get("factor_b", "factor_b"))

        df = pd.DataFrame(data)
        formula = f"value ~ C({factor_a}) + C({factor_b}) + C({factor_a}):C({factor_b})"
        model = ols(formula, data=df).fit()
        table = anova_lm(model, typ=2)

        anova_table = {}
        for idx, row in table.iterrows():
            anova_table[str(idx)] = {
                "SS": float(row.get("sum_sq", 0.0)),
                "df": float(row.get("df", 0.0)),
                "F": float(row.get("F", 0.0)) if not pd.isna(row.get("F", float("nan"))) else None,
                "p_value": float(row.get("PR(>F)", 1.0)) if not pd.isna(row.get("PR(>F)", float("nan"))) else None,
            }

        interaction_key = f"C({factor_a}):C({factor_b})"
        interaction_p = anova_table.get(interaction_key, {}).get("p_value", None)

        self.add_log_entry(
            f"[RESULT] Two-way ANOVA: factors={factor_a}, {factor_b}; interaction p={interaction_p}"
        )
        return {
            "anova_table": anova_table,
            "interaction_p_value": float(interaction_p) if interaction_p is not None else None,
        }
