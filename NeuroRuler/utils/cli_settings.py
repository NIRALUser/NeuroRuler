"""CLI settings set through arguments.

Default values for some are in the cli_config.json file.

The values in this file don't matter since they'll be overwritten by what's in config.json and then by CLI options,
if any. But the values here should match the values in config.json for consistency."""
DEBUG: bool = False
"""Whether or not to print debugging information throughout execution."""

FILE: str = ""
"""The file."""
