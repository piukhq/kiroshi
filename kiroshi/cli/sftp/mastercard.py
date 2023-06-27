"""Module providing a command-line interface for connecting to the Mastercard SFTP and pulling files locally."""

import click

from kiroshi.sftp.mastercard import MastercardSFTP


@click.command(name="mastercard")
@click.option(
    "-h",
    "--host",
    default="files.mastercard.com",
    type=click.Choice(
        ["files.mastercard.com", "mtf.files.mastercard.com", "uksouthstagingsftpc75y.blob.core.windows.net"],
    ),
    help="The Mastercard SFTP host to connect to",
)
@click.option(
    "-u",
    "--user",
    default="Z216458",
    type=click.Choice(["Z218502", "Z216458", "Z218502", "uksouthstagingsftpc75y.mastercard.kiroshi"]),
    help="The Mastercard SFTP user to use",
)
@click.option("-p", "--port", default=16022, type=int, help="The Mastercard SFTP port")
@click.option(
    "-k",
    "--keypath",
    default="/tmp/mastercard",  # noqa: S108
    type=str,
    help="The Path to the Mastercard SFTP RSA Key",
)
@click.option(
    "-d",
    "--directories",
    default="/0073185/production/download/TGX2:/mnt/harmonia-imports/mastercard",
    type=click.Choice(
        [
            "/0073185/production/download/TGX2:/mnt/harmonia-imports/mastercard",
            "/0073185/production/download/TS44:/mnt/harmonia-imports/payment/mastercard",
            "/0073185/test/download/TGX4:/mnt/harmonia-imports/test/mastercard-settlement",
        ],
    ),
    help="Map of remote and local directories to use, colon seperated",
)
def mastercard(host: str, user: str, port: int, keypath: str, directories: str) -> None:
    """Connect to the Mastercard SFTP and pull files locally.

    Designed to be used in conjunction with Harmonia.
    """
    sftp = MastercardSFTP(host=host, port=port, user=user, keypath=keypath, directories=directories)
    sftp.run()
