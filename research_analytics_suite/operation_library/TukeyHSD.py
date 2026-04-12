"""
Operation:      TukeyHSD
Version:        0.0.1
Description:    Perform Tukey's HSD post-hoc pairwise comparisons following ANOVA.

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


class TukeyHSD(BaseOperation):
    """
    Perform Tukey's HSD post-hoc pairwise comparisons following a one-way ANOVA.

    Requires:
        groups (list): List of lists -- each inner list contains numerical values for one group.
        group_names (list): Optional list of string labels for the groups.

    Returns:
        comparisons (list): List of dicts, each with keys group1, group2, meandiff, p_adj, reject.
    """
    name = "TukeyHSD"
    version = "0.0.1"
    description = "Perform Tukey's HSD post-hoc pairwise comparisons following ANOVA."
    category_id = 303
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"groups": list, "group_names": list}
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
        from statsmodels.stats.multicomp import pairwise_tukeyhsd

        _inputs = self.get_inputs()
        groups = _inputs.get("groups", [])
        group_names = _inputs.get("group_names", [])

        if not group_names:
            group_names = [f"Group{i + 1}" for i in range(len(groups))]

        values = np.concatenate([np.array(g, dtype=float) for g in groups])
        labels = np.concatenate([
            np.array([group_names[i]] * len(groups[i]))
            for i in range(len(groups))
        ])

        result = pairwise_tukeyhsd(values, labels, alpha=0.05)
        summary_data = result.summary().data[1:]

        comparisons = []
        for row in summary_data:
            comparisons.append({
                "group1": str(row[0]),
                "group2": str(row[1]),
                "meandiff": float(row[2]),
                "p_adj": float(row[3]),
                "reject": bool(row[6]),
            })

        n_significant = sum(1 for c in comparisons if c["reject"])
        self.add_log_entry(
            f"[RESULT] {len(comparisons)} pairwise comparisons; {n_significant} significant at alpha=0.05"
        )
        return {"comparisons": comparisons}
