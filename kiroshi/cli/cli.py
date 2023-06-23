"""Module containing the command-line interface for Kiroshi."""

import click
from trogon import tui

from kiroshi.cli.checks.frontdoor import frontdoor as checks_frontdoor
from kiroshi.cli.checks.spreedly import spreedly as checks_spreedly
from kiroshi.cli.sftp.blobcopy import blobcopy as sftp_blobcopy
from kiroshi.cli.sftp.mastercard import mastercard as sftp_mastercard
from kiroshi.cli.sftp.wasabi import wasabi as sftp_wasabi


@tui()
@click.group()
def cli() -> None:
    """Group for the top-level commands and groups."""


@cli.group(name="checks")
def checks() -> None:
    """Group for Monitoring Tools."""


@cli.group(name="sftp")
def sftp() -> None:
    """Group for SFTP Tools."""


checks.add_command(checks_frontdoor)
checks.add_command(checks_spreedly)
sftp.add_command(sftp_mastercard)
sftp.add_command(sftp_wasabi)
sftp.add_command(sftp_blobcopy)


if __name__ == "__main__":
    cli()
