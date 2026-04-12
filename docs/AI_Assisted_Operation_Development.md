# AI-Assisted Operation Development for RAS

This guide explains how to use generative AI (such as Claude, ChatGPT, or similar tools) to rapidly develop custom analytics operations for the Research Analytics Suite (RAS). By the end, you will understand the operation interface well enough to write an effective AI prompt and integrate the result into RAS with minimal friction.

---

## Table of Contents

1. [What is a RAS Operation?](#1-what-is-a-ras-operation)
2. [The Operation Interface](#2-the-operation-interface)
3. [Category Reference](#3-category-reference)
4. [The Prompt Template](#4-the-prompt-template)
5. [Worked Examples](#5-worked-examples)
6. [Validating and Installing Your Operation](#6-validating-and-installing-your-operation)
7. [Tips and Common Pitfalls](#7-tips-and-common-pitfalls)

---

## 1. What is a RAS Operation?

An **operation** is a self-contained, reusable analytics routine that RAS can discover, schedule, chain, and execute. Operations range from simple calculations (computing a mean) to complex pipelines (ARIMA forecasting, stepwise regression).

Each operation lives in a single `.py` file inside:

```
research_analytics_suite/operation_library/
```

RAS discovers operations automatically at startup — no import list or registration step is required. You only need to drop the file in that folder and restart RAS.

---

## 2. The Operation Interface

Every operation inherits from `BaseOperation` and implements exactly three methods. The structure below is the complete contract.

### 2.1 File Header (docstring)

```python
"""
Operation:      YourOperationName
Version:        0.0.1
Description:    One-line description of what this operation does.

Author:         Your Name
GitHub:         your-github-username
Email:          your.email@example.com

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Your Name
Status:         In Progress
"""
```

### 2.2 Required Class Attributes

| Attribute | Type | Purpose |
|---|---|---|
| `name` | `str` | Unique identifier for the operation (matches the class name) |
| `version` | `str` | Semantic version string, e.g. `"0.0.1"` |
| `description` | `str` | One-line human-readable description |
| `category_id` | `int` | Integer subcategory code (see [Category Reference](#3-category-reference)) |
| `author` | `str` | Your display name |
| `github` | `str` | Your GitHub username |
| `email` | `str` | Your contact email |
| `required_inputs` | `dict[str, type]` | Input name → bare Python type **only** (e.g. `{"x": list, "n": int}`). Do NOT use nested dicts with `"type"` or `"description"` keys. |
| `parent_operation` | `Optional[Type[BaseOperation]]` | Always `None` for standalone operations |
| `inheritance` | `Optional[list]` | Always `[]` for standalone operations |
| `is_loop` | `bool` | `True` only if the operation manages its own internal loop |
| `is_cpu_bound` | `bool` | `True` for computationally intensive work (enables process pool) |
| `is_gpu_bound` | `bool` | `True` if a GPU is required |
| `parallel` | `bool` | `True` if child operations should run in parallel |

### 2.3 Required Methods

#### `__init__`
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
```
Only add instance attributes here if you need state between `initialize_operation` and `execute`. Most operations need nothing beyond the `super()` call.

#### `initialize_operation`
```python
async def initialize_operation(self):
    await super().initialize_operation()
    # Optional: open files, instantiate sub-operations, etc.
```
Called once before `execute`. Use it to set up any resources that are expensive to create. Always call `super()` first.

#### `execute`
```python
async def execute(self):
    _inputs = self.get_inputs()
    value = _inputs.get("input_name", default_value)

    # ... computation ...

    self.add_log_entry(f"[RESULT] ...")
    return {"output_name": result}
```
The return value is a `dict` mapping output names to values. Log the key results with `self.add_log_entry`. Wrap the body in a `try/except` and call `self.handle_error(e)` on exceptions you cannot recover from.

### 2.4 Minimal Complete Template

```python
"""
Operation:      MyOperation
Version:        0.0.1
Description:    Describe what this operation does.

Author:         Your Name
GitHub:         your-github-username
Email:          your.email@example.com

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Your Name
Status:         In Progress
"""
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class MyOperation(BaseOperation):
    """
    Describe what this operation does.

    Requires:
        input_name (type): Description.

    Returns:
        output_name (type): Description.
    """
    name = "MyOperation"
    version = "0.0.1"
    description = "Describe what this operation does."
    category_id = 101               # Replace with appropriate code
    author = "Your Name"
    github = "your-github-username"
    email = "your.email@example.com"
    required_inputs = {"input_name": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    is_gpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        _inputs = self.get_inputs()
        input_name = _inputs.get("input_name", [])

        result = sum(input_name)  # Replace with real logic

        self.add_log_entry(f"[RESULT] output_name: {result}")
        return {"output_name": result}
```

---

## 3. Category Reference

Set `category_id` to the integer code that best describes your operation.

| Category | Subcategory | Code |
|---|---|---|
| Descriptive Statistics | Central Tendency | **101** |
| | Variability | **102** |
|  | Distribution | **103** |
| Inferential Statistics | Parametric Tests | **201** |
|  | Non-parametric Tests | **202** |
|  | Confidence Intervals | **203** |
| Hypothesis Testing | T-Tests | **301** |
| | Chi-Square Tests | **302** |
| | ANOVA | **303** |
| Regression & Correlation | Linear Regression | **401** |
| | Multiple Regression | **402** |
| | Correlation Analysis | **403** |
| Time Series Analysis | Trend Analysis | **501** |
| | Seasonal Analysis | **502** |
| | Forecasting | **503** |
| Data Preprocessing | Data Cleaning | **601** |
| | Data Transformation | **602** |
| | Data Normalization | **603** |

---

## 4. The Prompt Template

Copy this template and fill in the bracketed sections when prompting a generative AI tool. The more specific your description, the better the result.

---

```
You are a Python developer working on the Research Analytics Suite (RAS), a scientific
data analysis platform. Your task is to implement a single RAS operation as a standalone
Python file.

## OPERATION SPECIFICATION

Name:           [OperationClassName]          # PascalCase, no spaces
Description:    [What this operation computes or does]
Category:       [Category name from the list below] → code [NNN]
Author:         [Your name]
GitHub:         [Your GitHub username]
Email:          [Your email]

Inputs:
  [input_name_1] ([python_type]): [Description, including units or valid range if relevant]
  [input_name_2] ([python_type]): [Description]
  ...

Outputs:
  [output_name_1] ([python_type]): [Description]
  [output_name_2] ([python_type]): [Description]
  ...

Additional details:
  [Any special algorithm choices, edge-case handling, or library preferences.
   E.g. "Use scipy.stats for the computation", "Mark is_cpu_bound = True",
   "Return NaN for empty inputs rather than raising", etc.]


## CATEGORY CODES (pick the most relevant integer for category_id)

101 Central Tendency | 102 Variability | 103 Distribution
201 Parametric Tests | 202 Non-parametric Tests | 203 Confidence Intervals
301 T-Tests | 302 Chi-Square Tests | 303 ANOVA
401 Linear Regression | 402 Multiple Regression | 403 Correlation Analysis
501 Trend Analysis | 502 Seasonal Analysis | 503 Forecasting
601 Data Cleaning | 602 Data Transformation | 603 Data Normalization


## RULES (follow exactly — deviations will break the auto-discovery loader)

1. The file must contain exactly ONE class that inherits from BaseOperation.
2. The class name must exactly match the `name` attribute string.
3. All required class-level attributes must be present:
       name, version, description, category_id, author, github, email,
       required_inputs, parent_operation, inheritance,
       is_loop, is_cpu_bound, is_gpu_bound, parallel
3a. `required_inputs` must be a flat dict mapping string keys to bare Python types.
    The value for each key must be a plain type object — NOT a nested dict, NOT a string,
    NOT a dict with "type"/"description" sub-keys.

    CORRECT:   required_inputs = {"numbers": list, "n": int, "alpha": float}
    WRONG:     required_inputs = {"numbers": {"type": list, "description": "..."}}
    WRONG:     required_inputs = {"numbers": "list"}

4. Only two imports at the module level are allowed:
       from typing import Optional, Type
       from research_analytics_suite.operation_manager import BaseOperation
   All other imports (numpy, scipy, pandas, etc.) must be placed INSIDE
   the execute() method body, not at the top of the file.
5. `initialize_operation` must call `await super().initialize_operation()` first.
6. `execute` must:
     a. Retrieve inputs with:  _inputs = self.get_inputs()
     b. Extract each input:    value = _inputs.get("key", default)
     c. Return a dict mapping output names to computed values.
     d. Call self.add_log_entry(f"[RESULT] ...") with a summary before returning.
7. Wrap the compute block in try/except; call self.handle_error(e) and re-raise.
8. Do NOT add extra methods, properties, class methods, or helper functions.
9. Follow the exact file-header docstring format shown below.
10. Set is_cpu_bound = True for operations involving iterative fitting, large matrix
    operations, or loops over >1 000 rows.


## FILE-HEADER DOCSTRING FORMAT

"""
Operation:      [OperationClassName]
Version:        0.0.1
Description:    [One-line description]

Author:         [Your name]
GitHub:         [GitHub username]
Email:          [Email]

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     [Your name]
Status:         In Progress
"""


## MINIMAL SKELETON (replace the execute body with real logic)

from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class [OperationClassName](BaseOperation):
    """
    [One-line description]

    Requires:
        [input_name] ([type]): [Description]

    Returns:
        [output_name] ([type]): [Description]
    """
    name = "[OperationClassName]"
    version = "0.0.1"
    description = "[One-line description]"
    category_id = [NNN]
    author = "[Your name]"
    github = "[GitHub username]"
    email = "[Email]"
    required_inputs = {[input dict]}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    is_gpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        try:
            [imports here]
            _inputs = self.get_inputs()
            [extract inputs]

            [computation]

            self.add_log_entry(f"[RESULT] [summary]")
            return {[output dict]}
        except Exception as e:
            self.handle_error(e)
            raise


Now produce the complete, ready-to-save Python file for the operation specified above.
```

---

## 5. Worked Examples

The following examples show how to fill in the template for operations of increasing complexity. The expected AI output follows each prompt excerpt.

---

### Example A — Single Input, Single Output (Descriptive Statistic)

One input, one output, one library call. This is the floor-level complexity for any new operation.

**Prompt excerpt (OPERATION SPECIFICATION section only):**

```
Name:           GeometricMean
Description:    Compute the geometric mean of a list of positive numbers.
Category:       Central Tendency → code 101
Author:         Jane Researcher
GitHub:         jresearcher
Email:          jane@university.edu

Inputs:
  numbers (list): A list of positive numerical values.

Outputs:
  geometric_mean (float): The geometric mean of the input values.

Additional details:
  Use scipy.stats.gmean. Return 0.0 for empty input without raising.
```

**Expected AI output:**

```python
"""
Operation:      GeometricMean
Version:        0.0.1
Description:    Compute the geometric mean of a list of positive numbers.

Author:         Jane Researcher
GitHub:         jresearcher
Email:          jane@university.edu

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Jane Researcher
Status:         In Progress
"""
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class GeometricMean(BaseOperation):
    """
    Compute the geometric mean of a list of positive numbers.

    Requires:
        numbers (list): A list of positive numerical values.

    Returns:
        geometric_mean (float): The geometric mean of the input values.
    """
    name = "GeometricMean"
    version = "0.0.1"
    description = "Compute the geometric mean of a list of positive numbers."
    category_id = 101
    author = "Jane Researcher"
    github = "jresearcher"
    email = "jane@university.edu"
    required_inputs = {"numbers": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    is_gpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        try:
            from scipy.stats import gmean
            _inputs = self.get_inputs()
            numbers = _inputs.get("numbers", [])

            if not numbers:
                self.add_log_entry("[RESULT] GeometricMean: 0.0 (empty input)")
                return {"geometric_mean": 0.0}

            geometric_mean = float(gmean(numbers))
            self.add_log_entry(f"[RESULT] GeometricMean: {geometric_mean}")
            return {"geometric_mean": geometric_mean}
        except Exception as e:
            self.handle_error(e)
            raise
```

---

### Example B — Two Inputs, Multiple Outputs (Hypothesis Test)

Two sample inputs, four diagnostic outputs. The complexity comes from interpreting and surfacing multiple results from a single statistical test.

**Prompt excerpt:**

```
Name:           ChiSquareGoodnessOfFit
Description:    Perform a chi-square goodness-of-fit test and report the statistic,
                p-value, degrees of freedom, and effect size (Cramer's V).
Category:       Chi-Square Tests → code 302
Author:         Jane Researcher
GitHub:         jresearcher
Email:          jane@university.edu

Inputs:
  observed (list): Observed frequency counts (non-negative integers).
  expected (list): Expected frequency counts. If empty, assume a uniform distribution
                   across the observed categories.

Outputs:
  chi2_stat (float):  The chi-square test statistic.
  p_value (float):    The p-value of the test.
  dof (int):          Degrees of freedom (number of categories minus 1).
  cramers_v (float):  Cramer's V effect size (0 = no association, 1 = perfect).

Additional details:
  Use scipy.stats.chisquare. Compute Cramer's V as sqrt(chi2 / (n * (k - 1)))
  where n is the total count and k is the number of categories.
  Return 0.0 for cramers_v when n or k-1 is zero.
```

**Expected AI output:**

```python
"""
Operation:      ChiSquareGoodnessOfFit
Version:        0.0.1
Description:    Perform a chi-square goodness-of-fit test and report the statistic,
                p-value, degrees of freedom, and effect size (Cramer's V).

Author:         Jane Researcher
GitHub:         jresearcher
Email:          jane@university.edu

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Jane Researcher
Status:         In Progress
"""
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class ChiSquareGoodnessOfFit(BaseOperation):
    """
    Perform a chi-square goodness-of-fit test and report the statistic,
    p-value, degrees of freedom, and effect size (Cramer's V).

    Requires:
        observed (list): Observed frequency counts (non-negative integers).
        expected (list): Expected frequency counts. If empty, uniform distribution assumed.

    Returns:
        chi2_stat (float):  The chi-square test statistic.
        p_value (float):    The p-value of the test.
        dof (int):          Degrees of freedom.
        cramers_v (float):  Cramer's V effect size.
    """
    name = "ChiSquareGoodnessOfFit"
    version = "0.0.1"
    description = ("Perform a chi-square goodness-of-fit test and report the statistic, "
                   "p-value, degrees of freedom, and effect size (Cramer's V).")
    category_id = 302
    author = "Jane Researcher"
    github = "jresearcher"
    email = "jane@university.edu"
    required_inputs = {"observed": list, "expected": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    is_gpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        try:
            import math
            from scipy.stats import chisquare

            _inputs = self.get_inputs()
            observed = _inputs.get("observed", [])
            expected = _inputs.get("expected", []) or None

            result = chisquare(f_obs=observed, f_exp=expected)
            chi2_stat = float(result.statistic)
            p_value = float(result.pvalue)
            k = len(observed)
            dof = k - 1
            n = sum(observed)
            cramers_v = math.sqrt(chi2_stat / (n * dof)) if (n > 0 and dof > 0) else 0.0

            self.add_log_entry(
                f"[RESULT] chi2={chi2_stat:.4f}; p={p_value:.4f}; "
                f"dof={dof}; Cramer's V={cramers_v:.4f}"
            )
            return {
                "chi2_stat": chi2_stat,
                "p_value": p_value,
                "dof": dof,
                "cramers_v": cramers_v,
            }
        except Exception as e:
            self.handle_error(e)
            raise
```

---

### Example C — Multiple Mixed-Type Inputs, Rich Model Outputs (Regression)

Five inputs of mixed types, six outputs drawn from a fitted statistical model. The complexity lies in correctly extracting and serializing model diagnostics.

**Prompt excerpt:**

```
Name:           MultipleLinearRegressionDiagnostics
Description:    Fit an OLS multiple linear regression model and return coefficients,
                p-values, R-squared, adjusted R-squared, AIC, and BIC.
Category:       Multiple Regression → code 402
Author:         Jane Researcher
GitHub:         jresearcher
Email:          jane@university.edu

Inputs:
  X (list):         A list of observations, where each observation is itself a list
                    of predictor values (i.e. a 2-D list, rows × predictors).
  y (list):         A list of outcome values (one per observation).
  add_constant (list): Single-element list containing a bool (True to prepend an
                    intercept column via statsmodels.add_constant, False to skip).

Outputs:
  coefficients (list):    Fitted coefficient for each predictor (and intercept if added).
  p_values (list):        P-value for each coefficient.
  r_squared (float):      R² of the fitted model.
  adj_r_squared (float):  Adjusted R².
  aic (float):            Akaike Information Criterion.
  bic (float):            Bayesian Information Criterion.

Additional details:
  Use statsmodels OLS. Extract add_constant as add_constant[0] (bool).
  Convert all list outputs to plain Python floats before returning.
```

**Expected AI output:**

```python
"""
Operation:      MultipleLinearRegressionDiagnostics
Version:        0.0.1
Description:    Fit an OLS multiple linear regression model and return coefficients,
                p-values, R-squared, adjusted R-squared, AIC, and BIC.

Author:         Jane Researcher
GitHub:         jresearcher
Email:          jane@university.edu

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Jane Researcher
Status:         In Progress
"""
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class MultipleLinearRegressionDiagnostics(BaseOperation):
    """
    Fit an OLS multiple linear regression model and return coefficients,
    p-values, R-squared, adjusted R-squared, AIC, and BIC.

    Requires:
        X (list):            2-D list of predictor values (rows × predictors).
        y (list):            Outcome values, one per observation.
        add_constant (list): Single-element list containing a bool; True prepends
                             an intercept column.

    Returns:
        coefficients (list):   Fitted coefficients.
        p_values (list):       P-values for each coefficient.
        r_squared (float):     R² of the model.
        adj_r_squared (float): Adjusted R².
        aic (float):           Akaike Information Criterion.
        bic (float):           Bayesian Information Criterion.
    """
    name = "MultipleLinearRegressionDiagnostics"
    version = "0.0.1"
    description = ("Fit an OLS multiple linear regression model and return coefficients, "
                   "p-values, R-squared, adjusted R-squared, AIC, and BIC.")
    category_id = 402
    author = "Jane Researcher"
    github = "jresearcher"
    email = "jane@university.edu"
    required_inputs = {"X": list, "y": list, "add_constant": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    is_gpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        try:
            import numpy as np
            import statsmodels.api as sm

            _inputs = self.get_inputs()
            X = np.array(_inputs.get("X", []), dtype=float)
            y = np.array(_inputs.get("y", []), dtype=float)
            use_constant = bool(_inputs.get("add_constant", [True])[0])

            if use_constant:
                X = sm.add_constant(X)

            model = sm.OLS(y, X).fit()

            coefficients = [float(v) for v in model.params.tolist()]
            p_values = [float(v) for v in model.pvalues.tolist()]

            self.add_log_entry(
                f"[RESULT] R²={model.rsquared:.4f}; adj-R²={model.rsquared_adj:.4f}; "
                f"AIC={model.aic:.4f}; BIC={model.bic:.4f}"
            )
            return {
                "coefficients": coefficients,
                "p_values": p_values,
                "r_squared": float(model.rsquared),
                "adj_r_squared": float(model.rsquared_adj),
                "aic": float(model.aic),
                "bic": float(model.bic),
            }
        except Exception as e:
            self.handle_error(e)
            raise
```

---

## 6. Validating and Installing Your Operation

### 6.1 Check the file

Before installing, verify three things manually:

1. **Class name matches `name` attribute** — the loader uses the `name` attribute, not the filename, but keeping them the same avoids confusion.
2. **All required class attributes are present** — compare against the table in [Section 2.2](#22-required-class-attributes).
3. **No module-level imports other than `typing` and `BaseOperation`** — all scientific library imports must be inside `execute()`.

### 6.2 Install

Where to drop the file depends on whether you are running the packaged application or the source code directly.

---

#### Windows (packaged app)

1. Locate `ResearchAnalyticsSuite.exe` — typically in `C:\Program Files\ResearchAnalyticsSuite\` or wherever you extracted the release.
2. Open the `_internal` folder in the same directory as the `.exe`.
3. Copy your operation file into `_internal\operation_library_src\`.

```
ResearchAnalyticsSuite.exe
_internal\
    operation_library_src\
        YourOperation.py   ← place it here
```

---

#### macOS (packaged app)

1. Open **Finder** and navigate to your **Applications** folder.
2. Right-click `ResearchAnalyticsSuite.app` and choose **Show Package Contents**.
3. Navigate to `Contents/Frameworks/operation_library_src/`.
4. Copy your operation file into that folder.

```
ResearchAnalyticsSuite.app/
    Contents/
        Frameworks/
            operation_library_src/
                YourOperation.py   ← place it here
```

---

Regardless of platform, **restart RAS after copying the file**. The operation loader runs at startup — there is no hot-reload.

### 6.3 Verify discovery

Start RAS and look for your operation name in the operation browser.


---

## 7. Tips and Common Pitfalls

| Pitfall | Fix |
|---|---|
| **`required_inputs` values are nested dicts** (e.g. `{"type": list, "description": "..."}`) instead of bare types | Use `{"key": list}` — the value must be the raw Python type, nothing else |
| **Module-level scientific imports** cause import errors when the environment is missing a package | Move all `import numpy`, `from scipy...` etc. inside `execute()` |
| **Class name ≠ `name` attribute** causes the operation to appear under the wrong name in the UI | Keep them identical |
| **`initialize_operation` missing `await super()`** causes the operation to never reach `running` status | Always put `await super().initialize_operation()` as the first line |
| **Returning a non-dict from `execute`** crashes the output handler | Always `return {"key": value, ...}` |
| **Forgetting `self.handle_error(e)`** means exceptions are silently swallowed | Wrap the body in `try/except Exception as e:` and call `self.handle_error(e); raise` |
| **Setting `is_cpu_bound = False` for a heavy computation** causes the UI to freeze | Set `is_cpu_bound = True` for anything that runs iterative solvers or large matrix ops |
| **Using `print()` instead of `self.add_log_entry()`** means output never appears in the RAS log panel | Replace all `print` calls with `self.add_log_entry(f"[RESULT] ...")` |
| **Adding helper methods** to the class works but is not needed and adds noise | Keep computation inline inside `execute()` |

### Iterating with AI

If the generated code has a bug or doesn't match your needs, give the AI the error message and the relevant rule it violated. For example:

> The code you generated has `import numpy as np` at the top of the file. Per Rule 4, all imports other than `typing` and `BaseOperation` must be inside `execute()`. Please move the import.

AI models respond well to explicit rule references from the prompt template above.
