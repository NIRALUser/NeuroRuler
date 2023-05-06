"""Constants used in tests."""

import os
import numpy as np

TARGET_R_SQUARED: float = 0.98
UBUNTU_GITHUB_ACTIONS_CI: bool = os.getenv("HOME") == "/home/runner"
"""Whether the tests are being run in an Ubuntu GitHub Actions CI environment.
Use this to skip PyQt6 imports if in Ubuntu GH Actions CI environment.

Ubuntu environments lack a required ``libEGL.so`` file for PyQt6 imports. This causes an error when importing PyQt6.
However, Windows environments have the required dependencies for importing PyQt6.

See GH actions 559 https://github.com/NIRALUser/NeuroRuler/actions/runs/4901894070/jobs/8753416763.
Note test_algorithm was skipped on Ubuntu but passed on Windows.

Therefore, this environment variable checks specifically for whether we're in an Ubuntu GH CI environment
(Windows paths use backslashes)."""


def labeled_result(path) -> float:
    with open(path, "r") as file:
        line = file.readline().strip()
        parts = line.split("\t")
        last_section = parts[-1]
        return float(last_section)


# Source: https://www.askpython.com/python/coefficient-of-determination
def compute_r_squared(actual: list[float], predicted: list[float]) -> float:
    return (np.corrcoef(actual, predicted)[0, 1]) ** 2
