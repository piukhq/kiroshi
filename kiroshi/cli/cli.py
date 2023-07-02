"""Module containing the command-line interface for Kiroshi."""

import click
from trogon import tui

from kiroshi.cli.checks.frontdoor import frontdoor as checks_frontdoor
from kiroshi.cli.checks.spreedly import spreedly as checks_spreedly
from kiroshi.cli.storage.blob import blob as storage_blob
from kiroshi.cli.storage.sftp import sftp as storage_sftp


@tui()
@click.group()
def cli() -> None:
    """Group for the top-level commands and groups."""


@cli.group(name="checks")
def checks() -> None:
    """Group for Monitoring Tools."""


@cli.group(name="storage")
def storage() -> None:
    """Group for SFTP Tools."""


checks.add_command(checks_frontdoor)
checks.add_command(checks_spreedly)
storage.add_command(storage_blob)
storage.add_command(storage_sftp)


if __name__ == "__main__":
    cli()
