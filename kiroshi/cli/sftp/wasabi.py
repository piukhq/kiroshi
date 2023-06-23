"""Module providing a command-line interface for connecting to the Wasabi SFTP and pulling files locally."""

import click

from kiroshi.sftp.wasabi import WasabiSFTP


@click.command(name="wasabi")
@click.option(
    "-h",
    "--host",
    default="sftp.k3btg.com",
    type=click.Choice(["sftp.k3btg.com", "sftp.gb.bink.com"]),
    help="The Wasabi SFTP host to connect to",
)
@click.option(
    "-u",
    "--user",
    default="FTP.bink.132",
    type=click.Choice(["FTP.bink.132", "binktest_dev", "binktest_staging", "binktest_perf"]),
    help="The Wasabi SFTP user to use",
)
@click.option("-p", "--port", default=22, type=int, help="The Wasabi SFTP port")
@click.option(
    "-k",
    "--keypath",
    default="/tmp/wasabi",  # noqa: S108
    type=str,
    help="The Path to the Wasabi SFTP RSA Key",
)
@click.option(
    "-d",
    "--directories",
    default="/upload:/mnt/harmonia-imports/scheme/wasabi",
    type=click.Choice(
        [
            "/upload:/mnt/harmonia-imports/scheme/wasabi",
        ],
    ),
    help="Map of remote and local directories to use, colon seperated",
)
def wasabi(host: str, user: str, port: int, keypath: str, directories: str) -> None:
    """Connect to the Wasabi SFTP and pull files locally.

    Designed to be used in conjunction with Harmonia.
    """
    sftp = WasabiSFTP(host=host, port=port, user=user, keypath=keypath, directories=directories)
    sftp.run()
