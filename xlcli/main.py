"""
main.py
Entry point for xlcli. Delegates everything to the Click CLI defined in cli.py.
"""

from .cli import cli

def main():
    cli()


if __name__ == "__main__":
    main()
