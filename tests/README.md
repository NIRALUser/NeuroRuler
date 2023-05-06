# README

Unit tests and PyQt6 imports in `test_algorithm.py` and `test_algorithm_unittest.py` are skipped when run in
Ubuntu environments in GitHub Actions CI due to missing dependencies. However, the tests run in Windows environments.

See the docstring of `tests.constants.UBUNTU_GITHUB_ACTIONS_CI` for more information. For convenience, it's reproduced here but could be outdated.

```py
import os

UBUNTU_GITHUB_ACTIONS_CI: bool = os.getenv("HOME") == "/home/runner"
"""Whether the tests are being run in an Ubuntu GitHub Actions CI environment.
Use this to skip PyQt6 imports if in Ubuntu GH Actions CI environment.

Ubuntu environments lack a required ``libEGL.so`` file for PyQt6 imports. This causes an error when importing PyQt6.
However, Windows environments have the required dependencies for importing PyQt6.

See GH actions 559 https://github.com/NIRALUser/NeuroRuler/actions/runs/4901894070/jobs/8753416763.
Note test_algorithm was skipped on Ubuntu but passed on Windows.

Therefore, this environment variable checks specifically for whether we're in an Ubuntu GH CI environment
(Windows paths use backslashes)."""
```
