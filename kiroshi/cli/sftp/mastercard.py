"""Module providing a command-line interface for connecting to the Mastercard SFTP and pulling files locally."""

from pathlib import Path

import click

from kiroshi.sftp.mastercard import BlobFileWriter, LocalFileWriter, MastercardSFTP


@click.command(name="mastercard")
@click.option(
    "-h",
    "--host",
    default="files.mastercard.com",
    type=click.Choice(
        [
            "files.mastercard.com",
            "mtf.files.mastercard.com",
            "uksouthstagingsftpc75y.blob.core.windows.net",
            "localhost",
        ],
    ),
    help="The Mastercard SFTP host to connect to",
)
@click.option(
    "-u",
    "--user",
    default="Z216458",
    type=click.Choice(["Z218502", "Z216458", "Z218502", "uksouthstagingsftpc75y.mastercard.kiroshi", "foo"]),
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
            "/share:/mnt/harmonia-imports/mastercard",
        ],
    ),
    help="Map of remote and local directories to use, colon seperated",
)
@click.option(
    "--use-blob-storage",
    default=False,
    is_flag=True,
    help="Use Azure Blob Storage to store files instead of writing locally",
)
def mastercard(  # noqa: PLR0913
    host: str,
    user: str,
    port: int,
    keypath: str,
    directories: str,
    use_blob_storage: bool,  # noqa: FBT001
) -> None:
    """Connect to the Mastercard SFTP and pull files locally.

    Designed to be used in conjunction with Harmonia.
    """
    remote_path, local_path = map(Path, directories.split(":"))

    container_name = "harmonia-imports"
    base_path = Path("/mnt") / container_name
    settlement_path = local_path.relative_to(base_path)
    refund_path = settlement_path.parent / "mastercard-refund"

    writer = BlobFileWriter(container_name) if use_blob_storage else LocalFileWriter(base_path)

    sftp = MastercardSFTP(
        host=host,
        port=port,
        user=user,
        keypath=keypath,
        remote_path=remote_path,
        writer=writer,
        settlement_path=settlement_path,
        refund_path=refund_path,
    )
    sftp.run()
