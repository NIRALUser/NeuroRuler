"""CLI settings set through arguments.

Default values for some are in the cli_config.json file."""
import NeuroRuler.utils.global_vars as global_vars

DEBUG: bool = False
"""Whether or not to print debugging information throughout execution."""

FILE: str = ""
"""The file."""

THETA_X: int = global_vars.THETA_X
"""In degrees"""
THETA_Y: int = global_vars.THETA_Y
"""In degrees"""
THETA_Z: int = global_vars.THETA_Z
"""In degrees"""
SLICE: int = -1
"""0-indexed. Overwritten later."""

USE_OTSU: bool = True
"""Whether to use a otsu or a binary threshold."""

LOWER_THRESHOLD: float = global_vars.LOWER_THRESHOLD
"""Threshold option for binary threshold."""
UPPER_THRESHOLD: float = global_vars.UPPER_THRESHOLD
"""Threshold option for binary threshold."""
