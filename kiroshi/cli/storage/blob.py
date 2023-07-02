"""Blob command."""

import click

from kiroshi.storage.blob import Blob


@click.command(name="blob")
@click.option(
    "-s",
    "--source",
    help="Source Storage Location, format: <blob|sftp|nfs>:<container_name>:<directory_name>",
)
@click.option(
    "-d",
    "--destination",
    help="Destination Storage Location, format: <blob|sftp|nfs>:<container_name>:<directory_name>",
)
def blob(source: str, destination: str) -> None:
    """Azure Blob Storage Commands."""
    blob = Blob(source=source, destination=destination)
    blob.run()
