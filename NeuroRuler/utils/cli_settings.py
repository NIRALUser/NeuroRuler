"""CLI settings set through command-line arguments and ``cli_config.json``.

Command-line arguments override the values in the JSON."""

from typing import Any
import NeuroRuler.utils.global_vars as global_vars
from NeuroRuler.utils.constants import ThresholdFilter

DEBUG: bool = False
"""Whether or not to print debugging information throughout execution."""

RAW: bool = False
"""Whether to print the \"raw\" circumference.

If false, it prints a \"pretty\", rounded output with units included."""

FILE: str = ""
"""The file path."""

THETA_X: int = global_vars.THETA_X
"""In degrees"""
THETA_Y: int = global_vars.THETA_Y
"""In degrees"""
THETA_Z: int = global_vars.THETA_Z
"""In degrees"""
SLICE: int = -1
"""0-indexed. Overwritten later."""

CONDUCTANCE_PARAMETER: float = global_vars.CONDUCTANCE_PARAMETER
"""Smoothing option. See global_vars.CONDUCTANCE_PARAMETER."""
SMOOTHING_ITERATIONS: int = global_vars.SMOOTHING_ITERATIONS
"""Smoothing option. See global_vars.SMOOTHING_ITERATIONS."""
TIME_STEP: float = global_vars.TIME_STEP
"""Smoothing option. See global_vars.TIME_STEP."""

THRESHOLD_FILTER: ThresholdFilter = ThresholdFilter.Otsu
"""Which threshold filter to use. Default is Otsu."""

LOWER_BINARY_THRESHOLD: float = global_vars.LOWER_BINARY_THRESHOLD
"""Required threshold option for binary threshold.

If ``THRESHOLD_FILTER`` is ``ThresholdFilter.Otsu``, then this field will not be updated by CLI args
or by ``cli_config.json``."""

UPPER_BINARY_THRESHOLD: float = global_vars.UPPER_BINARY_THRESHOLD
"""Required threshold option for binary threshold.

If ``THRESHOLD_FILTER`` is ``ThresholdFilter.Otsu``, then this field will not be updated by CLI args
or by ``cli_config.json``."""


def get_settings() -> dict[str, Any]:
    r"""Returns ``dict`` containing values of all variables in this file, used for debugging

    :return: ``dict`` of all CLI settings
    :rtype: ``dict[str, Any]``"""
    return {
        "DEBUG": DEBUG,
        "RAW": RAW,
        "FILE": FILE,
        "THETA_X": THETA_X,
        "THETA_Y": THETA_Y,
        "THETA_Z": THETA_Z,
        "SLICE": SLICE,
        "CONDUCTANCE_PARAMETER": CONDUCTANCE_PARAMETER,
        "SMOOTHING_ITERATIONS": SMOOTHING_ITERATIONS,
        "TIME_STEP": TIME_STEP,
        "THRESHOLD_FILTER": THRESHOLD_FILTER,
        "LOWER_BINARY_THRESHOLD": LOWER_BINARY_THRESHOLD,
        "UPPER_BINARY_THRESHOLD": UPPER_BINARY_THRESHOLD,
    }
