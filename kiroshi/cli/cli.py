"""Module containing the command-line interface for Kiroshi."""

import click
from trogon import tui

from kiroshi.cli.checks.frontdoor import frontdoor as checks_frontdoor
from kiroshi.cli.checks.spreedly import spreedly as checks_spreedly
from kiroshi.cli.kubernetes import linkerd as kubernetes_linkerd
from kiroshi.cli.kubernetes import scale as kubernetes_scale
from kiroshi.cli.server.image import image as server_image
from kiroshi.cli.storage.blob import blob as storage_blob
from kiroshi.cli.storage.sftp import sftp as storage_sftp
from kiroshi.cli.storage.stonegate import stonegate as storage_stonegate


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


@cli.group(name="server")
def server() -> None:
    """Group for Servers."""


@cli.group(name="kubernetes")
def kubernetes() -> None:
    """Group for Kubernetes Commands."""


checks.add_command(checks_frontdoor)
checks.add_command(checks_spreedly)
storage.add_command(storage_blob)
storage.add_command(storage_sftp)
storage.add_command(storage_stonegate)
server.add_command(server_image)
kubernetes.add_command(kubernetes_linkerd)
kubernetes.add_command(kubernetes_scale)


if __name__ == "__main__":
    cli()
