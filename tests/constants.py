"""Constants used in tests."""

import os
import numpy as np

TARGET_R_SQUARED: float = 0.98
GITHUB_ACTIONS_CI: bool = os.getenv("HOME") == "/home/runner"
"""Whether the tests are being run in a GitHub Actions CI environment or not.

Use this to skip tests in that import PyQt6 dependencies (including NeuroRuler imports that import PyQt6).

The computers running GitHub Actions CI tests will get an error when importing PyQt6
because they don't have a GUI so lack a required ``libEGL.so`` file."""

print(f"GITHUB_ACTIONS_CI: {GITHUB_ACTIONS_CI}")
print(f"os.getenv('HOME'): {os.getenv('HOME')}")


def labeled_result(path) -> float:
    with open(path, "r") as file:
        line = file.readline().strip()
        parts = line.split("\t")
        last_section = parts[-1]
        return float(last_section)


# Source: https://www.askpython.com/python/coefficient-of-determination
def compute_r_squared(actual: list[float], predicted: list[float]) -> float:
    return (np.corrcoef(actual, predicted)[0, 1]) ** 2
