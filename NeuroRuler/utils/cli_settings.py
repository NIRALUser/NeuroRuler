"""CLI settings/arguments set through arguments.

Default values for some are in the cli_config.json file."""
DEBUG: bool = False
"""Whether or not to print debugging information throughout execution."""

FILE: str = ""
"""The file."""

THETA_X: int = 0
"""In degrees"""
THETA_Y: int = 0
"""In degrees"""
THETA_Z: int = 0
"""In degrees"""
SLICE: int = -1
"""0-indexed. Overwritten later."""

USE_OTSU: bool = True
"""Whether to use a otsu or a binary threshold."""  # values for binary are in global_vars.py
