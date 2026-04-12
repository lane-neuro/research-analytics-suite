"""
Operation:      RepeatedMeasuresANOVA
Version:        0.0.1
Description:    Approximate repeated-measures ANOVA across conditions using scipy F-test.

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


class RepeatedMeasuresANOVA(BaseOperation):
    """
    Approximate repeated-measures ANOVA across conditions.
    Each inner list in groups represents one condition's observations across subjects.
    Note: this is an approximation via scipy f_oneway; for full within-subjects correction
    use a dedicated library such as pingouin.

    Requires:
        groups (list): List of lists -- each inner list is one condition's values.
        n_conditions (int): Number of conditions (should equal len(groups)).

    Returns:
        f_stat (float): The F-statistic.
        p_value (float): The p-value.
        n_conditions (int): Number of conditions.
        note (str): Approximation warning.
    """
    name = "RepeatedMeasuresANOVA"
    version = "0.0.1"
    description = "Approximate repeated-measures ANOVA across conditions using scipy F-test."
    category_id = 303
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"groups": list, "n_conditions": int}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        from scipy import stats

        _inputs = self.get_inputs()
        groups = _inputs.get("groups", [])
        n_conditions = int(_inputs.get("n_conditions", len(groups)))

        f_stat, p_value = stats.f_oneway(*groups)
        note = (
            "Approximation via one-way F-test. For full within-subjects correction, "
            "use pingouin.rm_anova."
        )
        self.add_log_entry(
            f"[RESULT] F-statistic: {f_stat:.4f}; p-value: {p_value:.4f}; "
            f"n_conditions: {n_conditions}"
        )
        return {
            "f_stat": float(f_stat),
            "p_value": float(p_value),
            "n_conditions": n_conditions,
            "note": note,
        }
