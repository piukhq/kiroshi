"""Mastercard Hacks, now we added file deletion."""
import io
from pathlib import Path

import paramiko
from azure.storage.blob import BlobServiceClient

from kiroshi.storage.hacks.mastercard import _mastercard as hacks_mastercard


def _mastercard_testing(
    sftp_client: paramiko.SFTPClient,
    sftp_path: Path,
    blob_client: BlobServiceClient,
    blob_container: str,
    blob_directory: str,
    filename: str,
    fo: io.BytesIO,
) -> None:
    hacks_mastercard(
        blob_client=blob_client,
        blob_container=blob_container,
        blob_directory=blob_directory,
        filename=filename,
        fo=fo,
    )
    sftp_client.remove(f"{sftp_path}/{filename}")
