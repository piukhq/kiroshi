"""SFTP Command."""

from pathlib import Path

import click

from kiroshi.storage.sftp import SFTP


@click.command(name="sftp")
@click.option(
    "-h",
    "--host",
    required=True,
    help="SFTP Server Host",
)
@click.option(
    "-p",
    "--port",
    default=22,
    help="SFTP Server Port",
)
@click.option(
    "-u",
    "--user",
    required=True,
    help="SFTP Server User",
)
@click.option(
    "-P",
    "--path",
    required=True,
    help="SFTP Server Path",
)
@click.option(
    "-k",
    "--key",
    required=True,
    help="SFTP Server Key Path",
)
@click.option(
    "-b",
    "--blob_path",
    required=True,
    help="Blob Storage Location, format: <container_name>:<directory_name>",
)
@click.option(
    "-H",
    "--hacks",
    required=False,
    help="Enable Provider Specific Hacks",
    type=click.Choice(["mastercard", "wasabi"]),
)
def sftp(host: str, port: int, user: str, key: Path, path: Path, blob_path: str, hacks: str) -> None:
    """Third-Party SFTP Commands."""
    s = SFTP(
        sftp_host=host,
        sftp_port=port,
        sftp_user=user,
        sftp_key=key,
        sftp_path=path,
        blob_path=blob_path,
        hacks=hacks,
    )
    s.run()
