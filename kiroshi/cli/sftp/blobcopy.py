import click

from kiroshi.sftp.blobcopy import BlobCopy


@click.command(name="blobcopy")
@click.option("--sftp-container-name", help="The SFTP Storage Container to use")
@click.option("--sftp-directory-name", default="uploads", show_default=True, help="The directory to Scan for files")
@click.option("--blob-container-name", help="The Blob Storage Container to use")
@click.option("--blob-directory-name", help="The directory to copy blobs to")
def blobcopy(
    sftp_container_name: str, sftp_directory_name: str, blob_container_name: str, blob_directory_name: str
) -> None:
    """
    Copies Blobs from SFTP Storage Accounts to Blob Storage Accounts
    """
    bc = BlobCopy(
        sftp_container_name=sftp_container_name,
        sftp_directory_name=sftp_directory_name,
        blob_container_name=blob_container_name,
        blob_directory_name=blob_directory_name,
    )
    bc.run()
