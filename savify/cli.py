"""Console script for Savify."""

import sys
import datetime
import click

from . import __version__, __author__


@click.command()
def main(args=None):
    """Console script for savify."""
    click.echo(f"Savify version {__version__} Copyright (c) 2018-{datetime.datetime.now().year} {__author__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
