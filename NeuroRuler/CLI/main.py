"""
Defines main(), the entrypoint of the CLI (if you want to call it that).
"""


def main() -> None:
    """Main entrypoint of CLI."""
    pass


if __name__ == "__main__":
    import NeuroRuler.utils.parser as parser

    parser.parse_config_json()  # TODO: are these all basically GUI settings? -Eric
    parser.parse_gui_cli()
    main()
